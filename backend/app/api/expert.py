"""
专家评审团生成 API
两步走：1. 意图分析（提炼研讨领域） 2. 生成专家阵容
"""

import traceback
from flask import request, jsonify

from . import expert_bp
from ..config import Config
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger
from ..utils.locale import t

logger = get_logger('mirofish.api.expert')

# ============================================================
# 系统 Prompt 模板
# ============================================================

# Step 1: 意图分析 - 从用户需求中提炼研讨领域
INTENT_ANALYSIS_PROMPT = """\
你是一个资深的项目组局顾问。请分析以下用户的研讨需求，提炼出 3-6 个关键研讨领域/视角。

【用户需求】
{sim_requirement}

【输出要求】
1. 领域应涵盖该需求涉及的各方利益相关方、专业视角、对立观点。
2. 每个领域用一句话说明为什么需要该视角。
3. 返回纯 JSON 格式，不要任何额外文本。

【输出格式】
{{
  "summary": "一句话总结研讨的核心议题",
  "domains": [
    {{"label": "领域名称", "reason": "为什么需要这个视角"}},
    ...
  ]
}}
"""

# Step 2: 生成专家阵容
EXPERT_GENERATION_PROMPT = """\
你是一个顶级的专家邀约专家。请根据以下需求生成一组用于模拟研讨会议的角色阵容。

【研讨需求】
{sim_requirement}

【选定的研讨领域】
{selected_domains}

{existing_experts_hint}

【生成要求】
1. 身份贴合：每个角色的职业、身份、立场必须与研讨主题高度相关。
2. 立场多元：确保组内包含不同利益视角的人物（决策者、执行者、受益者、反对者等）。
3. 背景鲜活：每个人物要有具体的履历、专长、性格特征，避免"模板人"。
4. 风格各异：确保每个人的说话风格不同。
{count_instruction}
5. 语言规范：返回纯 JSON 对象，不要额外文本。

【输出格式】
{{
  "experts": [
    {{
      "name": "角色姓名",
      "identity": "身份标签（如：全国政协委员/经济学派）",
      "domain": "所属研讨领域",
      "background": "简短履历（1-2句话）",
      "mindset": "思维倾向/性格（如：务实谨慎、激进改革派、数据驱动）",
      "focus": ["核心关注点1", "核心关注点2"],
      "stance": "在此次研讨中的基本立场",
      "speaking_style": "说话风格（如：直击要害、引经据典、通俗易懂）"
    }},
    ...
  ]
}}
"""

# ============================================================
# API 接口
# ============================================================


def _get_llm_client(req_data=None):
    """获取 LLM 客户端（支持运行时模型切换）"""
    model_name = Config.LLM_MODEL_NAME
    base_url = Config.LLM_BASE_URL

    if req_data:
        model_name = req_data.get('model_name', model_name)
        base_url = req_data.get('base_url', base_url)

    return LLMClient(
        api_key=Config.LLM_API_KEY,
        base_url=base_url,
        model=model_name
    )


@expert_bp.route('/analyze-intent', methods=['POST'])
def analyze_intent():
    """
    Step 1: 意图分析
    根据模拟提示词，提炼研讨领域
    """
    try:
        data = request.get_json() or {}
        sim_requirement = data.get('sim_requirement', '')

        if not sim_requirement:
            return jsonify({
                "success": False,
                "error": "请提供模拟提示词"
            }), 400

        client = _get_llm_client(data)
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的研讨组局顾问。只返回JSON，不要多余的话。"
            },
            {
                "role": "user",
                "content": INTENT_ANALYSIS_PROMPT.format(
                    sim_requirement=sim_requirement
                )
            }
        ]

        result = client.chat_json(messages, temperature=0.7, max_tokens=2048)

        logger.info(f"意图分析成功: {result.get('summary', '')[:50]}...")

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        logger.error(f"意图分析失败: {e}\n{traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@expert_bp.route('/generate-experts', methods=['POST'])
def generate_experts():
    """
    Step 2: 生成专家阵容
    根据选定领域生成具体专家
    支持增量模式（在现有专家基础上追加）
    """
    try:
        data = request.get_json() or {}
        sim_requirement = data.get('sim_requirement', '')
        selected_domains = data.get('selected_domains', [])
        existing_experts = data.get('existing_experts', [])
        additional_request = data.get('additional_request', '')
        target_count = data.get('count', 10)

        if not sim_requirement:
            return jsonify({
                "success": False,
                "error": "请提供模拟提示词"
            }), 400

        # 构建领域描述
        domain_text = ""
        for i, d in enumerate(selected_domains, 1):
            label = d.get('label', '') if isinstance(d, dict) else str(d)
            reason = d.get('reason', '') if isinstance(d, dict) else ''
            domain_text += f"{i}. {label}（{reason}）\n"

        # 已有专家提示（增量模式）
        existing_hint = ""
        if existing_experts:
            existing_hint = "【已有专家阵容】\n当前已有以下专家：\n"
            for i, e in enumerate(existing_experts, 1):
                existing_hint += f"{i}. {e.get('name', '')} - {e.get('identity', '')}（{e.get('domain', '')}）\n"
            # 明确告知 LLM 只生成新增角色，且返回列表必须为纯新增（不包含任何已有角色）
            existing_hint += "\n【重要】你只需输出需要新增的角色，不要包含以上已有角色。返回的 experts 数组仅包含新增角色。"
            existing_hint += "\n【禁止】绝对不要返回以上已有专家阵容中的任何一个人。必须创造全新的、不同姓名的新专家。"

        # 数量指令
        count_instruction = ""
        if existing_experts and not additional_request:
            new_count = max(target_count - len(existing_experts), 1)
            count_instruction = f"4. 数量：仅生成 {new_count} 位与已有专家不同的新专家。"
        elif not existing_experts:
            count_instruction = f"4. 数量：生成 {target_count} 位专家。"
        else:
            new_count = max(target_count - len(existing_experts), 1)
            count_instruction = f"4. 数量：仅生成 {new_count} 位与已有专家不同的新专家，需考虑：{additional_request}。"

        client = _get_llm_client(data)
        messages = [
            {
                "role": "system",
                "content": "你是专家组局专家。只返回JSON，不要多余的话。"
            },
            {
                "role": "user",
                "content": EXPERT_GENERATION_PROMPT.format(
                    sim_requirement=sim_requirement,
                    selected_domains=domain_text,
                    existing_experts_hint=existing_hint,
                    count_instruction=count_instruction
                )
            }
        ]

        result = client.chat_json(messages, temperature=0.8, max_tokens=4096)

        experts = result.get('experts', [])
        logger.info(f"生成专家阵容: {len(experts)} 人")

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:
        logger.error(f"生成专家阵容失败: {e}\n{traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
