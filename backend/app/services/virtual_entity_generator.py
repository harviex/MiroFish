"""
虚拟实体生成器
使用LLM根据本体定义和模拟需求生成虚拟人物实体（如50位不同领域的政协委员）
替代从Zep图谱抽取实体的方式，适用于需要创造虚构人物的场景
"""

import json
import time
import random
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from openai import OpenAI

from ..config import Config
from ..utils.logger import get_logger

logger = get_logger('mirofish.virtual_entity')

@dataclass
class VirtualEntityNode:
    """虚拟实体节点数据结构（兼容EntityNode接口）"""
    uuid: str
    name: str
    labels: List[str]
    summary: str
    attributes: Dict[str, Any]
    related_edges: List[Dict[str, Any]] = field(default_factory=list)
    related_nodes: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'uuid': self.uuid,
            'name': self.name,
            'labels': self.labels,
            'summary': self.summary,
            'attributes': self.attributes,
            'related_edges': self.related_edges,
            'related_nodes': self.related_nodes,
        }
    
    def get_entity_type(self) -> Optional[str]:
        """获取实体类型（排除默认的Entity标签）"""
        for label in self.labels:
            if label not in ['Entity', 'Node']:
                return label
        return None


class VirtualEntityGenerator:
    """
    虚拟实体生成器
    
    核心功能：
    1. 解析本体定义中的实体类型
    2. 用LLM批量生成指定数量的虚拟人物实体
    3. 确保人物覆盖指定领域、类型多元化
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
    ):
        self.api_key = api_key or Config.LLM_API_KEY
        self.base_url = base_url or Config.LLM_BASE_URL
        self.model_name = model_name or Config.LLM_MODEL_NAME
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=300.0,
        )
    
    def generate_virtual_entities(
        self,
        entity_types: List[str],
        relation_types: List[str],
        requirement: str,
        target_count: int,
        document_text: str = "",
        progress_callback: Optional[callable] = None,
    ) -> List[VirtualEntityNode]:
        """
        使用LLM生成虚拟人物实体
        
        Args:
            entity_types: 本体定义的实体类型列表（如 MemberOfCPPCC, GovernmentOfficial）
            relation_types: 本体定义的关系类型列表
            requirement: 模拟需求描述
            target_count: 目标生成数量
            document_text: 参考文档内容（可选）
            progress_callback: 进度回调 (stage, progress, message)
            
        Returns:
            虚拟实体列表
        """
        if progress_callback:
            progress_callback("generating_virtual_entities", 0, f"开始生成 {target_count} 个虚拟实体...")
        
        entities = []
        max_per_batch = 10  # 每批最多生成10个，避免JSON过大
        remaining = target_count
        
        batch_num = 0
        
        while remaining > 0:
            batch_num += 1
            batch_size = min(max_per_batch, remaining)
            start_id = len(entities) + 1
            
            if progress_callback:
                progress_callback(
                    "generating_virtual_entities",
                    int((target_count - remaining) / target_count * 100),
                    f"第 {batch_num} 批: 生成 {batch_size} 个实体（#{start_id}-#{start_id+batch_size-1}）"
                )
            
            batch_entities = self._generate_entity_batch(
                entity_types=entity_types,
                relation_types=relation_types,
                requirement=requirement,
                batch_size=batch_size,
                start_index=start_id,
                document_text=document_text,
            )
            
            entities.extend(batch_entities)
            remaining -= len(batch_entities)
            
            logger.info(f"批次 {batch_num}: 生成 {len(batch_entities)} 个实体，剩余 {remaining}")
            
            if len(batch_entities) == 0:
                logger.warning("LLM未返回任何实体，使用规则生成兜底")
                break
        
        if progress_callback:
            progress_callback(
                "generating_virtual_entities",
                100,
                f"完成，共生成 {len(entities)} 个虚拟实体"
            )
        
        return entities
    
    def _generate_entity_batch(
        self,
        entity_types: List[str],
        relation_types: List[str],
        requirement: str,
        batch_size: int,
        start_index: int,
        document_text: str = "",
        max_retries: int = 3,
    ) -> List[VirtualEntityNode]:
        """生成一批虚拟实体"""
        entity_types_str = ", ".join(entity_types)
        relation_types_str = ", ".join(relation_types) if relation_types else "无"
        doc_preview = document_text[:1000] if document_text else "无参考文档"
        
        prompt = f"""你是中国政治和社会领域的专家，任务是根据本体定义和模拟需求，生成{batch_size}个虚构但真实感强的政协委员人物。

## 本体定义
实体类型: {entity_types_str}
关系类型: {relation_types_str}

## 模拟需求
{requirement}

## 参考文档（政策背景）
{doc_preview}

## 要求
1. 生成{batch_size}个虚构人物，每人有独特的专业领域
2. 人物编号从 #{start_index} 到 #{start_index + batch_size - 1}
3. 覆盖不同实体类型（MemberOfCPPCC, GovernmentOfficial, Academic, Executive 等）
4. 姓名使用真实感强的中国姓名（两字或三字）
5. 每人有明确的专业领域（如教育、医疗、环保、科技、农业、养老、数字经济等）
6. 每人有独特的背景：年龄、性别、职业经历、MBTI性格
7. 摘要(summary)用中文，200字以内，描述人物的专业背景和主要关注议题
8. 属性(attributes)用JSON格式，包含：age(数字), gender("男"或"女"), profession(中文职业描述), domain(专业领域), entity_type(本体中的实体类型)
9. labels列表使用本体中的实体类型名称（如 MemberOfCPPCC）

## 输出格式（严格的JSON数组）
[
  {{
    "id": {start_index},
    "name": "张三",
    "labels": ["MemberOfCPPCC"],
    "summary": "教育工作者，关注乡村教育振兴与教育公平...",
    "attributes": {{
      "age": 52,
      "gender": "男",
      "profession": "中学教育专家",
      "domain": "教育",
      "entity_type": "MemberOfCPPCC"
    }}
  }}
]

注意：必须返回合法的JSON数组，不要任何额外文字。不要输出markdown代码块包裹。"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "你是中国政治领域专家。必须返回合法JSON数组。"},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.8,
                )
                
                content = response.choices[0].message.content.strip()
                
                # 提取JSON数组
                content = self._extract_json_array(content)
                if content is None:
                    raise ValueError("无法提取JSON数组")
                
                parsed = json.loads(content)
                if not isinstance(parsed, list):
                    raise ValueError("返回的不是JSON数组")
                
                entities = []
                for item in parsed:
                    if not isinstance(item, dict):
                        continue
                    
                    name = item.get("name", f"未命名实体_{start_index}")
                    labels = item.get("labels", ["Person"])
                    if not labels:
                        labels = ["Person"]
                    summary = item.get("summary", "")
                    attributes = item.get("attributes", {})
                    
                    entity = VirtualEntityNode(
                        uuid=f"virtual_{start_index}_{hash(name)}",
                        name=name,
                        labels=labels,
                        summary=summary,
                        attributes=attributes,
                    )
                    entities.append(entity)
                    start_index += 1
                
                return entities
                
            except Exception as e:
                logger.warning(f"虚拟实体生成失败 (尝试 {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
        
        # 兜底：用规则生成
        return self._generate_fallback_entities(batch_size, entity_types, start_index)
    
    def _extract_json_array(self, content: str) -> Optional[str]:
        """从LLM输出中提取JSON数组"""
        import re
        
        # 1. 尝试直接解析
        content = content.strip()
        if content.startswith("[") and content.endswith("]"):
            return content
        
        # 2. 去除 markdown 代码块
        match = re.search(r'\[([^\]]*)\]', content, re.DOTALL)
        if match:
            return match.group(1)
        
        # 3. 寻找最外层方括号
        start = content.find("[")
        if start == -1:
            return None
        
        # 从start开始找到匹配的]
        depth = 0
        for i in range(start, len(content)):
            if content[i] == '[':
                depth += 1
            elif content[i] == ']':
                depth -= 1
                if depth == 0:
                    return content[start:i+1]
        
        return None
    
    def _generate_fallback_entities(
        self,
        count: int,
        entity_types: List[str],
        start_index: int,
    ) -> List[VirtualEntityNode]:
        """规则生成兜底实体"""
        first_names = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "胡", "朱", "林", "何", "高", "郭", "马", "罗"]
        last_names = ["建国", "明华", "秀英", "志强", "淑贞", "文博", "雅琴", "伟民", "红梅", "志刚", "丽娟", "德昌", "玉梅", "学明", "翠兰", "光宗", "秀萍", "永平", "晓峰", "慧敏", "静怡", "宇航", "浩然", "雨萱", "思远"]
        domains = ["教育", "医疗", "环保", "科技", "农业", "养老", "数字经济", "住房", "交通", "文化", "体育", "金融", "就业", "食品安全", "能源", "社会保障"]
        entity_types = entity_types or ["MemberOfCPPCC"]
        
        entities = []
        for i in range(count):
            idx = start_index + i
            name = random.choice(first_names) + random.choice(last_names)
            domain = domains[i % len(domains)]
            etype = entity_types[i % len(entity_types)]
            
            entity = VirtualEntityNode(
                uuid=f"fallback_{idx}",
                name=name,
                labels=[etype],
                summary=f"{domain}领域专家，关注{domain}相关议题，提出{domain}方面建议。",
                attributes={
                    "age": random.randint(35, 70),
                    "gender": random.choice(["男", "女"]),
                    "profession": f"{domain}专家",
                    "domain": domain,
                    "entity_type": etype,
                },
            )
            entities.append(entity)
        
        logger.info(f"兜底生成了 {len(entities)} 个实体")
        return entities

