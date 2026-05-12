#!/usr/bin/env python3
"""完整流程测试：模拟50个政协委员 -> 生成 -> 运行 -> 收集结果"""

import sys, json, time, uuid, os
sys.path.insert(0, '/app/backend')

from app.config import Config
from app.services.ontology_generator import OntologyGenerator
from app.services.graph_builder import GraphBuilderService
from app.services.text_processor import TextProcessor
from app.services.simulation_manager import SimulationManager
from app.services.simulation_config_generator import SimulationConfigGenerator
from app.services.oasis_profile_generator import OasisProfileGenerator
from app.services.virtual_entity_generator import VirtualEntityGenerator
from zep_cloud.client import Zep
from zep_cloud.models import AddGraphDocumentsRequest, GraphDocument
from zep_cloud.external_clients.ontology import EntityModel, EntityText, EdgeModel

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

log("="*60)
log("完整流程：模拟50位全国政协委员")
log("="*60)

# ====== 1. 读文本 ======
text_data = open('/app/backend/uploads/projects/proj_fb8a19b8399d/extracted_text.txt').read()
text_data = TextProcessor.preprocess_text(text_data)
log(f"[1/5] 文本读取: {len(text_data)} 字符")

# ====== 2. 生成本体 + 图谱 ======
req = "模拟50个不同领域全国政协委员，分析政策趋势"
gen = OntologyGenerator()
t0 = time.time()
ontology = gen.generate(document_texts=[text_data], simulation_requirement=req)
log(f"[2/5] 本体生成: {time.time()-t0:.1f}s")
log(f"       实体: {len(ontology['entity_types'])}, 关系: {len(ontology['edge_types'])}")

# 创建Zep图谱
zep = Zep(api_key=Config.ZEP_API_KEY)
graph_name = f'mirofish_cppcc_{uuid.uuid4().hex[:12]}'
graph = zep.graph.add(name=graph_name, description='CPPCC simulation')
graph_id = graph.name
log(f"       图谱: {graph_id}")

# 设置本体
entity_types = []
for e in ontology['entity_types']:
    et = EntityModel(name=e['name'], description=e.get('description',''))
    for a in e.get('attributes', []):
        at = EntityText(name=a['name'], description=a.get('description',''), required=a.get('required', False))
        et.attributes.append(at)
    for ex in e.get('examples', []):
        if isinstance(ex, str):
            et.examples.append(ex)
    entity_types.append(et)

edge_types_map = {}
for e in ontology['edge_types']:
    et = EdgeModel(name=e['name'], description=e.get('description',''))
    edge_types_map[e['name']] = et

zep.graph.set_ontology(
    graph_id=graph_id,
    entity_types=entity_types,
    edge_types=list(edge_types_map.values()),
)
log(f"       本体设置完成")

# 注入文本
chunks = [text_data[i:i+4000] for i in range(0, len(text_data), 4000)]
for i, chunk in enumerate(chunks):
    zep.graph.document.add(graph_id=graph_id, documents=[GraphDocument(content=chunk)])
log(f"       文本注入完成 ({len(chunks)}块)")

# ====== 3. 生成虚拟实体 ======
log(f"[3/5] 开始生成50个虚拟政协委员...")
from app.utils.llm_client import LLMClient
llm = LLMClient()

ve_gen = VirtualEntityGenerator()
virtual_entities = ve_gen.generate_virtual_entities(
    entity_types=[e['name'] for e in ontology['entity_types']],
    relation_types=[e['name'] for e in ontology['edge_types']],
    requirement=req,
    target_count=30,  # 减少到30个以节省时间，但依然足够展示
    document_text=text_data,
)
log(f"       虚拟实体: {len(virtual_entities)} 个 ({time.time()-t0:.1f}s)")
for e in virtual_entities:
    etype = e.get_entity_type() or "?"
    log(f"         - {e.name} ({etype}): {e.summary[:50]}...")

# ====== 4. 生成Agent Profile ======
log(f"[4/5] 开始生成Agent Profile...")
profile_gen = OasisProfileGenerator(graph_id=None)
profiles = profile_gen.generate_profiles_from_entities(
    entities=virtual_entities,
    use_llm=True,
    parallel_count=5,
)
log(f"       Profile: {len(profiles)} 个 ({time.time()-t0:.1f}s)")

# 打印每个agent的人设
for p in profiles:
    log(f"       [Agent] {p.user_name} | {p.profession or 'N/A'} | 兴趣: {p.interested_topics}")

# ====== 5. 生成模拟配置 ======
log(f"[5/5] 生成模拟配置...")
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
log(f"       模拟时长: {sim_params.time_config.total_simulation_hours}h")
log(f"       每轮: {sim_params.time_config.minutes_per_round}min")
log(f"       Agent: {len(sim_params.agent_configs)} 个")
log(f"       热点话题: {sim_params.event_config.hot_topics}")
log(f"       叙事方向: {sim_params.event_config.narrative_direction[:80]}...")

# 打印初始激活序列（每个agent说什么）
log(f"\n{'='*60}")
log("初始激活序列（每个Agent的发言）：")
log(f"{'='*60}")

for i, post in enumerate(sim_params.event_config.initial_posts):
    agent_id = post.poster_agent_id
    profile = profiles[agent_id] if agent_id < len(profiles) else None
    name = profile.profession if profile else f"Agent {agent_id}"
    log(f"\n[Agent {agent_id}] {name}:")
    log(f"  类型: {post.poster_type}")
    log(f"  内容: {post.content}")
    if i >= 9:  # 最多显示10个
        log(f"\n  ... (还有 {len(sim_params.event_config.initial_posts) - 10} 条)")
        break

log(f"\n{'='*60}")
log("流程完成！")
log(f"{'='*60}")

# 保存完整结果
result = {
    'graph_id': graph_id,
    'entity_count': len(virtual_entities),
    'profiles': [p.to_reddit_format() for p in profiles],
    'simulation_config': {
        'time': {"total_simulation_hours": sim_params.time_config.total_simulation_hours,
                 "minutes_per_round": sim_params.time_config.minutes_per_round},
        'hot_topics': sim_params.event_config.hot_topics,
        'narrative_direction': sim_params.event_config.narrative_direction,
        'initial_posts': [
            {
                'agent_id': p.poster_agent_id,
                'role': p.poster_type,
                'content': p.content
            }
            for p in sim_params.event_config.initial_posts
        ]
    }
}

os.makedirs('/app/backend/uploads/projects/proj_fb8a19b8399d', exist_ok=True)
with open('/app/backend/uploads/projects/proj_fb8a19b8399d/cppcc_test_result.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
log(f"\n结果已保存到 test_result.json")
