"""
修身相关API路由
Step 2: AI亮底牌 - 基于基础事实推测部分数据
Step 3: AI深猜 - 基于前两步数据推测全部~70项
"""

import json
import re
import traceback
from flask import request, jsonify

from . import cultivation_bp
from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger('mirofish.api.cultivation')

# MBTI 16型
MBTI_TYPES = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']

# 星座
ZODIAC_SIGNS = [
    ('摩羯座', (1, 1), (1, 19)),
    ('水瓶座', (1, 20), (2, 18)),
    ('双鱼座', (2, 19), (3, 20)),
    ('白羊座', (3, 21), (4, 19)),
    ('金牛座', (4, 20), (5, 20)),
    ('双子座', (5, 21), (6, 21)),
    ('巨蟹座', (6, 22), (7, 22)),
    ('狮子座', (7, 23), (8, 22)),
    ('处女座', (8, 23), (9, 22)),
    ('天秤座', (9, 23), (10, 23)),
    ('天蝎座', (10, 24), (11, 22)),
    ('射手座', (11, 23), (12, 21)),
    ('摩羯座', (12, 22), (12, 31)),
]


def get_zodiac(birth_date_str):
    """根据出生日期计算星座"""
    try:
        from datetime import datetime
        d = datetime.strptime(birth_date_str, '%Y-%m-%d')
        m, day = d.month, d.day
        for name, (sm, sd), (em, ed) in ZODIAC_SIGNS:
            if (m == sm and day >= sd) or (m == em and day <= ed):
                return name
    except Exception:
        pass
    return '未知'


def get_age(birth_date_str):
    """根据出生日期计算年龄"""
    try:
        from datetime import datetime
        d = datetime.strptime(birth_date_str, '%Y-%m-%d')
        now = datetime.now()
        return now.year - d.year - ((now.month, now.day) < (d.month, d.day))
    except Exception:
        return 30


@cultivation_bp.route('/guess-step2', methods=['POST'])
def guess_step2():
    """
    Step 2: AI亮底牌
    基于基础事实推测 MBTI、大五人格、昼夜节律、身体健康、心理能量、决策风格、人际互动
    """
    try:
        data = request.get_json()
        birth_date = data.get('birthDate', '')
        blood_type = data.get('bloodType', '')
        gender = data.get('gender', '')
        birthplace = data.get('birthplace', '')
        education = data.get('education', '')
        occupation = data.get('occupation', '')
        marital_status = data.get('maritalStatus', '')
        children_count = data.get('childrenCount', 0)
        income_range = data.get('incomeRange', '')

        zodiac = get_zodiac(birth_date)
        age = get_age(birth_date)

        # 构建 prompt
        prompt = f"""你是一位资深心理学专家，请根据以下用户基础信息，推测其心理特征。

用户信息：
- 出生日期：{birth_date}（{zodiac}）
- 血型：{blood_type}
- 性别：{gender}
- 出生地：{birthplace}
- 最高学历：{education}
- 当前职业：{occupation}
- 婚姻状况：{marital_status}
- 子女数量：{children_count}
- 月收入范围：{income_range}

请严格按以下 JSON 格式返回推测结果（不要包含其他文字）：

{{
  "zodiac": "{zodiac}",
  "mbti": {{
    "options": [
      {{"type": "XXXX", "p": 0.XX, "reason": "简短推理"}},
      {{"type": "XXXX", "p": 0.XX, "reason": "简短推理"}},
      {{"type": "XXXX", "p": 0.XX, "reason": "简短推理"}}
    ],
    "reasoning": ["推理依据1", "推理依据2", "推理依据3"]
  }},
  "bigFive": {{"value": "描述", "confidence": 0.X}},
  "chronotype": {{"value": "晨型(云雀)/夜型(猫头鹰)/中间型/不规律型", "confidence": 0.X}},
  "healthBaseline": {{"value": "描述", "confidence": 0.3, "aiNote": "AI无法准确推测，基于年龄职业的参考"}},
  "mentalEnergy": {{"value": "描述", "confidence": 0.3, "aiNote": "AI无法准确推测，基于年龄职业的参考"}},
  "decisionStyle": {{"value": "理性分析型/直觉冲动型/谨慎犹豫型/从众依赖型/独立果断型/回避拖延型", "confidence": 0.X}},
  "interactionPattern": {{"value": "安全型依恋/焦虑型依恋/回避型依恋/混乱型依恋/外向社交型/内向独立型/选择性社交", "confidence": 0.X}}
}}

注意：
1. MBTI 选项概率之和应为 1.0
2. 大五人格用简短描述（如"高开放性、中等尽责性"）
3. confidence 范围 0.1-0.9
4. 身体健康和心理能量的 confidence 应较低（0.2-0.4），因为AI确实猜不准
"""

        llm = LLMClient()
        response = llm.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2048
        )

        # 解析 JSON
        result = _parse_json_response(response)
        if not result:
            result = _get_default_step2_result(zodiac, age, occupation)

        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Step2 推测失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": _get_default_step2_result('', 30, '')
        })


@cultivation_bp.route('/guess-step3', methods=['POST'])
def guess_step3():
    """
    Step 3: AI深猜
    基于前两步数据推测全部~70项，按5大类组织
    """
    try:
        data = request.get_json()
        step1 = data.get('step1', {})
        step2 = data.get('step2', {})

        birth_date = step1.get('birthDate', '')
        zodiac = step1.get('zodiac', get_zodiac(birth_date))
        age = get_age(birth_date)
        blood_type = step1.get('bloodType', '')
        gender = step1.get('gender', '')
        education = step1.get('education', '')
        occupation = step1.get('occupation', '')
        marital_status = step1.get('maritalStatus', '')
        income_range = step1.get('incomeRange', '')
        mbti = step2.get('mbti', 'ISTJ')
        big_five = step2.get('bigFive', '')
        chronotype = step2.get('chronotype', '')
        decision_style = step2.get('decisionStyle', '')
        interaction_pattern = step2.get('interactionPattern', '')

        prompt = f"""你是一位资深心理学和人生分析专家，请根据以下用户信息，对其人生5大维度进行深度分析和推测。

用户基础信息：
- 出生日期：{birth_date}（{zodiac}，{age}岁）
- 血型：{blood_type} | 性别：{gender}
- 学历：{education} | 职业：{occupation}
- 婚姻：{marital_status} | 收入：{income_range}

AI初步推测：
- MBTI：{mbti}
- 大五人格：{big_five}
- 昼夜节律：{chronotype}
- 决策风格：{decision_style}
- 人际互动：{interaction_pattern}

请严格按以下 JSON 格式返回推测结果。每个项目必须包含 label（标签）、value（推测值）、confidence（置信度0.1-0.9）、options（可选值数组，3-6个选项）。

{{
  "categories": [
    {{
      "id": "life-foundation",
      "name": "生命根基",
      "icon": "🌱",
      "items": [
        {{"id": "family-structure", "label": "原生家庭结构", "value": "...", "confidence": 0.X, "options": ["选项1", "选项2", "选项3"]}},
        {{"id": "family-economy", "label": "家庭经济状况", "value": "...", "confidence": 0.X, "options": ["选项1", "选项2", "选项3", "选项4"]}},
        {{"id": "family-education", "label": "家庭教育风格", "value": "...", "confidence": 0.X, "options": ["专制型", "民主型", "放任型", "忽视型"]}},
        {{"id": "family-culture", "label": "家族文化传承", "value": "...", "confidence": 0.X, "options": ["重视教育", "重视经商", "重视手艺", "无明显传承"]}},
        {{"id": "family-events", "label": "重要家庭变故", "value": "...", "confidence": 0.X, "options": ["父母离异", "亲人去世", "家庭搬迁", "移民", "无明显变故"]}},
        {{"id": "growth-region", "label": "成长地域轨迹", "value": "...", "confidence": 0.X, "options": ["农村成长", "小城镇", "城市成长", "多地迁徙"]}},
        {{"id": "education-path", "label": "教育塑造历程", "value": "...", "confidence": 0.X, "options": ["初中", "高中", "大专", "本科", "硕士", "博士"]}},
        {{"id": "early-events", "label": "早期重大事件", "value": "...", "confidence": 0.X, "options": ["无显著事件", "童年创伤", "关键转折", "荣誉成就", "失去经历"]}},
        {{"id": "generational", "label": "代际传承印记", "value": "...", "confidence": 0.X, "options": ["家族职业传承", "家风家训", "代际创伤", "资源继承", "无明显传承"]}},
        {{"id": "cultural-adapt", "label": "文化适应经历", "value": "...", "confidence": 0.X, "options": ["无显著适应", "城乡文化适应", "地域文化适应", "跨文化适应"]}}
      ]
    }},
    {{
      "id": "social-existence",
      "name": "社会存在",
      "icon": "🏛️",
      "items": [
        {{"id": "career-identity", "label": "职业身份定位", "value": "...", "confidence": 0.X, "options": []}},
        {{"id": "economic-resource", "label": "经济资源状况", "value": "...", "confidence": 0.X, "options": []}},
        {{"id": "social-network", "label": "社会关系网络", "value": "...", "confidence": 0.X, "options": ["广泛", "中等规模", "较小", "极小"]}},
        {{"id": "class-perception", "label": "社会阶层感知", "value": "...", "confidence": 0.X, "options": ["底层", "工薪", "中产", "上层"]}},
        {{"id": "public-participation", "label": "公共参与程度", "value": "...", "confidence": 0.X, "options": ["高", "中", "低", "无"]}},
        {{"id": "career-satisfaction", "label": "职业满意度", "value": "...", "confidence": 0.X, "options": ["非常满意", "比较满意", "中等", "不太满意", "很不满意"]}},
        {{"id": "career-relations", "label": "职业人际关系", "value": "...", "confidence": 0.X, "options": ["非常紧张", "有些紧张", "一般", "良好", "非常好"]}},
        {{"id": "career-plan", "label": "职业发展规划", "value": "...", "confidence": 0.X, "options": ["晋升", "转行", "创业", "维持现状", "不确定"]}},
        {{"id": "social-support", "label": "社会支持度", "value": "...", "confidence": 0.X, "options": ["强", "中等", "弱"]}},
        {{"id": "class-mobility", "label": "阶层流动经历", "value": "...", "confidence": 0.X, "options": ["向上流动", "向下流动", "稳定", "波动"]}}
      ]
    }},
    {{
      "id": "physical-mental",
      "name": "身心状态",
      "icon": "💪",
      "items": [
        {{"id": "personality", "label": "性格特质", "value": "{mbti}", "confidence": 0.X, "options": ["INTJ","INTP","ENTJ","ENTP","INFJ","INFP","ENFJ","ENFP","ISTJ","ISFJ","ESTJ","ESFJ","ISTP","ISFP","ESTP","ESFP"]}},
        {{"id": "physical-health", "label": "身体健康基线", "value": "...", "confidence": 0.X, "options": ["非常健康", "基本健康", "亚健康", "有慢性疾病", "正在恢复中"]}},
        {{"id": "mental-energy", "label": "心理能量水平", "value": "...", "confidence": 0.X, "options": ["精力充沛", "状态良好", "中等水平", "容易疲劳", "长期倦怠"]}},
        {{"id": "energy-rhythm", "label": "精力管理节律", "value": "...", "confidence": 0.X, "options": ["晨型(云雀)", "夜型(猫头鹰)", "中间型", "不规律型"]}},
        {{"id": "body-mind", "label": "身心连接状态", "value": "...", "confidence": 0.X, "options": ["非常协调", "基本协调", "偶尔失调", "经常失调"]}},
        {{"id": "emotional-stability", "label": "情绪稳定性", "value": "...", "confidence": 0.X, "options": ["非常稳定", "比较稳定", "中等", "不太稳定", "很不稳定"]}},
        {{"id": "stress-level", "label": "压力水平", "value": "...", "confidence": 0.X, "options": ["无压力", "轻度", "中度", "重度", "极重度"]}},
        {{"id": "resilience", "label": "心理韧性", "value": "...", "confidence": 0.X, "options": ["非常强", "比较强", "中等", "比较弱", "非常弱"]}},
        {{"id": "sleep-quality", "label": "睡眠质量", "value": "...", "confidence": 0.X, "options": ["非常好", "比较好", "一般", "比较差", "非常差"]}},
        {{"id": "diet-pattern", "label": "饮食模式", "value": "...", "confidence": 0.X, "options": ["规律三餐", "偶尔不规律", "经常不规律", "节食", "暴饮暴食"]}}
      ]
    }},
    {{
      "id": "spiritual-world",
      "name": "精神世界",
      "icon": "🌟",
      "items": [
        {{"id": "core-values", "label": "核心价值观排序", "value": "...", "confidence": 0.X, "options": []}},
        {{"id": "life-meaning", "label": "人生意义感来源", "value": "...", "confidence": 0.X, "options": ["工作", "家庭", "信仰", "创造", "服务", "体验"]}},
        {{"id": "knowledge-interest", "label": "知识兴趣地图", "value": "...", "confidence": 0.X, "options": ["文史", "科技", "哲学", "艺术", "体育", "其他"]}},
        {{"id": "aesthetic", "label": "审美与创造表达", "value": "...", "confidence": 0.X, "options": ["音乐", "绘画", "写作", "手工", "摄影", "无明显偏好"]}},
        {{"id": "belief", "label": "信念与精神寄托", "value": "...", "confidence": 0.X, "options": ["佛教", "基督教", "伊斯兰教", "道教", "无宗教信仰", "其他"]}},
        {{"id": "reading-pref", "label": "阅读偏好", "value": "...", "confidence": 0.X, "options": ["文学小说", "非虚构类", "科技类", "哲学类", "不常阅读"]}},
        {{"id": "creative-tendency", "label": "创作倾向", "value": "...", "confidence": 0.X, "options": ["经常创作", "偶尔创作", "有想法不实践", "无创作欲望"]}},
        {{"id": "spiritual-practice", "label": "精神实践", "value": "...", "confidence": 0.X, "options": ["冥想", "瑜伽", "祈祷", "阅读", "无"]}},
        {{"id": "life-philosophy", "label": "人生哲学", "value": "...", "confidence": 0.X, "options": []}},
        {{"id": "death-view", "label": "生死观", "value": "...", "confidence": 0.X, "options": []}}
      ]
    }},
    {{
      "id": "behavior-pattern",
      "name": "行为模式",
      "icon": "⚡",
      "items": [
        {{"id": "decision-style", "label": "决策风格", "value": "{decision_style}", "confidence": 0.X, "options": ["理性分析型", "直觉冲动型", "谨慎犹豫型", "从众依赖型", "独立果断型", "回避拖延型"]}},
        {{"id": "interaction-mode", "label": "人际互动模式", "value": "{interaction_pattern}", "confidence": 0.X, "options": ["安全型依恋", "焦虑型依恋", "回避型依恋", "混乱型依恋", "外向社交型", "内向独立型", "选择性社交"]}},
        {{"id": "time-management", "label": "时间管理特征", "value": "...", "confidence": 0.X, "options": ["严格计划", "有计划", "随性", "经常拖延"]}},
        {{"id": "stress-response", "label": "应对压力策略", "value": "...", "confidence": 0.X, "options": ["积极应对", "寻求帮助", "逃避", "情绪化", "物质依赖"]}},
        {{"id": "growth-pattern", "label": "成长与改变模式", "value": "...", "confidence": 0.X, "options": ["快速成长", "稳步成长", "停滞", "倒退"]}},
        {{"id": "learning-agility", "label": "学习敏捷性", "value": "...", "confidence": 0.X, "options": ["非常敏捷", "比较敏捷", "中等", "不太敏捷"]}},
        {{"id": "comfort-zone", "label": "舒适区边界", "value": "...", "confidence": 0.X, "options": ["愿意突破", "中等", "比较保守", "非常保守"]}},
        {{"id": "change-willingness", "label": "改变意愿", "value": "...", "confidence": 0.X, "options": ["非常愿意", "比较愿意", "中等", "不太愿意", "抗拒"]}},
        {{"id": "self-reflection", "label": "自我反思习惯", "value": "...", "confidence": 0.X, "options": ["经常反思", "偶尔反思", "很少反思", "从不反思"]}},
        {{"id": "habit-formation", "label": "习惯养成能力", "value": "...", "confidence": 0.X, "options": ["非常强", "比较强", "中等", "比较弱"]}}
      ]
    }}
  ]
}}

注意：
1. 每个 item 的 options 数组必须包含 3-6 个选项（可以是空数组表示自由填写）
2. confidence 范围 0.1-0.9，AI 不确定的项给低置信度
3. 职业相关的项（职业身份、经济资源）confidence 应较高
4. 只返回 JSON，不要其他文字
"""

        llm = LLMClient()
        response = llm.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=4096
        )

        result = _parse_json_response(response)
        if not result or 'categories' not in result:
            result = _get_default_step3_result(mbti, chronotype, decision_style, interaction_pattern)

        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error(f"Step3 推测失败: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": _get_default_step3_result('ISTJ', '中间型', '理性分析型', '安全型依恋')
        })


def _parse_json_response(response):
    """从 LLM 响应中解析 JSON"""
    try:
        # 尝试直接解析
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    try:
        # 尝试提取 JSON 块
        match = re.search(r'\{[\s\S]*\}', response)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, AttributeError):
        pass

    logger.warning(f"无法解析 LLM 响应: {response[:200]}...")
    return None


def _get_default_step2_result(zodiac, age, occupation):
    """Step2 降级默认值"""
    return {
        "zodiac": zodiac or "未知",
        "mbti": {
            "options": [
                {"type": "ISTJ", "p": 0.35, "reason": "基于统计分布"},
                {"type": "INTJ", "p": 0.28, "reason": "职业特征分析"},
                {"type": "ISFJ", "p": 0.20, "reason": "血型性格关联"}
            ],
            "reasoning": ["基于星座和血型统计分布", "职业特征分析", "教育背景推断"]
        },
        "bigFive": {"value": "均衡型", "confidence": 0.5},
        "chronotype": {"value": "中间型", "confidence": 0.4},
        "healthBaseline": {"value": "基本健康", "confidence": 0.3, "aiNote": "AI无法准确推测，基于年龄职业的参考"},
        "mentalEnergy": {"value": "中等水平", "confidence": 0.3, "aiNote": "AI无法准确推测，基于年龄职业的参考"},
        "decisionStyle": {"value": "理性分析型", "confidence": 0.55},
        "interactionPattern": {"value": "安全型依恋", "confidence": 0.45}
    }


def _get_default_step3_result(mbti, chronotype, decision_style, interaction_pattern):
    """Step3 降级默认值"""
    return {
        "categories": [
            {
                "id": "life-foundation", "name": "生命根基", "icon": "🌱",
                "items": [
                    {"id": "family-structure", "label": "原生家庭结构", "value": "双亲家庭", "confidence": 0.7, "options": ["单亲家庭", "双亲家庭", "隔代抚养", "重组家庭", "其他"]},
                    {"id": "family-economy", "label": "家庭经济状况", "value": "工薪阶层", "confidence": 0.6, "options": ["贫困", "工薪阶层", "中产", "富裕"]},
                    {"id": "family-education", "label": "家庭教育风格", "value": "民主型", "confidence": 0.5, "options": ["专制型", "民主型", "放任型", "忽视型"]},
                    {"id": "family-culture", "label": "家族文化传承", "value": "重视教育", "confidence": 0.5, "options": ["重视教育", "重视经商", "重视手艺", "无明显传承"]},
                    {"id": "family-events", "label": "重要家庭变故", "value": "无明显变故", "confidence": 0.4, "options": ["父母离异", "亲人去世", "家庭搬迁", "移民", "无明显变故"]},
                    {"id": "growth-region", "label": "成长地域轨迹", "value": "城市成长", "confidence": 0.6, "options": ["农村成长", "小城镇", "城市成长", "多地迁徙"]},
                    {"id": "education-path", "label": "教育塑造历程", "value": "本科", "confidence": 0.8, "options": ["初中", "高中", "大专", "本科", "硕士", "博士"]},
                    {"id": "early-events", "label": "早期重大事件", "value": "无明显事件", "confidence": 0.3, "options": ["无显著事件", "童年创伤", "关键转折", "荣誉成就", "失去经历"]},
                    {"id": "generational", "label": "代际传承印记", "value": "无明显传承", "confidence": 0.3, "options": ["家族职业传承", "家风家训", "代际创伤", "资源继承", "无明显传承"]},
                    {"id": "cultural-adapt", "label": "文化适应经历", "value": "无显著适应", "confidence": 0.4, "options": ["无显著适应", "城乡文化适应", "地域文化适应", "跨文化适应"]}
                ]
            },
            {
                "id": "social-existence", "name": "社会存在", "icon": "🏛️",
                "items": [
                    {"id": "career-identity", "label": "职业身份定位", "value": "专业人士", "confidence": 0.8, "options": []},
                    {"id": "economic-resource", "label": "经济资源状况", "value": "中等收入", "confidence": 0.7, "options": []},
                    {"id": "social-network", "label": "社会关系网络", "value": "中等规模", "confidence": 0.4, "options": ["广泛", "中等规模", "较小", "极小"]},
                    {"id": "class-perception", "label": "社会阶层感知", "value": "中产", "confidence": 0.5, "options": ["底层", "工薪", "中产", "上层"]},
                    {"id": "public-participation", "label": "公共参与程度", "value": "低", "confidence": 0.4, "options": ["高", "中", "低", "无"]},
                    {"id": "career-satisfaction", "label": "职业满意度", "value": "中等", "confidence": 0.4, "options": ["非常满意", "比较满意", "中等", "不太满意", "很不满意"]},
                    {"id": "career-relations", "label": "职业人际关系", "value": "良好", "confidence": 0.5, "options": ["非常紧张", "有些紧张", "一般", "良好", "非常好"]},
                    {"id": "career-plan", "label": "职业发展规划", "value": "稳步发展", "confidence": 0.4, "options": ["晋升", "转行", "创业", "维持现状", "不确定"]},
                    {"id": "social-support", "label": "社会支持度", "value": "中等", "confidence": 0.4, "options": ["强", "中等", "弱"]},
                    {"id": "class-mobility", "label": "阶层流动经历", "value": "向上流动", "confidence": 0.4, "options": ["向上流动", "向下流动", "稳定", "波动"]}
                ]
            },
            {
                "id": "physical-mental", "name": "身心状态", "icon": "💪",
                "items": [
                    {"id": "personality", "label": "性格特质", "value": mbti, "confidence": 0.5, "options": MBTI_TYPES},
                    {"id": "physical-health", "label": "身体健康基线", "value": "基本健康", "confidence": 0.3, "options": ["非常健康", "基本健康", "亚健康", "有慢性疾病", "正在恢复中"]},
                    {"id": "mental-energy", "label": "心理能量水平", "value": "中等水平", "confidence": 0.3, "options": ["精力充沛", "状态良好", "中等水平", "容易疲劳", "长期倦怠"]},
                    {"id": "energy-rhythm", "label": "精力管理节律", "value": chronotype or "中间型", "confidence": 0.4, "options": ["晨型(云雀)", "夜型(猫头鹰)", "中间型", "不规律型"]},
                    {"id": "body-mind", "label": "身心连接状态", "value": "基本协调", "confidence": 0.3, "options": ["非常协调", "基本协调", "偶尔失调", "经常失调"]},
                    {"id": "emotional-stability", "label": "情绪稳定性", "value": "中等", "confidence": 0.4, "options": ["非常稳定", "比较稳定", "中等", "不太稳定", "很不稳定"]},
                    {"id": "stress-level", "label": "压力水平", "value": "中等", "confidence": 0.4, "options": ["无压力", "轻度", "中度", "重度", "极重度"]},
                    {"id": "resilience", "label": "心理韧性", "value": "中等", "confidence": 0.4, "options": ["非常强", "比较强", "中等", "比较弱", "非常弱"]},
                    {"id": "sleep-quality", "label": "睡眠质量", "value": "一般", "confidence": 0.4, "options": ["非常好", "比较好", "一般", "比较差", "非常差"]},
                    {"id": "diet-pattern", "label": "饮食模式", "value": "规律三餐", "confidence": 0.4, "options": ["规律三餐", "偶尔不规律", "经常不规律", "节食", "暴饮暴食"]}
                ]
            },
            {
                "id": "spiritual-world", "name": "精神世界", "icon": "🌟",
                "items": [
                    {"id": "core-values", "label": "核心价值观排序", "value": "成就>关系>自由", "confidence": 0.4, "options": []},
                    {"id": "life-meaning", "label": "人生意义感来源", "value": "工作", "confidence": 0.4, "options": ["工作", "家庭", "信仰", "创造", "服务", "体验"]},
                    {"id": "knowledge-interest", "label": "知识兴趣地图", "value": "科技", "confidence": 0.5, "options": ["文史", "科技", "哲学", "艺术", "体育", "其他"]},
                    {"id": "aesthetic", "label": "审美与创造表达", "value": "无明显偏好", "confidence": 0.3, "options": ["音乐", "绘画", "写作", "手工", "摄影", "无明显偏好"]},
                    {"id": "belief", "label": "信念与精神寄托", "value": "无宗教信仰", "confidence": 0.4, "options": ["佛教", "基督教", "伊斯兰教", "道教", "无宗教信仰", "其他"]},
                    {"id": "reading-pref", "label": "阅读偏好", "value": "非虚构类", "confidence": 0.4, "options": ["文学小说", "非虚构类", "科技类", "哲学类", "不常阅读"]},
                    {"id": "creative-tendency", "label": "创作倾向", "value": "偶尔", "confidence": 0.3, "options": ["经常创作", "偶尔创作", "有想法不实践", "无创作欲望"]},
                    {"id": "spiritual-practice", "label": "精神实践", "value": "无", "confidence": 0.3, "options": ["冥想", "瑜伽", "祈祷", "阅读", "无"]},
                    {"id": "life-philosophy", "label": "人生哲学", "value": "务实主义", "confidence": 0.3, "options": []},
                    {"id": "death-view", "label": "生死观", "value": "顺其自然", "confidence": 0.3, "options": []}
                ]
            },
            {
                "id": "behavior-pattern", "name": "行为模式", "icon": "⚡",
                "items": [
                    {"id": "decision-style", "label": "决策风格", "value": decision_style or "理性分析型", "confidence": 0.55, "options": ["理性分析型", "直觉冲动型", "谨慎犹豫型", "从众依赖型", "独立果断型", "回避拖延型"]},
                    {"id": "interaction-mode", "label": "人际互动模式", "value": interaction_pattern or "安全型依恋", "confidence": 0.45, "options": ["安全型依恋", "焦虑型依恋", "回避型依恋", "混乱型依恋", "外向社交型", "内向独立型", "选择性社交"]},
                    {"id": "time-management", "label": "时间管理特征", "value": "有计划", "confidence": 0.4, "options": ["严格计划", "有计划", "随性", "经常拖延"]},
                    {"id": "stress-response", "label": "应对压力策略", "value": "积极应对", "confidence": 0.4, "options": ["积极应对", "寻求帮助", "逃避", "情绪化", "物质依赖"]},
                    {"id": "growth-pattern", "label": "成长与改变模式", "value": "稳步成长", "confidence": 0.4, "options": ["快速成长", "稳步成长", "停滞", "倒退"]},
                    {"id": "learning-agility", "label": "学习敏捷性", "value": "中等", "confidence": 0.5, "options": ["非常敏捷", "比较敏捷", "中等", "不太敏捷"]},
                    {"id": "comfort-zone", "label": "舒适区边界", "value": "中等", "confidence": 0.4, "options": ["愿意突破", "中等", "比较保守", "非常保守"]},
                    {"id": "change-willingness", "label": "改变意愿", "value": "中等", "confidence": 0.4, "options": ["非常愿意", "比较愿意", "中等", "不太愿意", "抗拒"]},
                    {"id": "self-reflection", "label": "自我反思习惯", "value": "偶尔", "confidence": 0.4, "options": ["经常反思", "偶尔反思", "很少反思", "从不反思"]},
                    {"id": "habit-formation", "label": "习惯养成能力", "value": "中等", "confidence": 0.4, "options": ["非常强", "比较强", "中等", "比较弱"]}
                ]
            }
        ]
    }
