<template>
  <div class="home-container">
    <!-- 顶部导航栏 -->
    <nav class="navbar">
      <div class="nav-brand">MIROFISH</div>
      <div class="nav-links">
        <LanguageSwitcher />
        <a href="https://github.com/666ghj/MiroFish" target="_blank" class="github-link">
          {{ $t('nav.visitGithub') }} <span class="arrow">↗</span>
        </a>
      </div>
    </nav>

    <div class="main-content">
      <!-- 下半部分：双栏布局 -->
      <section class="dashboard-section">
        <!-- 左栏：专家会堂 -->
        <div class="left-panel">
          <div class="panel-header">
            <span class="status-dot">◇</span> 专家会堂
          </div>
          
          <!-- Step 1: 意图分析结果 -->
          <div v-if="currentStep === 1 && intentAnalyzed" class="panel-card intent-card">
            <div class="card-title">🎯 研讨分析</div>
            <div class="int-summary">{{ intentAnalyzed.summary }}</div>
            <div class="int-label">建议研讨领域：</div>
            <div class="int-domains">
              <label v-for="(d, i) in (intentAnalyzed?.domains || [])" :key="i" class="domain-check">
                <input type="checkbox" v-model="selectedDomainIndices" :value="i" />
                <span class="domain-label">{{ d.label }}</span>
                <span class="domain-reason">{{ d.reason }}</span>
              </label>
            </div>
            <button class="action-btn primary" @click="handleGenerateExperts">
              ✓ 确认并生成专家阵容
            </button>
          </div>

          <!-- Loading: 意图分析中 -->
          <div v-if="intentAnalyzing" class="panel-card loading-card">
            <div class="loading-spinner-spin"></div>
            <div class="loading-text">正在分析研讨意图...</div>
          </div>

          <!-- Loading: 生成专家中 -->
          <div v-if="expertsGenerating" class="panel-card loading-card">
            <div class="loading-spinner-spin"></div>
            <div class="loading-text">正在组建专家团队...</div>
          </div>

          <!-- Step 2: 专家阵容展示 -->
          <div v-if="currentStep === 2 && generatedExperts.length > 0" class="panel-card expert-card">
            <div class="card-title">👥 专家阵容 ({{ generatedExperts.length }}人)</div>

            <div class="expert-scroll-area">
              <div
                v-for="(expert, i) in generatedExperts"
                :key="i" class="expert-chip"
                :class="{ 'expert-checked': selectedExpertIndices.includes(i) }"
              >
                <div class="expert-chip-header">
                  <input type="checkbox" :value="i" v-model="selectedExpertIndices" class="expert-checkbox" />
                  <span class="expert-name">{{ expert.name }}</span>
                  <span class="expert-identity">{{ expert.identity }}</span>
                </div>
                <div class="expert-chip-body">
                  <span class="expert-domain-tag">{{ expert.domain }}</span>
                  <div class="expert-stance">立场: {{ expert.stance }}</div>
                  <div class="expert-style">🗣 {{ expert.speaking_style }}</div>
                </div>
              </div>
            </div>

            <!-- 增量调整 -->
            <div class="expert-adjust">
              <!-- 追加数量控制 -->
              <div class="expert-count-row">
                <label class="expert-count-label">追加数量：</label>
                <input
                  type="number"
                  v-model.number="addCount"
                  class="expert-count-input"
                  min="-20"
                  max="20"
                />
                <span class="expert-count-unit">人（负数移除）</span>
              </div>
              <textarea
                v-model="additionalExpertRequest"
                class="expert-input"
                placeholder="是否需要增加其他角色？（例：添加一位持反对意见的学者）"
                rows="2"
              ></textarea>
            </div>

            <!-- 步骤导航 + 追加角色（同一行） -->
            <div class="step-nav">
              <button class="action-btn small ghost" @click="goPrevStep">⬅ 上一步</button>
              <button class="action-btn small" @click="handleAddExperts">+ 追加角色</button>
              <button class="action-btn small primary" @click="goNextStep">下一步 ✅</button>
            </div>
          </div>
          
          <!-- 工作流步骤 (压缩显示) -->
          <div class="workflow-steps-compact">
            <div class="workflow-list">
              <div class="workflow-item">
                <span class="step-num">01</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step01Title') }}</div>
                  <div class="step-desc">{{ $t('home.step01Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">02</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step02Title') }}</div>
                  <div class="step-desc">{{ $t('home.step02Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">03</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step03Title') }}</div>
                  <div class="step-desc">{{ $t('home.step03Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">04</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step04Title') }}</div>
                  <div class="step-desc">{{ $t('home.step04Desc') }}</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">05</span>
                <div class="step-info">
                  <div class="step-title">{{ $t('home.step05Title') }}</div>
                  <div class="step-desc">{{ $t('home.step05Desc') }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右栏：交互控制台 -->
        <div class="right-panel">
          <div class="console-box">
            <!-- 上传区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">{{ $t('home.realitySeed') }}</span>
                <span class="console-meta">{{ $t('home.supportedFormats') }}</span>
              </div>
              
              <div 
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt"
                  @change="handleFileSelect"
                  style="display: none"
                  :disabled="loading"
                />
                
                <div v-if="files.length === 0" class="upload-placeholder">
                  <div class="upload-icon">↑</div>
                  <div class="upload-title">{{ $t('home.dragToUpload') }}</div>
                  <div class="upload-hint">{{ $t('home.orBrowse') }}</div>
                </div>
                
                <div v-else class="file-list">
                  <div v-for="(file, index) in files" :key="index" class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 分割线 -->
            <div class="console-divider">
              <span>{{ $t('home.inputParams') }}</span>
            </div>

            <!-- 输入区域 -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">{{ $t('home.simulationPrompt') }}</span>
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  :placeholder="$t('home.promptPlaceholder')"
                  rows="6"
                  :disabled="loading"
                ></textarea>
                <div class="model-badge">⚙ {{ activeModelDisplay }}</div>
              </div>

              <!-- 意图分析 / 生成专家按钮 -->
              <button
                class="generate-experts-btn"
                @click="!intentAnalyzed ? handleAnalyzeIntent() : handleGenerateExperts()"
                :disabled="!(formData.simulationRequirement.trim() !== '') || intentAnalyzing || expertsGenerating"
                v-if="!intentAnalyzed"
              >
                <span>🎯 分析研讨意图</span>
              </button>
              <button
                class="generate-experts-btn"
                @click="handleGenerateExperts()"
                :disabled="!intentAnalyzed || intentAnalyzing || expertsGenerating"
                v-if="intentAnalyzed"
              >
                <span>👥 生成专家阵容</span>
              </button>

              <!-- 常驻模型切换栏 -->
              <div class="model-inline-form">
                <label class="model-inline-label">{{ $t('home.modelId') }}</label>
                <input
                  v-model="modelId"
                  class="model-inline-input"
                  :placeholder="$t('home.modelIdPlaceholder')"
                  :disabled="switching"
                  @keyup.enter="handleSwitchModel"
                />
                <label class="model-inline-label">{{ $t('home.baseUrl') }}</label>
                <input
                  v-model="baseUrl"
                  class="model-inline-input"
                  :placeholder="$t('home.baseUrlPlaceholder')"
                  :disabled="switching"
                  @keyup.enter="handleSwitchModel"
                />
                <button
                  class="model-switch-btn"
                  @click="handleSwitchModel"
                  :disabled="switching"
                >
                  <span v-if="!switching">{{ $t('home.modelSwitch') }}</span>
                  <span v-else>{{ $t('home.switchingModel') }}</span>
                </button>
                <div
                  v-if="switchMsg"
                  class="model-switch-msg"
                  :class="switchMsgType"
                >
                  {{ switchMsg }}
                </div>
              </div>
            </div>

            <!-- 启动按钮 -->
            <div class="console-section btn-section">
              <button 
                class="start-engine-btn"
                @click="startSimulation"
                :disabled="!canSubmit || loading"
              >
                <span v-if="!loading">{{ $t('home.startEngine') }}</span>
                <span v-else>{{ $t('home.initializing') }}</span>
                <span class="btn-arrow">→</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 历史项目数据库 -->
      <HistoryDatabase />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { updateConfig, analyzeIntent, generateExperts } from '../api/simulation'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import LanguageSwitcher from '../components/LanguageSwitcher.vue'

const router = useRouter()

// 表单数据
const formData = ref({
  simulationRequirement: ''
})

// 文件列表
const files = ref([])

// 状态
const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)

// 模型切换状态
const modelId = ref('')
const baseUrl = ref('')
const switching = ref(false)
const switchMsg = ref('')
const switchMsgType = ref('')

// 专家会堂状态
const addCount = ref(0)
const additionalExpertRequest = ref('')
const selectedExpertIndices = ref([])
const currentStep = ref(1) // 1=分析结果 2=专家阵容
const intentAnalyzing = ref(false)
const expertsGenerating = ref(false)
const intentAnalyzed = ref(null)  // { summary, domains }
const selectedDomainIndices = ref([])
const generatedExperts = ref([])

// 计算属性:当前模型显示
const activeModelDisplay = computed(() => {
  return modelId.value || 'MiroFish-V1.0'
})

// 模型验证
const validateModelId = (id) => {
  return id && id.includes('/')
}

// 切换模型
const handleSwitchModel = async () => {
  if (!validateModelId(modelId.value)) {
    switchMsg.value = $t('home.invalidModelId')
    switchMsgType.value = 'error'
    return
  }

  switching.value = true
  switchMsg.value = ''

  try {
    const res = await updateConfig({
      model_name: modelId.value,
      base_url: baseUrl.value || undefined
    })

    if (res.data?.success) {
      switchMsg.value = $t('home.switchSuccess', { model: modelId.value })
      switchMsgType.value = 'success'
    } else {
      switchMsg.value = $t('home.switchFailed', { error: res.data?.error || 'Unknown' })
      switchMsgType.value = 'error'
    }
  } catch (e) {
    switchMsg.value = $t('home.switchFailed', { error: e.message || 'Unknown' })
    switchMsgType.value = 'error'
  } finally {
    switching.value = false
  }
}

// 文件输入引用
const fileInput = ref(null)

// 计算属性:是否可以提交
const canSubmit = computed(() => {
  return formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
})

// 专家会堂相关方法
const canAnalyzeExperts = computed(() => {
  return formData.value.simulationRequirement.trim() !== ''
})

// Step 1: 分析意图
const handleAnalyzeIntent = async () => {
  if (!canAnalyzeExperts.value || intentAnalyzing.value) return
  
  intentAnalyzing.value = true
  selectedDomainIndices.value = []
  
  try {
    const res = await analyzeIntent({ sim_requirement: formData.value.simulationRequirement })
    if (res.success) {
      intentAnalyzed.value = res.data
      // 默认全选所有领域 (防御性: 检查 domains 是否存在)
      const domains = intentAnalyzed.value?.domains
      if (domains && Array.isArray(domains)) {
        selectedDomainIndices.value = domains.map((_, i) => i)
      } else {
        console.warn('意图分析返回缺少 domains 字段:', res.data)
        selectedDomainIndices.value = []
        alert('意图分析结果格式异常，缺少领域信息。请重试。')
        intentAnalyzed.value = null
      }
    } else {
      alert(res.data?.error || '分析失败')
    }
  } catch (error) {
    console.error('意图分析失败:', error)
    alert('意图分析失败: ' + (error.message || '网络错误'))
  } finally {
    intentAnalyzing.value = false
  }
}

// Step 2: 生成专家阵容
const handleGenerateExperts = async () => {
  if (!intentAnalyzed.value || selectedDomainIndices.value.length === 0) return

  expertsGenerating.value = true
  generatedExperts.value = []
  selectedExpertIndices.value = []

  try {
    const selectedDomains = selectedDomainIndices.value.map(i => intentAnalyzed.value.domains[i])
    const res = await generateExperts({
      sim_requirement: formData.value.simulationRequirement,
      selected_domains: selectedDomains,
      count: 10
    })
    if (res.success) {
      generatedExperts.value = res.data.experts || []
      // 默认全选
      selectedExpertIndices.value = generatedExperts.value.map((_, i) => i)
      // 切换到专家阵容步骤
      currentStep.value = 2
    } else {
      alert(res.error || '生成失败')
    }
  } catch (error) {
    console.error('生成专家阵容失败:', error)
    alert('生成专家阵容失败: ' + (error.message || '网络错误'))
  } finally {
    expertsGenerating.value = false
  }
}

// 追加/移除角色
const handleAddExperts = async () => {
  const n = addCount.value
  if (n === 0) return

  // 移除模式
  if (n < 0) {
    const removeCount = Math.min(Math.abs(n), generatedExperts.value.length)
    // 优先移除已勾选的
    const checked = new Set(selectedExpertIndices.value)
    const indicesToRemove = [...checked]
    // 如果勾选的不够，从末尾补
    if (indicesToRemove.length < removeCount) {
      for (let i = generatedExperts.value.length - 1; i >= 0 && indicesToRemove.length < removeCount; i--) {
        if (!indicesToRemove.includes(i)) indicesToRemove.push(i)
      }
    }
    const removeSet = new Set(indicesToRemove.slice(0, removeCount))
    generatedExperts.value = generatedExperts.value.filter((_, i) => !removeSet.has(i))
    selectedExpertIndices.value = selectedExpertIndices.value.filter(i => !removeSet.has(i))
    addCount.value = 0
    return
  }

// 添加模式
  if (generatedExperts.value.length === 0) {
    alert('请先生成初始专家阵容')
    return
  }

  expertsGenerating.value = true

  try {
    const selectedDomains = selectedDomainIndices.value.map(i => intentAnalyzed.value.domains[i])
    const currentCount = generatedExperts.value.length
    const res = await generateExperts({
      sim_requirement: formData.value.simulationRequirement,
      selected_domains: selectedDomains,
      existing_experts: generatedExperts.value,
      additional_request: additionalExpertRequest.value,
      count: currentCount + n
    })
    if (res.success) {
      const rawExperts = res.data.experts || []
      // 过滤空数据（不去重，因为增量模式下LLM应该只返回新角色）
      const validNewExperts = rawExperts.filter(e =>
        e && e.name && e.identity && e.domain
      )
      if (validNewExperts.length > 0) {
        generatedExperts.value = generatedExperts.value.concat(validNewExperts)
        addCount.value = 0
        additionalExpertRequest.value = ''
      } else {
        alert('LLM 未返回有效的新角色（返回 ' + rawExperts.length + ' 个，全部无效）')
      }
    } else {
      alert(res.error || '追加失败')
    }
} catch (error) {
    console.error('追加角色失败:', error)
    alert('追加角色失败: ' + (error.message || '网络错误'))
  } finally {
    expertsGenerating.value = false
  }
}

// 上一步：回到建议研讨领域
const goPrevStep = () => {
  currentStep.value = 1
}

// 现实种子文件名
const seedFileName = ref('')

// 点击下一步：将选中专家生成为 .md 文件并添加到现实种子上传列表
const goNextStep = () => {
  const experts = generatedExperts.value
  if (!experts.length) return
  const selectedSet = new Set(selectedExpertIndices.value)
  const targetExperts = selectedSet.size > 0
    ? experts.filter((_, i) => selectedSet.has(i))
    : experts
  if (!targetExperts.length) return

  // 生成 Markdown 内容
  const lines = ['# 专家阵容 - 现实种子\n']
  targetExperts.forEach((e, i) => {
    lines.push(`## ${i + 1}. ${e.name}\n`)
    lines.push(`- **身份**: ${e.identity || '暂无'}`)
    lines.push(`- **领域**: ${e.domain || '暂无'}`)
    lines.push(`- **背景**: ${e.background || '暂无'}`)
    lines.push(`- **立场**: ${e.stance || '暂无'}`)
    lines.push(`- **风格**: ${e.speaking_style || '暂无'}`)
    if (e.mindset) lines.push(`- **思维倾向**: ${e.mindset}`)
    if (e.focus && e.focus.length) lines.push(`- **核心关注点**: ${e.focus.join('、')}`)
    lines.push('')
  })
  const content = lines.join('\n')
  const fileName = `专家阵容_${Date.now()}.md`
  seedFileName.value = fileName

  // 创建 File 对象并添加到上传列表
  const blob = new Blob([content], { type: 'text/markdown' })
  const file = new File([blob], fileName, { type: 'text/markdown' })
  addFiles([file])
}

// 触发文件选择
const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

// 处理拖拽相关
const handleDragOver = (e) => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (loading.value) return
  
  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

// 添加文件
const addFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

// 移除文件
const removeFile = (index) => {
  files.value.splice(index, 1)
}

// 开始模拟 - 立即跳转，API调用在Process页面进行
const startSimulation = () => {
  if (!canSubmit.value || loading.value) return
  
  // 存储待上传的数据（包含专家阵容）
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement, generatedExperts.value)
    
    // 立即跳转到Process页面（使用特殊标识表示新建项目）
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}
</script>

<style scoped>
/* 全局变量与重置 */
:root {
  --black: #000000;
  --white: #FFFFFF;
  --orange: #FF4500;
  --gray-light: #F5F5F5;
  --gray-text: #666666;
  --border: #E5E5E5;
  /* 
    使用 Space Grotesk 作为主要标题字体，JetBrains Mono 作为代码/标签字体
    确保已在 index.html 引入这些 Google Fonts 
  */
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', 'Noto Sans SC', system-ui, sans-serif;
  --font-cn: 'Noto Sans SC', system-ui, sans-serif;
}

.home-container {
  min-height: 100vh;
  background: var(--white);
  font-family: var(--font-sans);
  color: var(--black);
}

/* 顶部导航 */
.navbar {
  height: 60px;
  background: var(--black);
  color: var(--white);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.2rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 16px;
}

.github-link {
  color: var(--white);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: opacity 0.2s;
}

.github-link:hover {
  opacity: 0.8;
}

.arrow {
  font-family: sans-serif;
}

/* 主要内容区 */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 40px;
}

/* Dashboard 双栏布局 */
.dashboard-section {
  display: flex;
  gap: 60px;
  padding-top: 30px;
  align-items: flex-start;
}

.dashboard-section .left-panel,
.dashboard-section .right-panel {
  display: flex;
  flex-direction: column;
}

/* 左侧面板 */
.left-panel {
  flex: 0.8;
}

.panel-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #999;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.status-dot {
  color: var(--orange);
  font-size: 0.8rem;
}

.section-title {
  font-size: 2rem;
  font-weight: 520;
  margin: 0 0 15px 0;
}

.section-desc {
  color: var(--gray-text);
  margin-bottom: 25px;
  line-height: 1.6;
}

.metrics-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.metric-card {
  border: 1px solid var(--border);
  padding: 20px 30px;
  min-width: 150px;
}

.metric-value {
  font-family: var(--font-mono);
  font-size: 1.8rem;
  font-weight: 520;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 0.85rem;
  color: #999;
}

/* 项目模拟步骤介绍 */
.steps-container {
  border: 1px solid var(--border);
  padding: 30px;
  position: relative;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon {
  font-size: 1.2rem;
  line-height: 1;
}

/* 专家会堂 UI */
.expert-hall-empty {
  border: 1px solid var(--border);
  padding: 24px;
  text-align: center;
}
.expert-hall-empty .empty-icon { font-size: 2rem; margin-bottom: 12px; }
.expert-hall-empty .empty-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; }
.expert-hall-empty .empty-desc { font-size: 0.85rem; color: #999; line-height: 1.5; }

.panel-card {
  border: 1px solid var(--border);
  padding: 20px;
  margin-bottom: 12px;
}

.card-title {
  font-family: var(--font-mono);
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 14px;
  letter-spacing: 0.5px;
}

/* 空状态 */
.expert-hall-empty .empty-icon { font-size: 2rem; margin-bottom: 12px; }
.expert-hall-empty .empty-title { font-size: 1.1rem; font-weight: 600; margin-bottom: 8px; }
.expert-hall-empty .empty-desc { font-size: 0.85rem; color: #999; line-height: 1.5; }

/* 意图分析卡片 */
.intent-card .int-summary {
  font-size: 0.9rem;
  color: var(--black);
  font-weight: 500;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.intent-card .int-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #999;
  margin-bottom: 10px;
  text-transform: uppercase;
}
.int-domains {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}
.domain-check {
  display: flex;
  flex-direction: column;
  gap: 2px;
  cursor: pointer;
  padding: 8px 10px;
  background: #f9f9f9;
  border: 1px solid transparent;
  border-radius: 6px;
  transition: all 0.15s;
}
.domain-check:hover { border-color: var(--border); background: #fff; }
.domain-check input[type="checkbox"] { position: absolute; opacity: 0; cursor: pointer; }
.domain-label {
  font-weight: 600;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 6px;
}
.domain-label::before {
  content: '□';
  font-size: 1rem;
  color: #999;
}
.domain-check input:checked + .domain-label::before {
  content: '☑';
  color: var(--orange);
}
.domain-reason {
  font-size: 0.75rem;
  color: #999;
  padding-left: 20px;
}

/* 卡片操作按钮 */
.action-btn {
  display: block;
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border);
  background: transparent;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 6px;
}
.action-btn.primary {
  background: #000;
  color: #fff;
  border-color: #000;
}
.action-btn.primary:hover { opacity: 0.85; }
.action-btn.small {
  width: auto;
  padding: 6px 12px;
  font-size: 0.7rem;
}
.action-btn.small.ghost {
  background: transparent;
}
.action-btn.small:hover { background: #f0f0f0; }

/* Loading 卡片 */
.loading-card {
  border: 1px solid var(--border);
  padding: 32px;
  text-align: center;
}
.loading-card .loading-text {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: #999;
}
.loading-spinner-spin {
  width: 32px;
  height: 32px;
  border: 3px solid #eee;
  border-top-color: var(--orange);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 14px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 专家阵容卡片 */
.expert-card {
  border: 1px solid var(--border);
  padding: 16px;
}
.expert-card .card-title { padding: 0 4px 12px; }

.expert-scroll-area {
  max-height: 420px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 4px;
  margin-bottom: 12px;
}
.expert-scroll-area::-webkit-scrollbar { width: 4px; }
.expert-scroll-area::-webkit-scrollbar-track { background: #f3f3f3; }
.expert-scroll-area::-webkit-scrollbar-thumb { background: #ccc; border-radius: 2px; }

.expert-chip {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 10px 14px;
  transition: all 0.15s;
  background: #fafafa;
}
.expert-chip:hover { border-color: var(--orange); background: #fff; }

.expert-chip-header {
  display: flex;
  justify-content: flex-start;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 6px;
}
.expert-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--black);
  text-align: left;
}
.expert-identity {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  background: #f0ebe4;
  color: #8b7355;
  padding: 2px 8px;
  border-radius: 3px;
  white-space: nowrap;
}

.expert-chip-body {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.expert-domain-tag {
  font-family: var(--font-mono);
  font-size: 0.6rem;
  background: #e8edf2;
  color: #5a7ea6;
  padding: 1px 6px;
  border-radius: 2px;
  display: inline-block;
  width: fit-content;
}
.expert-stance {
  font-size: 0.78rem;
  color: #555;
  line-height: 1.4;
}
.expert-style {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #999;
}

/* 复选框 */
.expert-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--orange);
  cursor: pointer;
  margin-right: 4px;
}

.expert-chip-checked {
  border-color: var(--orange) !important;
  background: #fff3e0 !important;
}

/* 追加数量输入 */
.expert-count-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.expert-count-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #999;
  white-space: nowrap;
}
.expert-count-input {
  width: 50px;
  padding: 4px 6px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  outline: none;
  text-align: center;
}
.expert-count-input:focus {
  border-color: var(--orange);
}
.expert-count-unit {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #999;
}

/* 增量调整区域 */
.expert-adjust {
  border-top: 1px solid var(--border);
  padding-top: 12px;
  margin-top: 4px;
}
.expert-count-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}
.expert-count-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #999;
  white-space: nowrap;
}
.expert-count-input {
  width: 50px;
  padding: 4px 6px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  outline: none;
  text-align: center;
}
.expert-count-input:focus {
  border-color: var(--orange);
}
.expert-count-unit {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #999;
}
/* 追加数量输入 */
.expert-input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 0.8rem;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 8px;
  line-height: 1.4;
}

/* 步骤导航（按钮同行） */
.step-nav {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 生成专家阵容按钮 */
.generate-experts-btn {
  width: 100%;
  padding: 12px;
  border: 1px dashed var(--orange);
  background: transparent;
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--orange);
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 6px;
  margin-bottom: 12px;
}
.generate-experts-btn:hover:not(:disabled) {
  background: rgba(255, 160, 0, 0.06);
  border-style: solid;
}
.generate-experts-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 工作流步骤 (压缩显示) */
.workflow-steps-compact {
  margin-top: 10px;
  font-size: 0.82rem;
}
.workflow-steps-compact .workflow-item {
  gap: 14px;
  margin-bottom: 10px;
}
.workflow-steps-compact .step-num {
  font-size: 0.75rem;
  opacity: 0.2;
}
.workflow-steps-compact .step-title {
  font-size: 0.85rem;
}
.workflow-steps-compact .step-desc {
  font-size: 0.75rem;
}

/* 项目模拟步骤介绍 */
.steps-container {
  border: 1px solid var(--border);
  padding: 30px;
  position: relative;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diamond-icon {
  font-size: 1.2rem;
  line-height: 1;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.workflow-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.step-num {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--black);
  opacity: 0.3;
}

.step-info {
  flex: 1;
}

.step-title {
  font-weight: 520;
  font-size: 1rem;
  margin-bottom: 4px;
}

.step-desc {
  font-size: 0.85rem;
  color: var(--gray-text);
}

/* 右侧交互控制台 */
.right-panel {
  flex: 1.2;
}

.console-box {
  border: 1px solid #CCC; /* 外部实线 */
  padding: 8px; /* 内边距形成双重边框感 */
}

.console-section {
  padding: 20px;
}

.console-section.btn-section {
  padding-top: 0;
}

.console-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #666;
}

.upload-zone {
  border: 1px dashed #CCC;
  height: 200px;
  overflow-y: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #FAFAFA;
}

.upload-zone.has-files {
  align-items: flex-start;
}

.upload-zone:hover {
  background: #F0F0F0;
  border-color: #999;
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  width: 40px;
  height: 40px;
  border: 1px solid #DDD;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  color: #999;
}

.upload-title {
  font-weight: 500;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.upload-hint {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: #999;
}

.file-list {
  width: 100%;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: flex;
  align-items: center;
  background: var(--white);
  padding: 8px 12px;
  border: 1px solid #EEE;
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.file-name {
  flex: 1;
  margin: 0 10px;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #999;
}

.console-divider {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #EEE;
}

.console-divider span {
  padding: 0 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #BBB;
  letter-spacing: 1px;
}

.input-wrapper {
  position: relative;
  border: 1px solid #DDD;
  background: #FAFAFA;
}

.code-input {
  width: 100%;
  border: none;
  background: transparent;
  padding: 20px;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  min-height: 150px;
}

.model-badge {
  position: absolute;
  bottom: 10px;
  right: 15px;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #AAA;
  cursor: default;
}

/* 常驻模型切换栏 */
.model-inline-form {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.model-inline-label {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: #999;
  white-space: nowrap;
}

.model-inline-input {
  flex: 1;
  min-width: 180px;
  padding: 5px 8px;
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 3px;
  color: #EEE;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  outline: none;
}

.model-inline-input:focus {
  border-color: var(--orange);
}

.model-switch-btn {
  padding: 5px 14px;
  background: #333;
  border: 1px solid #555;
  color: #CCC;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  cursor: pointer;
  border-radius: 3px;
  transition: all 0.2s;
  white-space: nowrap;
}

.model-switch-btn:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
  color: #FFF;
}

.model-switch-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.model-switch-msg {
  margin-top: 10px;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  padding: 6px 10px;
  border-radius: 4px;
  text-align: center;
}

.model-switch-msg.success {
  background: rgba(0,200,83,0.15);
  color: #69F0AE;
  border: 1px solid rgba(0,200,83,0.3);
}

.model-switch-msg.error {
  background: rgba(255,82,82,0.15);
  color: #FF8A80;
  border: 1px solid rgba(255,82,82,0.3);
}

.start-engine-btn {
  width: 100%;
  background: var(--black);
  color: var(--white);
  border: none;
  padding: 20px;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 1.1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
  position: relative;
  overflow: hidden;
}

/* 可点击状态（非禁用） */
.start-engine-btn:not(:disabled) {
  background: var(--black);
  border: 1px solid var(--black);
  animation: pulse-border 2s infinite;
}

.start-engine-btn:hover:not(:disabled) {
  background: var(--orange);
  border-color: var(--orange);
  transform: translateY(-2px);
}

.start-engine-btn:active:not(:disabled) {
  transform: translateY(0);
}

.start-engine-btn:disabled {
  background: #E5E5E5;
  color: #999;
  cursor: not-allowed;
  transform: none;
  border: 1px solid #E5E5E5;
}

/* 引导动画：微妙的边框脉冲 */
@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.2); }
  70% { box-shadow: 0 0 0 6px rgba(0, 0, 0, 0); }
  100% { box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); }
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .dashboard-section {
    flex-direction: column;
  }
}
</style>

<style>
/* English locale adjustments (unscoped to target html[lang]) */
html[lang="en"] .navbar .nav-links {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Left pane: system status + workflow */
html[lang="en"] .status-section {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .status-section .status-ready {
  font-size: 1.6rem;
}

html[lang="en"] .status-section .metric-value {
  font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 1.4rem;
}

html[lang="en"] .workflow-list .step-title {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

html[lang="en"] .workflow-list .step-desc {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  font-size: 0.72rem !important;
  line-height: 1.4 !important;
}

html[lang="en"] .workflow-list {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
