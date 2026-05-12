#!/usr/bin/env python3
"""
完整流程测试：模拟政协委员 -> 本体 -> 图谱 -> 人物 -> 人设 -> 配置 -> 初始序列
跳过LLM本体生成（改用预定义本体），节省时间并提高可靠性
"""
import sys, json, time, uuid, os
sys.path.insert(0, '/app/backend')

from app.config import Config
from app.services.graph_builder import GraphBuilderService
from app.services.text_processor import TextProcessor
from app.services.oasis_profile_generator import OasisProfileGenerator
from app.services.simulation_config_generator import SimulationConfigGenerator
from app.services.virtual_entity_generator import VirtualEntityGenerator
from zep_cloud import Zep, EpisodeData

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

overall_t0 = time.time()

# ====== 预定义的本体 ======
ONTOLOGY = {
    "entity_types": [
        {
            "name": "CPPCCMember",
            "description": "全国政协委员，按领域分类",
            "attributes": [
                {"name": "full_name", "type": "text", "description": "姓名"},
                {"name": "domain", "type": "text", "description": "专业领域"},
                {"name": "age", "type": "number", "description": "年龄"},
            ],
            "examples": ["陈明远", "林雅萍", "赵国强"],
        },
        {
            "name": "EducationExpert",
            "description": "教育领域政策专家",
            "attributes": [{"name": "specialization", "type": "text", "description": "专长领域"}],
            "examples": ["教育学者"],
        },
        {
            "name": "MedicalExpert",
            "description": "医疗健康政策专家",
            "attributes": [{"name": "title", "type": "text", "description": "职称"}],
            "examples": ["主任医师"],
        },
        {
            "name": "AgricultureExpert",
            "description": "农业与农村经济专家",
            "attributes": [{"name": "focus", "type": "text", "description": "关注方向"}],
            "examples": ["三农研究员"],
        },
        {
            "name": "TechExpert",
            "description": "科技创新与数字经济专家",
            "attributes": [{"name": "field", "type": "text", "description": "技术领域"}],
            "examples": ["AI研究员"],
        },
        {
            "name": "EnvironmentExpert",
            "description": "环保与双碳政策专家",
            "attributes": [{"name": "domain", "type": "text", "description": "研究方向"}],
            "examples": ["环保政策研究员"],
        },
        {
            "name": "SocialSecurityExpert",
            "description": "社会保障与民生专家",
            "attributes": [{"name": "domain", "type": "text", "description": "关注领域"}],
            "examples": ["社保政策专家"],
        },
        {
            "name": "GovernmentAgency",
            "description": "政府机构",
            "attributes": [{"name": "name", "type": "text"}],
            "examples": ["教育部", "民政部"],
        },
        {"name": "Person", "description": "通用个人", "attributes": [{"name": "full_name", "type": "text"}], "examples": []},
        {"name": "Organization", "description": "通用组织", "attributes": [{"name": "name", "type": "text"}], "examples": []},
    ],
    "edge_types": [
        {"name": "WORKS_FOR", "description": "在某机构工作", "source_targets": [], "attributes": []},
        {"name": "PROPOSES_ON", "description": "在某个议题上提出建议", "source_targets": [], "attributes": []},
        {"name": "COLLABORATES_WITH", "description": "与某人或机构合作", "source_targets": [], "attributes": []},
        {"name": "SUPPORTS", "description": "支持某个政策", "source_targets": [], "attributes": []},
        {"name": "OPPOSES", "description": "反对某个政策", "source_targets": [], "attributes": []},
        {"name": "RESPONDS_TO", "description": "回应某个政策或事件", "source_targets": [], "attributes": []},
        {"name": "REPORTS_ON", "description": "报道某个议题", "source_targets": [], "attributes": []},
        {"name": "AFFILIATED_WITH", "description": "隶属于某个组织", "source_targets": [], "attributes": []},
    ],
    "analysis_summary": "基于政策演进趋势和政协委员角色设计的本体",
}

log("=" * 60)
log("完整流程：模拟50位全国政协委员")
log("=" * 60)

# ====== 1. 读文本 ======
text_data = open('/app/backend/uploads/projects/proj_fb8a19b8399d/extracted_text.txt').read()
text_data = TextProcessor.preprocess_text(text_data)
log(f"[1/6] 文本读取: {len(text_data)} 字符")

# ====== 2. 创建Zep图谱 + 本体 ======
zep = Zep(api_key=Config.ZEP_API_KEY)
graph_id = f'mirofish_cppcc_{uuid.uuid4().hex[:12]}'
graph = zep.graph.create(graph_id=graph_id, name='CPPCC Simulation', description='模拟全国政协委员')
log(f"[2/6] 图谱创建: {graph_id}")

builder = GraphBuilderService(api_key=Config.ZEP_API_KEY)
builder.set_ontology(graph_id, ONTOLOGY)
log(f"       本体设置: 10实体, 8关系")

# 注入文本
chunks = TextProcessor.split_text(text_data, chunk_size=500, chunk_overlap=50)
log(f"       文本分块: {len(chunks)} 块，正在注入...")
for i in range(0, len(chunks), 3):
    batch = chunks[i:i+3]
    episodes = [EpisodeData(data=chunk, type="text") for chunk in batch]
    zep.graph.add_batch(graph_id=graph_id, episodes=episodes)
    log(f"         块 {min(i+3, len(chunks))}/{len(chunks)} OK")
    time.sleep(1)
log(f"       图谱注入完成")

# ====== 3. LLM生成虚拟人物 ======
req = "模拟50个不同领域全国政协委员，分析政策趋势，覆盖教育、医疗、农业、科技、环保、社保等领域"
log(f"[3/6] 开始生成30个虚拟政协委员...")
t0 = time.time()
ve_gen = VirtualEntityGenerator()
virtual_entities = ve_gen.generate_virtual_entities(
    entity_types=[e['name'] for e in ONTOLOGY['entity_types']],
    relation_types=[e['name'] for e in ONTOLOGY['edge_types']],
    requirement=req,
    target_count=30,
    document_text=text_data,
)
log(f"       生成 {len(virtual_entities)} 个人物 ({time.time()-t0:.1f}s)")
for e in virtual_entities:
    etype = e.get_entity_type() or "?"
    log(f"         {e.name} ({etype}): {e.summary[:60]}...")

# ====== 4. 生成Agent Profile ======
log(f"[4/6] 开始生成Agent Profile...")
t0 = time.time()
profile_gen = OasisProfileGenerator(graph_id=None)
profiles = profile_gen.generate_profiles_from_entities(
    entities=virtual_entities,
    use_llm=True,
    parallel_count=5,
)
log(f"       Profile: {len(profiles)} 个 ({time.time()-t0:.1f}s)")
for p in profiles:
    name = p.user_name
    prof = p.profession or p.source_entity_type or 'N/A'
    topics = ', '.join(p.interested_topics[:3])
    log(f"         {name} | {prof} | 话题: {topics}")

# ====== 5. 生成模拟配置 ======
log(f"[5/6] 生成模拟配置...")
t0 = time.time()
config_gen = SimulationConfigGenerator()
sim_params = config_gen.generate_config(
    simulation_id="sim_cppcc_test",
    project_id="proj_cppcc_test",
    graph_id=graph_id,
    simulation_requirement=req,
    document_text=text_data,
    entities=virtual_entities,
    enable_twitter=True,
    enable_reddit=True,
)
log(f"       配置生成: {time.time()-t0:.1f}s")
log(f"       模拟时长: {sim_params.time_config.total_simulation_hours}h")
log(f"       每轮: {sim_params.time_config.minutes_per_round}min")
log(f"       Agent数: {len(sim_params.agent_configs)}")
log(f"       热点话题: {sim_params.event_config.hot_topics}")
log(f"       叙事: {sim_params.event_config.narrative_direction[:100]}...")

# ====== 6. 打印初始序列 ======
log(f"\n{'='*60}")
log("初始激活序列（各Agent发言）：")
log(f"{'='*60}")

for i, post in enumerate(sim_params.event_config.initial_posts):
    agent_id = post.poster_agent_id
    if agent_id < len(profiles):
        profile = profiles[agent_id]
        name = profile.name
        profession = profile.profession or profile.source_entity_type or 'N/A'
    else:
        name = f"Agent {agent_id}"
        profession = 'N/A'
    
    log(f"\n[{agent_id}] {name} ({profession})")
    log(f"  角色: {post.poster_type}")
    log(f"  发言: {post.content}")

# ====== 总结 ======
total_time = time.time() - overall_t0
log(f"\n{'='*60}")
log(f"总耗时: {total_time:.1f}s ({total_time/60:.1f}分钟)")
log(f"图谱: {graph_id}")
log(f"人物: {len(profiles)} 个")
log(f"{'='*60}")

# 保存完整结果
result = {
    'graph_id': graph_id,
    'entity_count': len(virtual_entities),
    'profiles': [p.to_reddit_format() for p in profiles],
    'initial_posts': [
        {
            'agent_id': p.poster_agent_id,
            'name': profiles[p.poster_agent_id].name if p.poster_agent_id < len(profiles) else 'Unknown',
            'role': p.poster_type,
            'content': p.content
        }
        for p in sim_params.event_config.initial_posts
    ],
    'hot_topics': sim_params.event_config.hot_topics,
    'narrative': sim_params.event_config.narrative_direction,
    'total_time_seconds': total_time,
}
with open('/app/backend/uploads/projects/proj_fb8a19b8399d/cppcc_result.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
log(f"结果已保存到 cppcc_result.json")
