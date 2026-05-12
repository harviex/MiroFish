#!/usr/bin/env python3
"""完整流程测试：模拟50个政协委员 -> 生成人设 -> 生成配置 -> 收集初始序列"""

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
from zep_cloud import Zep

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

log("=" * 60)
log("完整流程：模拟全国政协委员")
log("=" * 60)
overall_t0 = time.time()

# ====== 1. 读文本 ======
text_data = open('/app/backend/uploads/projects/proj_fb8a19b8399d/extracted_text.txt').read()
text_data = TextProcessor.preprocess_text(text_data)
log(f"[1/6] 文本读取: {len(text_data)} 字符")

# ====== 2. 生成本体 ======
req = "模拟50个不同领域全国政协委员，分析政策趋势"
gen = OntologyGenerator()
t0 = time.time()
ontology = gen.generate(document_texts=[text_data], simulation_requirement=req)
print(f"[2/6] 本体生成: {time.time()-t0:.1f}s")
print(f"       实体: {len(ontology['entity_types'])}, 关系: {len(ontology['edge_types'])}")
for e in ontology['entity_types']:
    print(f"         - {e['name']}: {e.get('description','')[:60]}")

# ====== 3. 创建图谱 ======
zep = Zep(api_key=Config.ZEP_API_KEY)
graph_name = f'mirofish_cppcc_{uuid.uuid4().hex[:12]}'
graph = zep.graph.add(name=graph_name, description='CPPCC simulation')
graph_id = graph.name
log(f"[3/6] 图谱创建: {graph_id}")

# 设置本体
builder = GraphBuilderService(api_key=Config.ZEP_API_KEY)
builder.set_ontology(graph_id, ontology)
log(f"       本体设置完成")

# 注入文本到图谱——用 GraphBuilderService 的方法
from zep_cloud import EpisodeData
chunks = TextProcessor.split_text(text_data, chunk_size=500, chunk_overlap=50)
print(f"       文本分块: {len(chunks)} 块，正在注入...")

for i in range(0, len(chunks), 3):
    batch = chunks[i:i+3]
    episodes = [EpisodeData(data=chunk, type="text") for chunk in batch]
    zep.graph.add_batch(graph_id=graph_id, episodes=episodes)
    print(f"         块 {min(i+3, len(chunks))}/{len(chunks)} 成功")
    time.sleep(1)

log(f"       图谱注入完成")

# ====== 4. 生成虚拟人物 ======
log(f"[4/6] 开始生成30个虚拟政协委员...")
from app.utils.llm_client import LLMClient

ve_gen = VirtualEntityGenerator()
virtual_entities = ve_gen.generate_virtual_entities(
    entity_types=[e['name'] for e in ontology['entity_types']],
    relation_types=[e['name'] for e in ontology['edge_types']],
    requirement=req,
    target_count=30,
    document_text=text_data,
)
log(f"       生成: {len(virtual_entities)} 个实体")
for e in virtual_entities:
    etype = e.get_entity_type() or "?"
    log(f"         {e.name} ({etype})")

# ====== 5. 生成Agent Profile ======
log(f"[5/6] 开始生成Agent Profile...")
profile_gen = OasisProfileGenerator(graph_id=None)
profiles = profile_gen.generate_profiles_from_entities(
    entities=virtual_entities,
    use_llm=True,
    parallel_count=5,
)
log(f"       Profile: {len(profiles)} 个")
for p in profiles:
    name = p.user_name
    prof = p.profession or p.source_entity_type or 'N/A'
    topics = ', '.join(p.interested_topics[:3])
    log(f"         {name} | {prof} | {topics}")

# ====== 6. 生成模拟配置 ======
log(f"[6/6] 生成模拟配置...")
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
print(f"       配置生成: {time.time()-t0:.1f}s")
print(f"       模拟时长: {sim_params.time_config.total_simulation_hours} 小时")
print(f"       每轮: {sim_params.time_config.minutes_per_round} 分钟")
print(f"       Agent数: {len(sim_params.agent_configs)}")
print(f"\n       热点话题:")
for t in sim_params.event_config.hot_topics:
    print(f"         #{t}")
print(f"\n       叙事方向: {sim_params.event_config.narrative_direction[:120]}...")

# 打印初始序列 - 每个Agent说什么
print(f"\n{'='*60}")
print("初始激活序列（各Agent发言）：")
print(f"{'='*60}")

for i, post in enumerate(sim_params.event_config.initial_posts):
    agent_id = post.poster_agent_id
    if agent_id < len(profiles):
        profile = profiles[agent_id]
        name = profile.name
        profession = profile.profession or profile.source_entity_type or 'N/A'
    else:
        name = f"Agent {agent_id}"
        profession = 'N/A'
    
    print(f"\n[{agent_id}] {name} ({profession})")
    print(f"  角色: {post.poster_type}")
    print(f"  发言: {post.content}")
    if i >= 14:
        print(f"\n  ... (还有 {len(sim_params.event_config.initial_posts) - 15} 条)")
        break

# ====== 总结 ======
total_time = time.time() - overall_t0
print(f"\n{'='*60}")
print(f"总耗时: {total_time:.1f}s ({total_time/60:.1f}分钟)")
print(f"图谱: {graph_id}")
print(f"人物: {len(profiles)} 个")
print(f"模拟时长: {sim_params.time_config.total_simulation_hours}h")
print(f"{'='*60}")

# 保存结果
result = {
    'graph_id': graph_id,
    'entity_count': len(virtual_entities),
    'profiles': [p.to_reddit_format() for p in profiles],
    'simulation_config': {
        'total_hours': sim_params.time_config.total_simulation_hours,
        'minutes_per_round': sim_params.time_config.minutes_per_round,
        'agent_count': len(sim_params.agent_configs),
        'hot_topics': sim_params.event_config.hot_topics,
        'narrative_direction': sim_params.event_config.narrative_direction,
        'initial_posts': [
            {
                'agent_id': p.poster_agent_id,
                'name': profiles[p.poster_agent_id].name if p.poster_agent_id < len(profiles) else 'Unknown',
                'role': p.poster_type,
                'content': p.content
            }
            for p in sim_params.event_config.initial_posts
        ]
    },
    'total_time_seconds': total_time,
}

with open('/app/backend/uploads/projects/proj_fb8a19b8399d/cppcc_full_result.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
log(f"\n结果已保存到 cppcc_full_result.json")
