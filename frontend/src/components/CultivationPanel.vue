<template>
  <Transition name="overlay">
    <div v-if="visible" class="cultivation-overlay" @click.self="handleClose">
      <div class="cultivation-panel">
        <!-- 顶部栏 -->
        <div class="panel-topbar">
          <div class="topbar-left">
            <span class="topbar-icon">🧘</span>
            <span class="topbar-title">{{ $t('cultivation.title') }}</span>
            <span class="topbar-step">Step {{ currentStep }}/3</span>
          </div>
          <button class="close-btn" @click="handleClose">✕</button>
        </div>

        <!-- 进度条 -->
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          <span class="progress-text">{{ progressLabel }}</span>
        </div>

        <!-- Step 1: 基础事实 -->
        <Transition name="fade-slide" mode="out-in">
          <div v-if="currentStep === 1" key="step1" class="step-content">
            <div class="step-header">
              <div class="step-title">{{ $t('cultivation.step1Title') }}</div>
              <div class="step-subtitle">{{ $t('cultivation.step1Subtitle') }}</div>
            </div>

            <div class="form-grid">
              <!-- 出生日期 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.birthDate') }}</label>
                <input type="date" v-model="form.birthDate" class="field-input" />
                <span v-if="derived.zodiac" class="field-hint">♈ {{ derived.zodiac }}</span>
              </div>

              <!-- 出生时间 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.birthTime') }}</label>
                <input type="time" v-model="form.birthTime" class="field-input" />
                <span class="field-hint optional">{{ $t('cultivation.birthTimeHint') }}</span>
              </div>

              <!-- 血型 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.bloodType') }}</label>
                <select v-model="form.bloodType" class="field-select">
                  <option value="">{{ $t('cultivation.pleaseSelect') }}</option>
                  <option value="O">O</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="AB">AB</option>
                  <option value="unknown">{{ $t('cultivation.unknown') }}</option>
                </select>
              </div>

              <!-- 性别 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.gender') }}</label>
                <select v-model="form.gender" class="field-select">
                  <option value="">{{ $t('cultivation.pleaseSelect') }}</option>
                  <option value="male">{{ $t('cultivation.male') }}</option>
                  <option value="female">{{ $t('cultivation.female') }}</option>
                  <option value="undisclosed">{{ $t('cultivation.undisclosed') }}</option>
                </select>
              </div>

              <!-- 出生地 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.birthplace') }}</label>
                <input type="text" v-model="form.birthplace" class="field-input" :placeholder="$t('cultivation.birthplacePlaceholder')" />
              </div>

              <!-- 最高学历 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.education') }}</label>
                <select v-model="form.education" class="field-select">
                  <option value="">{{ $t('cultivation.pleaseSelect') }}</option>
                  <option value="junior">{{ $t('cultivation.juniorHigh') }}</option>
                  <option value="senior">{{ $t('cultivation.seniorHigh') }}</option>
                  <option value="college">{{ $t('cultivation.college') }}</option>
                  <option value="bachelor">{{ $t('cultivation.bachelor') }}</option>
                  <option value="master">{{ $t('cultivation.master') }}</option>
                  <option value="phd">{{ $t('cultivation.phd') }}</option>
                </select>
              </div>

              <!-- 当前职业 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.occupation') }}</label>
                <input type="text" v-model="form.occupation" class="field-input" :placeholder="$t('cultivation.occupationPlaceholder')" />
              </div>

              <!-- 婚姻状况 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.maritalStatus') }}</label>
                <select v-model="form.maritalStatus" class="field-select">
                  <option value="">{{ $t('cultivation.pleaseSelect') }}</option>
                  <option value="single">{{ $t('cultivation.single') }}</option>
                  <option value="married">{{ $t('cultivation.married') }}</option>
                  <option value="divorced">{{ $t('cultivation.divorced') }}</option>
                  <option value="widowed">{{ $t('cultivation.widowed') }}</option>
                  <option value="cohabiting">{{ $t('cultivation.cohabiting') }}</option>
                </select>
              </div>

              <!-- 子女数量 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.childrenCount') }}</label>
                <input type="number" v-model.number="form.childrenCount" class="field-input field-input-sm" min="0" max="10" />
              </div>

              <!-- 月收入范围 -->
              <div class="form-field">
                <label class="field-label">{{ $t('cultivation.incomeRange') }}</label>
                <select v-model="form.incomeRange" class="field-select">
                  <option value="">{{ $t('cultivation.pleaseSelect') }}</option>
                  <option value="under5k">{{ $t('cultivation.under5k') }}</option>
                  <option value="5k-10k">{{ $t('cultivation.5k-10k') }}</option>
                  <option value="10k-20k">{{ $t('cultivation.10k-20k') }}</option>
                  <option value="20k-50k">{{ $t('cultivation.20k-50k') }}</option>
                  <option value="over50k">{{ $t('cultivation.over50k') }}</option>
                  <option value="undisclosed">{{ $t('cultivation.undisclosed') }}</option>
                </select>
              </div>
            </div>

            <!-- Step 1 底部按钮 -->
            <div class="step-actions">
              <button class="action-btn ghost" @click="$emit('back')">{{ $t('cultivation.backToCards') }}</button>
              <button class="action-btn primary" @click="handleStep1Next" :disabled="!canStep1Next">
                🤖 {{ $t('cultivation.aiGuess') }}
              </button>
            </div>
          </div>

          <!-- Step 2: AI亮底牌 -->
          <div v-else-if="currentStep === 2" key="step2" class="step-content">
            <div class="step-header">
              <div class="step-title">{{ $t('cultivation.step2Title') }}</div>
              <div class="step-subtitle">{{ $t('cultivation.step2Subtitle') }}</div>
            </div>

            <div v-if="step2Loading" class="loading-area">
              <div class="loading-spinner-spin"></div>
              <div class="loading-text">{{ $t('cultivation.aiThinking') }}</div>
            </div>

            <div v-else class="guess-results">
              <!-- 客观推导项 -->
              <div v-if="step2Data.zodiac" class="guess-card locked">
                <div class="guess-card-header">
                  <span class="guess-card-icon">♈</span>
                  <span class="guess-card-title">{{ $t('cultivation.zodiac') }}</span>
                  <span class="locked-badge">{{ $t('cultivation.derived') }}</span>
                </div>
                <div class="guess-card-value">{{ step2Data.zodiac.value }}</div>
              </div>

              <!-- MBTI 推测 -->
              <div v-if="step2Data.mbti" class="guess-card">
                <div class="guess-card-header">
                  <span class="guess-card-icon">🧠</span>
                  <span class="guess-card-title">{{ $t('cultivation.mbti') }}</span>
                </div>
                <div class="guess-reasoning">
                  <div class="reasoning-title">{{ $t('cultivation.reasoning') }}：</div>
                  <ul class="reasoning-list">
                    <li v-for="(r, i) in step2Data.mbti.reasoning" :key="i">{{ r }}</li>
                  </ul>
                </div>
                <div class="edit-options">
                  <button
                    v-for="opt in step2Data.mbti.options"
                    :key="opt.type"
                    class="edit-option"
                    :class="{ selected: step2Data.mbti.userChoice === opt.type }"
                    @click="step2Data.mbti.userChoice = opt.type"
                  >
                    <span class="edit-opt-name">{{ opt.type }} - {{ getMbtiName(opt.type) }}</span>
                    <span class="edit-opt-desc">{{ (opt.p * 100).toFixed(0) }}% · {{ opt.reason }}</span>
                  </button>
                </div>
                <div class="mbti-alt-actions">
                  <button class="alt-btn" @click="step2Data.mbti.userChoice = 'self-select'">
                    {{ $t('cultivation.iKnowMyself') }}
                  </button>
                  <select v-if="step2Data.mbti.userChoice === 'self-select'" v-model="step2Data.mbti.selfSelected" class="field-select mbti-select">
                    <option v-for="t in MBTI_TYPES" :key="t" :value="t">{{ t }} - {{ getMbtiName(t) }}</option>
                  </select>
                  <a href="https://www.16personalities.com/free-personality-test" target="_blank" class="alt-btn link">
                    {{ $t('cultivation.takeTest') }} ↗
                  </a>
                  <button class="alt-btn" @click="step2Data.mbti.userChoice = 'undecided'">
                    {{ $t('cultivation.undecided') }}
                  </button>
                </div>
              </div>

              <!-- 大五人格 -->
              <div v-if="step2Data.bigFive" class="guess-card">
                <div class="guess-card-header">
                  <span class="guess-card-icon">📊</span>
                  <span class="guess-card-title">{{ $t('cultivation.bigFive') }}</span>
                  <span class="confidence-badge">{{ (step2Data.bigFive.confidence * 100).toFixed(0) }}%</span>
                </div>
                <div class="card-detail">
                  <div class="current-value">
                    <span class="value-label">AI推测：</span>
                    <span class="value-name">{{ getBigFiveName(step2Data.bigFive.value) }}</span>
                  </div>
                  <div class="option-desc">{{ getBigFiveDesc(step2Data.bigFive.value) }}</div>
                  <div class="option-reason">💡 {{ getBigFiveReason(step2Data.bigFive.value) }}</div>
                  <div class="option-actions">
                    <button class="mini-btn" @click="step2Data.bigFive.confirmed = true">✓ {{ $t('cultivation.confirm') }}</button>
                    <button class="mini-btn outline" @click="step2Data.bigFive.editing = true">✗ {{ $t('cultivation.modify') }}</button>
                  </div>
                  <div v-if="step2Data.bigFive.editing" class="edit-area">
                    <div class="edit-options">
                      <button
                        v-for="opt in BIG_FIVE_OPTIONS"
                        :key="opt"
                        class="edit-option"
                        :class="{ selected: step2Data.bigFive.value === opt }"
                        @click="step2Data.bigFive.value = opt; step2Data.bigFive.editing = false"
                      >
                        <span class="edit-opt-name">{{ getBigFiveName(opt) }}</span>
                        <span class="edit-opt-desc">{{ getBigFiveShortDesc(opt) }}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 昼夜节律 -->
              <div v-if="step2Data.chronotype" class="guess-card">
                <div class="guess-card-header">
                  <span class="guess-card-icon">⏰</span>
                  <span class="guess-card-title">{{ $t('cultivation.chronotype') }}</span>
                  <span class="confidence-badge">{{ (step2Data.chronotype.confidence * 100).toFixed(0) }}%</span>
                </div>
                <div class="card-detail">
                  <div class="current-value">
                    <span class="value-label">AI推测：</span>
                    <span class="value-name">{{ getChronotypeName(step2Data.chronotype.value) }}</span>
                  </div>
                  <div class="option-desc">{{ getChronotypeDesc(step2Data.chronotype.value) }}</div>
                  <div class="option-reason">💡 {{ getChronotypeReason(step2Data.chronotype.value) }}</div>
                  <div class="option-actions">
                    <button class="mini-btn" @click="step2Data.chronotype.confirmed = true">✓ {{ $t('cultivation.confirm') }}</button>
                    <button class="mini-btn outline" @click="step2Data.chronotype.editing = true">✗ {{ $t('cultivation.modify') }}</button>
                  </div>
                  <div v-if="step2Data.chronotype.editing" class="edit-area">
                    <div class="edit-options">
                      <button
                        v-for="opt in CHRONOTYPE_OPTIONS"
                        :key="opt"
                        class="edit-option"
                        :class="{ selected: step2Data.chronotype.value === opt }"
                        @click="step2Data.chronotype.value = opt; step2Data.chronotype.editing = false"
                      >
                        <span class="edit-opt-name">{{ getChronotypeName(opt) }}</span>
                        <span class="edit-opt-desc">{{ getChronotypeDesc(opt).slice(0, 30) }}...</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 身体健康基线 -->
              <div v-if="step2Data.healthBaseline" class="guess-card uncertain">
                <div class="guess-card-header">
                  <span class="guess-card-icon">💪</span>
                  <span class="guess-card-title">{{ $t('cultivation.healthBaseline') }}</span>
                  <span class="uncertain-badge">{{ $t('cultivation.aiUncertain') }}</span>
                </div>
                <div class="card-detail">
                  <div class="ai-note">{{ step2Data.healthBaseline.aiNote }}</div>
                  <div class="current-value">
                    <span class="value-label">AI参考：</span>
                    <span class="value-name">{{ getHealthName(step2Data.healthBaseline.value) }}</span>
                  </div>
                  <div class="option-desc">{{ getHealthDesc(step2Data.healthBaseline.value) }}</div>
                  <div class="option-reason">💡 {{ getHealthReason(step2Data.healthBaseline.value) }}</div>
                  <div class="option-actions">
                    <button class="mini-btn" @click="step2Data.healthBaseline.confirmed = true">{{ $t('cultivation.basicFit') }}</button>
                    <button class="mini-btn outline" @click="step2Data.healthBaseline.editing = true">{{ $t('cultivation.someDifferent') }}</button>
                    <button class="mini-btn ghost" @click="step2Data.healthBaseline.confirmed = 'skip'">{{ $t('cultivation.skipForNow') }}</button>
                  </div>
                  <div v-if="step2Data.healthBaseline.editing" class="edit-area">
                    <div class="edit-options">
                      <button
                        v-for="opt in HEALTH_OPTIONS"
                        :key="opt"
                        class="edit-option"
                        :class="{ selected: step2Data.healthBaseline.value === opt }"
                        @click="step2Data.healthBaseline.value = opt; step2Data.healthBaseline.editing = false"
                      >
                        <span class="edit-opt-name">{{ getHealthName(opt) }}</span>
                        <span class="edit-opt-desc">{{ getHealthDesc(opt).slice(0, 30) }}...</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 心理能量水平 -->
              <div v-if="step2Data.mentalEnergy" class="guess-card uncertain">
                <div class="guess-card-header">
                  <span class="guess-card-icon">🧘</span>
                  <span class="guess-card-title">{{ $t('cultivation.mentalEnergy') }}</span>
                  <span class="uncertain-badge">{{ $t('cultivation.aiUncertain') }}</span>
                </div>
                <div class="card-detail">
                  <div class="ai-note">{{ step2Data.mentalEnergy.aiNote }}</div>
                  <div class="current-value">
                    <span class="value-label">AI参考：</span>
                    <span class="value-name">{{ getMentalEnergyName(step2Data.mentalEnergy.value) }}</span>
                  </div>
                  <div class="option-desc">{{ getMentalEnergyDesc(step2Data.mentalEnergy.value) }}</div>
                  <div class="option-reason">💡 {{ getMentalEnergyReason(step2Data.mentalEnergy.value) }}</div>
                  <div class="option-actions">
                    <button class="mini-btn" @click="step2Data.mentalEnergy.confirmed = true">{{ $t('cultivation.basicFit') }}</button>
                    <button class="mini-btn outline" @click="step2Data.mentalEnergy.editing = true">{{ $t('cultivation.someDifferent') }}</button>
                    <button class="mini-btn ghost" @click="step2Data.mentalEnergy.confirmed = 'skip'">{{ $t('cultivation.skipForNow') }}</button>
                  </div>
                  <div v-if="step2Data.mentalEnergy.editing" class="edit-area">
                    <div class="edit-options">
                      <button
                        v-for="opt in MENTAL_ENERGY_OPTIONS"
                        :key="opt"
                        class="edit-option"
                        :class="{ selected: step2Data.mentalEnergy.value === opt }"
                        @click="step2Data.mentalEnergy.value = opt; step2Data.mentalEnergy.editing = false"
                      >
                        <span class="edit-opt-name">{{ getMentalEnergyName(opt) }}</span>
                        <span class="edit-opt-desc">{{ getMentalEnergyDesc(opt).slice(0, 30) }}...</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 决策风格 -->
              <div v-if="step2Data.decisionStyle" class="guess-card">
                <div class="guess-card-header">
                  <span class="guess-card-icon">⚡</span>
                  <span class="guess-card-title">{{ $t('cultivation.decisionStyle') }}</span>
                  <span class="confidence-badge">{{ (step2Data.decisionStyle.confidence * 100).toFixed(0) }}%</span>
                </div>
                <div class="card-detail">
                  <div class="current-value">
                    <span class="value-label">AI推测：</span>
                    <span class="value-name">{{ getDecisionName(step2Data.decisionStyle.value) }}</span>
                  </div>
                  <div class="option-desc">{{ getDecisionDesc(step2Data.decisionStyle.value) }}</div>
                  <div class="option-reason">💡 {{ getDecisionReason(step2Data.decisionStyle.value) }}</div>
                  <div class="option-actions">
                    <button class="mini-btn" @click="step2Data.decisionStyle.confirmed = true">✓ {{ $t('cultivation.confirm') }}</button>
                    <button class="mini-btn outline" @click="step2Data.decisionStyle.editing = true">✗ {{ $t('cultivation.modify') }}</button>
                  </div>
                  <div v-if="step2Data.decisionStyle.editing" class="edit-area">
                    <div class="edit-options">
                      <button
                        v-for="opt in DECISION_STYLE_OPTIONS"
                        :key="opt"
                        class="edit-option"
                        :class="{ selected: step2Data.decisionStyle.value === opt }"
                        @click="step2Data.decisionStyle.value = opt; step2Data.decisionStyle.editing = false"
                      >
                        <span class="edit-opt-name">{{ getDecisionName(opt) }}</span>
                        <span class="edit-opt-desc">{{ getDecisionDesc(opt).slice(0, 30) }}...</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 人际互动模式 -->
              <div v-if="step2Data.interactionPattern" class="guess-card">
                <div class="guess-card-header">
                  <span class="guess-card-icon">🤝</span>
                  <span class="guess-card-title">{{ $t('cultivation.interactionPattern') }}</span>
                  <span class="confidence-badge">{{ (step2Data.interactionPattern.confidence * 100).toFixed(0) }}%</span>
                </div>
                <div class="card-detail">
                  <div class="current-value">
                    <span class="value-label">AI推测：</span>
                    <span class="value-name">{{ getInteractionName(step2Data.interactionPattern.value) }}</span>
                  </div>
                  <div class="option-desc">{{ getInteractionDesc(step2Data.interactionPattern.value) }}</div>
                  <div class="option-reason">💡 {{ getInteractionReason(step2Data.interactionPattern.value) }}</div>
                  <div class="option-actions">
                    <button class="mini-btn" @click="step2Data.interactionPattern.confirmed = true">✓ {{ $t('cultivation.confirm') }}</button>
                    <button class="mini-btn outline" @click="step2Data.interactionPattern.editing = true">✗ {{ $t('cultivation.modify') }}</button>
                  </div>
                  <div v-if="step2Data.interactionPattern.editing" class="edit-area">
                    <div class="edit-options">
                      <button
                        v-for="opt in INTERACTION_OPTIONS"
                        :key="opt"
                        class="edit-option"
                        :class="{ selected: step2Data.interactionPattern.value === opt }"
                        @click="step2Data.interactionPattern.value = opt; step2Data.interactionPattern.editing = false"
                      >
                        <span class="edit-opt-name">{{ getInteractionName(opt) }}</span>
                        <span class="edit-opt-desc">{{ getInteractionDesc(opt).slice(0, 30) }}...</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 2 底部按钮 -->
            <div class="step-actions">
              <button class="action-btn ghost" @click="currentStep = 1">⬅ {{ $t('cultivation.prevStep') }}</button>
              <button class="action-btn primary" @click="handleStep2Next">
                {{ $t('cultivation.continueRefine') }} →
              </button>
            </div>
          </div>

          <!-- Step 3: AI深猜 + 用户精修 -->
          <div v-else-if="currentStep === 3" key="step3" class="step-content">
            <div class="step-header">
              <div class="step-title">{{ $t('cultivation.step3Title') }}</div>
              <div class="step-subtitle">{{ $t('cultivation.step3Subtitle') }}</div>
            </div>

            <div v-if="step3Loading" class="loading-area">
              <div class="loading-spinner-spin"></div>
              <div class="loading-text">{{ $t('cultivation.aiDeepThinking') }}</div>
            </div>

            <div v-else class="categories-area">
              <!-- 进度统计 -->
              <div class="completion-stats">
                <div class="stats-bar">
                  <div class="stats-fill" :style="{ width: completionPercent + '%' }"></div>
                </div>
                <span class="stats-text">{{ $t('cultivation.completedItems', { done: completedCount, total: totalCount }) }}</span>
              </div>

              <!-- 5个大类折叠卡片 -->
              <div class="category-list">
                <div
                  v-for="(cat, catIdx) in categories"
                  :key="cat.id"
                  class="category-card"
                  :class="{ expanded: cat.expanded, partially: isPartiallyChecked(cat) }"
                >
                  <div class="category-header" @click="cat.expanded = !cat.expanded">
                    <div class="cat-header-left">
                      <span class="cat-icon">{{ cat.icon }}</span>
                      <span class="cat-name">{{ cat.name }}</span>
                      <span class="cat-count">{{ getCatCompletedCount(cat) }}/{{ cat.items.length }}</span>
                    </div>
                    <div class="cat-header-right">
                      <label class="cat-check-all" @click.stop>
                        <input type="checkbox" :checked="isAllChecked(cat)" @change="toggleCatAll(cat, $event.target.checked)" />
                        <span>{{ $t('cultivation.checkAll') }}</span>
                      </label>
                      <span class="expand-arrow">{{ cat.expanded ? '▲' : '▼' }}</span>
                    </div>
                  </div>

                  <Transition name="expand">
                    <div v-if="cat.expanded" class="category-body">
                      <div
                        v-for="(item, itemIdx) in cat.items"
                        :key="item.id"
                        class="item-row"
                        :class="{ checked: item.checked, unchecked: !item.checked, editing: item.editing, expanded: expandedItem === item.id }"
                        :style="{ animationDelay: (itemIdx * 30) + 'ms' }"
                      >
                        <label class="item-check">
                          <input type="checkbox" v-model="item.checked" />
                        </label>
                        <div class="item-content" @click="toggleItemExpand(item.id)">
                          <div class="item-label">{{ item.label }}</div>
                          <div class="item-value" v-if="!item.editing">
                            {{ item.value }}
                            <span class="confidence-dots" :title="'置信度: ' + (item.confidence * 100).toFixed(0) + '%'">
                              <span v-for="n in 5" :key="n" class="dot" :class="{ active: n <= Math.round(item.confidence * 5) }"></span>
                            </span>
                          </div>
                          <div class="item-edit" v-else @click.stop>
                            <div v-if="item.options && item.options.length" class="edit-options-vertical">
                              <button
                                v-for="opt in item.options"
                                :key="opt"
                                class="edit-option"
                                :class="{ selected: item.value === opt }"
                                @click="item.value = opt"
                              >
                                {{ opt }}
                              </button>
                            </div>
                            <input v-else type="text" v-model="item.value" class="field-input item-input" />
                          </div>
                          <Transition name="expand">
                            <div v-if="expandedItem === item.id && !item.editing" class="item-reason">
                              <div class="reason-text">💡 {{ item.reason || 'AI基于你的整体信息推测此选项' }}</div>
                            </div>
                          </Transition>
                        </div>
                        <div class="item-actions" v-if="!item.editing">
                          <button class="icon-btn confirm" @click.stop="item.checked = true" :title="$t('cultivation.confirm')">✓</button>
                          <button class="icon-btn edit" @click.stop="item.editing = true" :title="$t('cultivation.modify')">✎</button>
                        </div>
                        <div class="item-actions" v-else>
                          <button class="icon-btn save" @click.stop="item.editing = false" :title="$t('cultivation.save')">✓</button>
                          <button class="icon-btn cancel" @click.stop="item.editing = false" :title="$t('cultivation.cancel')">✕</button>
                        </div>
                      </div>
                    </div>
                  </Transition>
                </div>
              </div>

              <!-- 追加类型 -->
              <div class="custom-add-area">
                <button class="add-custom-btn" @click="showCustomAdd = !showCustomAdd">
                  ➕ {{ $t('cultivation.addCustomType') }}
                </button>
                <Transition name="expand">
                  <div v-if="showCustomAdd" class="custom-add-form">
                    <input type="text" v-model="customInput" class="field-input" :placeholder="$t('cultivation.customPlaceholder')" @keyup.enter="addCustomItem" />
                    <button class="mini-btn" @click="addCustomItem">{{ $t('cultivation.add') }}</button>
                  </div>
                </Transition>
                <div v-if="customItems.length" class="custom-items-list">
                  <div v-for="(ci, i) in customItems" :key="i" class="custom-item">
                    <span class="custom-label">{{ ci.label }}</span>
                    <span class="custom-value">{{ ci.value }}</span>
                    <button class="icon-btn cancel" @click="customItems.splice(i, 1)">✕</button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Step 3 底部按钮 -->
            <div class="step-actions">
              <button class="action-btn ghost" @click="currentStep = 2">⬅ {{ $t('cultivation.prevStep') }}</button>
              <button class="action-btn primary" @click="handleComplete">
                ✅ {{ $t('cultivation.completeCultivation') }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import PSYCHOLOGY_KNOWLEDGE_BASE from '../data/psychologyKnowledgeBase.js'
import { guessStep2, guessStep3 } from '../api/cultivation'

const props = defineProps({
  visible: { type: Boolean, default: false },
  realitySeedFiles: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'back', 'complete'])

// ========== 常量 ==========
const MBTI_TYPES = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']
const BIG_FIVE_OPTIONS = ['高外向性','低外向性','高宜人性','低宜人性','高尽责性','低尽责性','高神经质','低神经质','高开放性','低开放性','均衡型']
const CHRONOTYPE_OPTIONS = ['晨型(云雀)','夜型(猫头鹰)','中间型','不规律型']
const HEALTH_OPTIONS = ['非常健康','基本健康','亚健康','有慢性疾病','正在恢复中']
const MENTAL_ENERGY_OPTIONS = ['精力充沛','状态良好','中等水平','容易疲劳','长期倦怠']
const DECISION_STYLE_OPTIONS = ['理性分析型','直觉冲动型','谨慎犹豫型','从众依赖型','独立果断型','回避拖延型']
const INTERACTION_OPTIONS = ['安全型依恋','焦虑型依恋','回避型依恋','混乱型依恋','外向社交型','内向独立型','选择性社交']

// ========== 状态 ==========
const currentStep = ref(1)
const step2Loading = ref(false)
const step3Loading = ref(false)
const showCustomAdd = ref(false)
const customInput = ref('')

// Step 1 表单
const form = reactive({
  birthDate: '',
  birthTime: '',
  bloodType: '',
  gender: '',
  birthplace: '',
  education: '',
  occupation: '',
  maritalStatus: '',
  childrenCount: 0,
  incomeRange: ''
})

// 星座推导
const ZODIAC_SIGNS = [
  { name: '摩羯座', start: [1, 1], end: [1, 19] },
  { name: '水瓶座', start: [1, 20], end: [2, 18] },
  { name: '双鱼座', start: [2, 19], end: [3, 20] },
  { name: '白羊座', start: [3, 21], end: [4, 19] },
  { name: '金牛座', start: [4, 20], end: [5, 20] },
  { name: '双子座', start: [5, 21], end: [6, 21] },
  { name: '巨蟹座', start: [6, 22], end: [7, 22] },
  { name: '狮子座', start: [7, 23], end: [8, 22] },
  { name: '处女座', start: [8, 23], end: [9, 22] },
  { name: '天秤座', start: [9, 23], end: [10, 23] },
  { name: '天蝎座', start: [10, 24], end: [11, 22] },
  { name: '射手座', start: [11, 23], end: [12, 21] },
  { name: '摩羯座', start: [12, 22], end: [12, 31] }
]

const derived = computed(() => {
  const result = { zodiac: '' }
  if (form.birthDate) {
    const d = new Date(form.birthDate)
    const m = d.getMonth() + 1
    const day = d.getDate()
    for (const z of ZODIAC_SIGNS) {
      const [sm, sd] = z.start
      const [em, ed] = z.end
      if ((m === sm && day >= sd) || (m === em && day <= ed)) {
        result.zodiac = z.name
        break
      }
    }
  }
  return result
})

// Step 1 是否可以下一步

// ========== 知识库辅助方法 ==========
const _fillTemplate = (tmpl) => {
  if (!tmpl) return ''
  return tmpl
    .replace(/{occupation}/g, form.occupation || '你的职业')
    .replace(/{education}/g, form.education || '你的学历')
    .replace(/{age}/g, String(age.value || 0))
    .replace(/{blood_type}/g, form.bloodType || '未知')
    .replace(/{zodiac}/g, derived.value.zodiac || '未知')
    .replace(/{gender}/g, form.gender || '未知')
    .replace(/{marital_status}/g, form.maritalStatus || '未知')
    .replace(/{income_range}/g, form.incomeRange || '未知')
    .replace(/{children_count}/g, String(form.childrenCount || 0))
}

// MBTI
const getMbtiName = (type) => PSYCHOLOGY_KNOWLEDGE_BASE.mbti[type]?.name || type
const getMbtiDesc = (type) => PSYCHOLOGY_KNOWLEDGE_BASE.mbti[type]?.description || ''
const getMbtiTraits = (type) => PSYCHOLOGY_KNOWLEDGE_BASE.mbti[type]?.traits || []
const getMbtiReason = (type) => _fillTemplate(PSYCHOLOGY_KNOWLEDGE_BASE.mbti[type]?.aiReasonTemplate)

// 大五人格
const getBigFiveName = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.bigFive[val]?.name || val
const getBigFiveDesc = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.bigFive[val]?.description || ''
const getBigFiveShortDesc = (val) => {
  const desc = PSYCHOLOGY_KNOWLEDGE_BASE.bigFive[val]?.description || ''
  return desc.length > 30 ? desc.slice(0, 30) + '...' : desc
}
const getBigFiveReason = (val) => _fillTemplate(PSYCHOLOGY_KNOWLEDGE_BASE.bigFive[val]?.aiReasonTemplate)

// 昼夜节律
const getChronotypeName = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.chronotype[val]?.name || val
const getChronotypeDesc = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.chronotype[val]?.description || ''
const getChronotypeReason = (val) => _fillTemplate(PSYCHOLOGY_KNOWLEDGE_BASE.chronotype[val]?.aiReasonTemplate)

// 身体健康
const getHealthName = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.healthBaseline[val]?.name || val
const getHealthDesc = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.healthBaseline[val]?.description || ''
const getHealthReason = (val) => _fillTemplate(PSYCHOLOGY_KNOWLEDGE_BASE.healthBaseline[val]?.aiReasonTemplate)

// 心理能量
const getMentalEnergyName = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.mentalEnergy[val]?.name || val
const getMentalEnergyDesc = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.mentalEnergy[val]?.description || ''
const getMentalEnergyReason = (val) => _fillTemplate(PSYCHOLOGY_KNOWLEDGE_BASE.mentalEnergy[val]?.aiReasonTemplate)

// 决策风格
const getDecisionName = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.decisionStyle[val]?.name || val
const getDecisionDesc = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.decisionStyle[val]?.description || ''
const getDecisionReason = (val) => _fillTemplate(PSYCHOLOGY_KNOWLEDGE_BASE.decisionStyle[val]?.aiReasonTemplate)

// 人际互动
const getInteractionName = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.interactionPattern[val]?.name || val
const getInteractionDesc = (val) => PSYCHOLOGY_KNOWLEDGE_BASE.interactionPattern[val]?.description || ''
const getInteractionReason = (val) => _fillTemplate(PSYCHOLOGY_KNOWLEDGE_BASE.interactionPattern[val]?.aiReasonTemplate)

// 展开/收拢状态
const expandedItem = ref(null)

const toggleItemExpand = (id) => { expandedItem.value = expandedItem.value === id ? null : id }

// 计算年龄
const age = computed(() => {
  if (!form.birthDate) return 0
  const d = new Date(form.birthDate)
  const now = new Date()
  return now.getFullYear() - d.getFullYear() - ((now.getMonth(), now.getDate()) < (d.getMonth(), d.getDate()))
})

const canStep1Next = computed(() => {
  return form.birthDate && form.bloodType && form.gender && form.education && form.occupation && form.maritalStatus && form.incomeRange
})

// Step 2 数据
const step2Data = reactive({
  zodiac: null,
  mbti: null,
  bigFive: null,
  chronotype: null,
  healthBaseline: null,
  mentalEnergy: null,
  decisionStyle: null,
  interactionPattern: null
})

// Step 3 数据
const categories = ref([])
const customItems = ref([])

// ========== 进度 ==========
const progressPercent = computed(() => {
  if (currentStep.value === 1) return 33
  if (currentStep.value === 2) return 66
  return 100
})

const progressLabel = computed(() => {
  if (currentStep.value === 1) return 'Step 1/3 - ' + '基础事实'
  if (currentStep.value === 2) return 'Step 2/3 - ' + 'AI亮底牌'
  return 'Step 3/3 - ' + 'AI深猜+精修'
})

const totalCount = computed(() => categories.value.reduce((s, c) => s + c.items.length, 0))
const completedCount = computed(() => categories.value.reduce((s, c) => s + c.items.filter(i => i.checked).length, 0))
const completionPercent = computed(() => {
  const total = totalCount.value
  return total > 0 ? (completedCount.value / total) * 100 : 0
})

// ========== 方法 ==========
const handleClose = () => emit('close')

const getCatCompletedCount = (cat) => cat.items.filter(i => i.checked).length
const isAllChecked = (cat) => cat.items.every(i => i.checked)
const isPartiallyChecked = (cat) => {
  const checked = cat.items.filter(i => i.checked).length
  return checked > 0 && checked < cat.items.length
}
const toggleCatAll = (cat, checked) => cat.items.forEach(i => i.checked = checked)

// Step 1 → Step 2
const handleStep1Next = async () => {
  if (!canStep1Next.value) return
  currentStep.value = 2
  step2Loading.value = true

  try {
    // 调用后端 API
    const res = await guessStep2({
      birthDate: form.birthDate,
      bloodType: form.bloodType,
      gender: form.gender,
      birthplace: form.birthplace,
      education: form.education,
      occupation: form.occupation,
      maritalStatus: form.maritalStatus,
      childrenCount: form.childrenCount,
      incomeRange: form.incomeRange,
      zodiac: derived.value.zodiac
    })

    if (res.success && res.data) {
      const d = res.data
      step2Data.zodiac = d.zodiac ? { value: d.zodiac, locked: true } : null
      step2Data.mbti = d.mbti || null
      step2Data.bigFive = d.bigFive ? { ...d.bigFive, confirmed: false, editing: false } : null
      step2Data.chronotype = d.chronotype ? { ...d.chronotype, confirmed: false, editing: false } : null
      step2Data.healthBaseline = d.healthBaseline ? { ...d.healthBaseline, confirmed: false, editing: false } : null
      step2Data.mentalEnergy = d.mentalEnergy ? { ...d.mentalEnergy, confirmed: false, editing: false } : null
      step2Data.decisionStyle = d.decisionStyle ? { ...d.decisionStyle, confirmed: false, editing: false } : null
      step2Data.interactionPattern = d.interactionPattern ? { ...d.interactionPattern, confirmed: false, editing: false } : null
    }
  } catch (e) {
    console.error('Step2 API error:', e)
    // 降级：使用本地默认值
    applyLocalStep2Defaults()
  } finally {
    step2Loading.value = false
  }
}

// Step 2 → Step 3
const handleStep2Next = async () => {
  currentStep.value = 3
  step3Loading.value = true

  try {
    const res = await guessStep3({
      step1: { ...form, zodiac: derived.value.zodiac },
      step2: {
        mbti: step2Data.mbti?.userChoice === 'self-select' ? step2Data.mbti?.selfSelected : (step2Data.mbti?.userChoice || step2Data.mbti?.options?.[0]?.type),
        bigFive: step2Data.bigFive?.value,
        chronotype: step2Data.chronotype?.value,
        healthBaseline: step2Data.healthBaseline?.confirmed === 'skip' ? null : step2Data.healthBaseline?.value,
        mentalEnergy: step2Data.mentalEnergy?.confirmed === 'skip' ? null : step2Data.mentalEnergy?.value,
        decisionStyle: step2Data.decisionStyle?.value,
        interactionPattern: step2Data.interactionPattern?.value
      }
    })

    if (res.success && res.data?.categories) {
      categories.value = res.data.categories.map(c => ({
        ...c,
        expanded: false,
        items: c.items.map(i => ({ ...i, checked: true, editing: false }))
      }))
    } else {
      applyLocalStep3Defaults()
    }
  } catch (e) {
    console.error('Step3 API error:', e)
    applyLocalStep3Defaults()
  } finally {
    step3Loading.value = false
  }
}

// 本地降级默认值
const applyLocalStep2Defaults = () => {
  step2Data.zodiac = { value: derived.value.zodiac, locked: true }
  step2Data.mbti = {
    options: [{ type: 'ISTJ', p: 0.35 }, { type: 'INTJ', p: 0.28 }, { type: 'ISFJ', p: 0.20 }],
    reasoning: ['基于星座和血型统计分布', '职业特征分析', '教育背景推断'],
    userChoice: null,
    selfSelected: ''
  }
  step2Data.bigFive = { value: '均衡型', confidence: 0.5, confirmed: false, editing: false }
  step2Data.chronotype = { value: '中间型', confidence: 0.4, confirmed: false, editing: false }
  step2Data.healthBaseline = { value: '基本健康', confidence: 0.3, aiNote: 'AI无法准确推测你的身体健康状况，30岁/技术岗位的常见模式仅供参考', confirmed: false, editing: false }
  step2Data.mentalEnergy = { value: '中等水平', confidence: 0.3, aiNote: 'AI无法准确推测你的心理能量水平，基于年龄和职业的参考', confirmed: false, editing: false }
  step2Data.decisionStyle = { value: '理性分析型', confidence: 0.55, confirmed: false, editing: false }
  step2Data.interactionPattern = { value: '安全型依恋', confidence: 0.45, confirmed: false, editing: false }
}

const applyLocalStep3Defaults = () => {
  categories.value = buildDefaultCategories()
}

// 完成修身
const handleComplete = () => {
  const md = generateMarkdown()
  const fileName = `修身_${Date.now()}.md`
  emit('complete', { markdown: md, fileName })
}

// 追加自定义项
const addCustomItem = () => {
  if (!customInput.value.trim()) return
  customItems.value.push({ label: '自定义', value: customInput.value.trim() })
  customInput.value = ''
}

// 生成 Markdown
const generateMarkdown = () => {
  const lines = ['# 修身 · 个人情况分析\n']

  // Step 1
  lines.push('## 基础事实\n')
  if (form.birthDate) lines.push(`- 出生日期：${form.birthDate}（${derived.value.zodiac}）`)
  if (form.bloodType) lines.push(`- 血型：${form.bloodType === 'unknown' ? '未知' : form.bloodType}`)
  if (form.gender) lines.push(`- 性别：${form.gender === 'male' ? '男' : form.gender === 'female' ? '女' : '不愿透露'}`)
  if (form.birthplace) lines.push(`- 出生地：${form.birthplace}`)
  if (form.education) lines.push(`- 最高学历：${form.education}`)
  if (form.occupation) lines.push(`- 当前职业：${form.occupation}`)
  if (form.maritalStatus) lines.push(`- 婚姻状况：${form.maritalStatus}`)
  lines.push(`- 子女数量：${form.childrenCount}`)
  if (form.incomeRange) lines.push(`- 月收入范围：${form.incomeRange}`)
  lines.push('')

  // Step 3 分类数据
  for (const cat of categories.value) {
    const checkedItems = cat.items.filter(i => i.checked)
    if (checkedItems.length === 0) continue
    lines.push(`## ${cat.name}\n`)
    for (const item of checkedItems) {
      lines.push(`- **${item.label}**：${item.value}`)
    }
    lines.push('')
  }

  // 自定义项
  if (customItems.value.length) {
    lines.push('## 自定义补充\n')
    for (const ci of customItems.value) {
      lines.push(`- **${ci.label}**：${ci.value}`)
    }
    lines.push('')
  }

  return lines.join('\n')
}

// 构建默认分类数据（本地降级用）
const buildDefaultCategories = () => {
  return [
    {
      id: 'life-foundation', name: '生命根基', icon: '🌱', expanded: false,
      items: [
        { id: 'family-structure', label: '原生家庭结构', value: '双亲家庭', confidence: 0.7, checked: true, options: ['单亲家庭','双亲家庭','隔代抚养','重组家庭','其他'], editing: false },
        { id: 'family-economy', label: '家庭经济状况', value: '工薪阶层', confidence: 0.6, checked: true, options: ['贫困','工薪阶层','中产','富裕'], editing: false },
        { id: 'family-education', label: '家庭教育风格', value: '民主型', confidence: 0.5, checked: true, options: ['专制型','民主型','放任型','忽视型'], editing: false },
        { id: 'family-culture', label: '家族文化传承', value: '重视教育', confidence: 0.5, checked: true, options: ['重视教育','重视经商','重视手艺','无明显传承'], editing: false },
        { id: 'family-events', label: '重要家庭变故', value: '无明显变故', confidence: 0.4, checked: true, options: ['父母离异','亲人去世','家庭搬迁','移民','无明显变故'], editing: false },
        { id: 'growth-region', label: '成长地域轨迹', value: '城市成长', confidence: 0.6, checked: true, options: ['农村成长','小城镇','城市成长','多地迁徙'], editing: false },
        { id: 'education-path', label: '教育塑造历程', value: '本科', confidence: 0.8, checked: true, options: ['初中','高中','大专','本科','硕士','博士'], editing: false },
        { id: 'early-events', label: '早期重大事件', value: '无明显事件', confidence: 0.3, checked: true, options: [], editing: false },
        { id: 'generational', label: '代际传承印记', value: '无明显传承', confidence: 0.3, checked: true, options: [], editing: false },
        { id: 'cultural-adapt', label: '文化适应经历', value: '无显著适应', confidence: 0.4, checked: true, options: [], editing: false }
      ]
    },
    {
      id: 'social-existence', name: '社会存在', icon: '🏛️', expanded: false,
      items: [
        { id: 'career-identity', label: '职业身份定位', value: form.occupation || '专业人士', confidence: 0.8, checked: true, options: [], editing: false },
        { id: 'economic-resource', label: '经济资源状况', value: form.incomeRange || '中等收入', confidence: 0.7, checked: true, options: [], editing: false },
        { id: 'social-network', label: '社会关系网络', value: '中等规模', confidence: 0.4, checked: true, options: ['广泛','中等规模','较小','极小'], editing: false },
        { id: 'class-perception', label: '社会阶层感知', value: '中产', confidence: 0.5, checked: true, options: ['底层','工薪','中产','上层'], editing: false },
        { id: 'public-participation', label: '公共参与程度', value: '低', confidence: 0.4, checked: true, options: ['高','中','低','无'], editing: false },
        { id: 'career-satisfaction', label: '职业满意度', value: '中等', confidence: 0.4, checked: true, options: ['非常满意','比较满意','中等','不太满意','很不满意'], editing: false },
        { id: 'career-relations', label: '职业人际关系', value: '良好', confidence: 0.5, checked: true, options: ['非常紧张','有些紧张','一般','良好','非常好'], editing: false },
        { id: 'career-plan', label: '职业发展规划', value: '稳步发展', confidence: 0.4, checked: true, options: ['晋升','转行','创业','维持现状','不确定'], editing: false },
        { id: 'social-support', label: '社会支持度', value: '中等', confidence: 0.4, checked: true, options: ['强','中等','弱'], editing: false },
        { id: 'class-mobility', label: '阶层流动经历', value: '向上流动', confidence: 0.4, checked: true, options: ['向上流动','向下流动','稳定','波动'], editing: false }
      ]
    },
    {
      id: 'physical-mental', name: '身心状态', icon: '💪', expanded: false,
      items: [
        { id: 'personality', label: '性格特质', value: step2Data.mbti?.options?.[0]?.type || 'ISTJ', confidence: 0.5, checked: true, options: MBTI_TYPES, editing: false },
        { id: 'physical-health', label: '身体健康基线', value: '基本健康', confidence: 0.3, checked: true, options: HEALTH_OPTIONS, editing: false },
        { id: 'mental-energy', label: '心理能量水平', value: '中等水平', confidence: 0.3, checked: true, options: MENTAL_ENERGY_OPTIONS, editing: false },
        { id: 'energy-rhythm', label: '精力管理节律', value: '中间型', confidence: 0.4, checked: true, options: CHRONOTYPE_OPTIONS, editing: false },
        { id: 'body-mind', label: '身心连接状态', value: '基本协调', confidence: 0.3, checked: true, options: ['非常协调','基本协调','偶尔失调','经常失调'], editing: false },
        { id: 'emotional-stability', label: '情绪稳定性', value: '中等', confidence: 0.4, checked: true, options: ['非常稳定','比较稳定','中等','不太稳定','很不稳定'], editing: false },
        { id: 'stress-level', label: '压力水平', value: '中等', confidence: 0.4, checked: true, options: ['无压力','轻度','中度','重度','极重度'], editing: false },
        { id: 'resilience', label: '心理韧性', value: '中等', confidence: 0.4, checked: true, options: ['非常强','比较强','中等','比较弱','非常弱'], editing: false },
        { id: 'sleep-quality', label: '睡眠质量', value: '一般', confidence: 0.4, checked: true, options: ['非常好','比较好','一般','比较差','非常差'], editing: false },
        { id: 'diet-pattern', label: '饮食模式', value: '规律三餐', confidence: 0.4, checked: true, options: ['规律三餐','偶尔不规律','经常不规律','节食','暴饮暴食'], editing: false }
      ]
    },
    {
      id: 'spiritual-world', name: '精神世界', icon: '🌟', expanded: false,
      items: [
        { id: 'core-values', label: '核心价值观排序', value: '成就>关系>自由', confidence: 0.4, checked: true, options: [], editing: false },
        { id: 'life-meaning', label: '人生意义感来源', value: '工作', confidence: 0.4, checked: true, options: ['工作','家庭','信仰','创造','服务','体验'], editing: false },
        { id: 'knowledge-interest', label: '知识兴趣地图', value: '科技', confidence: 0.5, checked: true, options: ['文史','科技','哲学','艺术','体育','其他'], editing: false },
        { id: 'aesthetic', label: '审美与创造表达', value: '无明显偏好', confidence: 0.3, checked: true, options: ['音乐','绘画','写作','手工','摄影','无明显偏好'], editing: false },
        { id: 'belief', label: '信念与精神寄托', value: '无宗教信仰', confidence: 0.4, checked: true, options: ['佛教','基督教','伊斯兰教','道教','无宗教信仰','其他'], editing: false },
        { id: 'reading-pref', label: '阅读偏好', value: '非虚构类', confidence: 0.4, checked: true, options: ['文学小说','非虚构类','科技类','哲学类','不常阅读'], editing: false },
        { id: 'creative-tendency', label: '创作倾向', value: '偶尔', confidence: 0.3, checked: true, options: ['经常创作','偶尔创作','有想法不实践','无创作欲望'], editing: false },
        { id: 'spiritual-practice', label: '精神实践', value: '无', confidence: 0.3, checked: true, options: ['冥想','瑜伽','祈祷','阅读','无'], editing: false },
        { id: 'life-philosophy', label: '人生哲学', value: '务实主义', confidence: 0.3, checked: true, options: [], editing: false },
        { id: 'death-view', label: '生死观', value: '顺其自然', confidence: 0.3, checked: true, options: [], editing: false }
      ]
    },
    {
      id: 'behavior-pattern', name: '行为模式', icon: '⚡', expanded: false,
      items: [
        { id: 'decision-style', label: '决策风格', value: '理性分析型', confidence: 0.55, checked: true, options: DECISION_STYLE_OPTIONS, editing: false },
        { id: 'interaction-mode', label: '人际互动模式', value: '安全型依恋', confidence: 0.45, checked: true, options: INTERACTION_OPTIONS, editing: false },
        { id: 'time-management', label: '时间管理特征', value: '有计划', confidence: 0.4, checked: true, options: ['严格计划','有计划','随性','经常拖延'], editing: false },
        { id: 'stress-response', label: '应对压力策略', value: '积极应对', confidence: 0.4, checked: true, options: ['积极应对','寻求帮助','逃避','情绪化','物质依赖'], editing: false },
        { id: 'growth-pattern', label: '成长与改变模式', value: '稳步成长', confidence: 0.4, checked: true, options: ['快速成长','稳步成长','停滞','倒退'], editing: false },
        { id: 'learning-agility', label: '学习敏捷性', value: '中等', confidence: 0.5, checked: true, options: ['非常敏捷','比较敏捷','中等','不太敏捷'], editing: false },
        { id: 'comfort-zone', label: '舒适区边界', value: '中等', confidence: 0.4, checked: true, options: ['愿意突破','中等','比较保守','非常保守'], editing: false },
        { id: 'change-willingness', label: '改变意愿', value: '中等', confidence: 0.4, checked: true, options: ['非常愿意','比较愿意','中等','不太愿意','抗拒'], editing: false },
        { id: 'self-reflection', label: '自我反思习惯', value: '偶尔', confidence: 0.4, checked: true, options: ['经常反思','偶尔反思','很少反思','从不反思'], editing: false },
        { id: 'habit-formation', label: '习惯养成能力', value: '中等', confidence: 0.4, checked: true, options: ['非常强','比较强','中等','比较弱'], editing: false }
      ]
    }
  ]
}

// watch visible 重置状态
watch(() => props.visible, (val) => {
  if (val) {
    currentStep.value = 1
    step2Loading.value = false
    step3Loading.value = false
    categories.value = []
    customItems.value = []
    showCustomAdd.value = false
    customInput.value = ''
    Object.assign(form, {
      birthDate: '', birthTime: '', bloodType: '', gender: '', birthplace: '',
      education: '', occupation: '', maritalStatus: '',
      childrenCount: 0, incomeRange: ''
    })
  }
})
</script>

<style scoped>
/* ========== 覆盖层动画 ========== */
.overlay-enter-active, .overlay-leave-active {
  transition: opacity 0.3s ease;
}
.overlay-enter-from, .overlay-leave-to {
  opacity: 0;
}

.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.25s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.expand-enter-active, .expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to {
  max-height: 0 !important;
  opacity: 0;
}

/* ========== 覆盖层 ========== */
.cultivation-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.cultivation-panel {
  background: var(--white, #FFF);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: panelIn 0.3s ease;
}

@keyframes panelIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

/* ========== 顶部栏 ========== */
.panel-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border, #E5E5E5);
  background: var(--black, #000);
  color: var(--white, #FFF);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topbar-icon { font-size: 1.2rem; }
.topbar-title {
  font-family: var(--font-mono, monospace);
  font-size: 0.9rem;
  font-weight: 600;
}
.topbar-step {
  font-family: var(--font-mono, monospace);
  font-size: 0.7rem;
  color: var(--orange, #FF4500);
  background: rgba(255, 69, 0, 0.15);
  padding: 2px 8px;
  border-radius: 3px;
}

.close-btn {
  background: none;
  border: none;
  color: var(--white, #FFF);
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}
.close-btn:hover { background: rgba(255, 255, 255, 0.15); }

/* ========== 进度条 ========== */
.progress-bar {
  height: 4px;
  background: #EEE;
  position: relative;
}
.progress-fill {
  height: 100%;
  background: var(--orange, #FF4500);
  transition: width 0.5s ease;
}
.progress-text {
  display: none;
}

/* ========== 步骤内容 ========== */
.step-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  max-height: calc(90vh - 60px);
}

.step-header {
  margin-bottom: 24px;
}
.step-title {
  font-family: var(--font-mono, monospace);
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 6px;
}
.step-subtitle {
  font-size: 0.8rem;
  color: #999;
}

/* ========== 表单网格 ========== */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-label {
  font-family: var(--font-mono, monospace);
  font-size: 0.7rem;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field-input, .field-select {
  padding: 8px 12px;
  border: 1px solid var(--border, #E5E5E5);
  border-radius: 6px;
  font-family: var(--font-sans, sans-serif);
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s;
  background: #FAFAFA;
}
.field-input:focus, .field-select:focus {
  border-color: var(--orange, #FF4500);
  background: #FFF;
}
.field-input-sm { width: 80px; }
.field-hint {
  font-family: var(--font-mono, monospace);
  font-size: 0.65rem;
  color: var(--orange, #FF4500);
}

/* ========== 底部按钮 ========== */
.step-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border, #E5E5E5);
}

.action-btn {
  padding: 10px 20px;
  border: 1px solid var(--border, #E5E5E5);
  background: transparent;
  font-family: var(--font-mono, monospace);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}
.action-btn:hover { background: #F0F0F0; }
.action-btn.primary {
  background: var(--black, #000);
  color: var(--white, #FFF);
  border-color: var(--black, #000);
}
.action-btn.primary:hover { opacity: 0.85; }
.action-btn.ghost {
  border-color: transparent;
}
.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ========== Loading ========== */
.loading-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 0;
  gap: 16px;
}
.loading-text {
  font-family: var(--font-mono, monospace);
  font-size: 0.85rem;
  color: #999;
}
.loading-spinner-spin {
  width: 32px;
  height: 32px;
  border: 3px solid #EEE;
  border-top-color: var(--orange, #FF4500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ========== Step 2 猜测卡片 ========== */
.guess-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.guess-card {
  border: 1px solid var(--border, #E5E5E5);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
}
.guess-card.locked {
  background: #F9F9F9;
  border-color: #DDD;
}
.guess-card.uncertain {
  border-style: dashed;
}

.guess-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.guess-card-icon { font-size: 1rem; }
.guess-card-title {
  font-family: var(--font-mono, monospace);
  font-size: 0.8rem;
  font-weight: 600;
  flex: 1;
}

.locked-badge {
  font-family: var(--font-mono, monospace);
  font-size: 0.6rem;
  color: #999;
  background: #EEE;
  padding: 2px 6px;
  border-radius: 3px;
}
.uncertain-badge {
  font-family: var(--font-mono, monospace);
  font-size: 0.6rem;
  color: var(--orange, #FF4500);
  background: rgba(255, 69, 0, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
}

.guess-card-value {
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 8px;
}

/* 推理依据 */
.guess-reasoning {
  margin-bottom: 12px;
}
.reasoning-title {
  font-family: var(--font-mono, monospace);
  font-size: 0.7rem;
  color: #999;
  margin-bottom: 4px;
}
.reasoning-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.reasoning-list li {
  font-size: 0.78rem;
  color: #666;
  padding: 2px 0;
  padding-left: 12px;
  position: relative;
}
.reasoning-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--orange, #FF4500);
}

/* MBTI 选项 */
.mbti-options {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.mbti-option {
  flex: 1;
  padding: 10px;
  border: 1px solid var(--border, #E5E5E5);
  border-radius: 6px;
  background: #FAFAFA;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  transition: all 0.15s;
}
.mbti-option:hover { border-color: var(--orange, #FF4500); }
.mbti-option.selected {
  border-color: var(--orange, #FF4500);
  background: rgba(255, 69, 0, 0.08);
}
.mbti-type {
  font-family: var(--font-mono, monospace);
  font-size: 0.85rem;
  font-weight: 700;
}
.mbti-prob {
  font-family: var(--font-mono, monospace);
  font-size: 0.65rem;
  color: #999;
}

.mbti-alt-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.alt-btn {
  font-family: var(--font-mono, monospace);
  font-size: 0.7rem;
  color: #666;
  background: none;
  border: 1px solid var(--border, #E5E5E5);
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}
.alt-btn:hover { border-color: var(--orange, #FF4500); color: var(--orange, #FF4500); }
.alt-btn.link { text-decoration: none; }
.mbti-select { width: 100px; padding: 4px 8px; }

/* 置信度条 */
.confidence-bar {
  height: 3px;
  background: #EEE;
  border-radius: 2px;
  margin-bottom: 8px;
  overflow: hidden;
}
.confidence-fill {
  height: 100%;
  background: var(--orange, #FF4500);
  border-radius: 2px;
  transition: width 0.3s;
}

/* AI 提示 */
.ai-note {
  font-size: 0.75rem;
  color: #999;
  margin-bottom: 8px;
  font-style: italic;
}

/* 操作按钮 */
.guess-actions {
  display: flex;
  gap: 8px;
}
.mini-btn {
  font-family: var(--font-mono, monospace);
  font-size: 0.65rem;
  padding: 4px 10px;
  border: 1px solid var(--black, #000);
  background: var(--black, #000);
  color: var(--white, #FFF);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}
.mini-btn:hover { opacity: 0.85; }
.mini-btn.outline {
  background: transparent;
  color: var(--black, #000);
}
.mini-btn.outline:hover { background: #F0F0F0; }
.mini-btn.ghost {
  background: transparent;
  border-color: transparent;
  color: #999;
}
.mini-btn.ghost:hover { color: var(--black, #000); }

.edit-area {
  margin-top: 8px;
}

/* ========== Step 3 分类区域 ========== */
.categories-area {
  margin-bottom: 24px;
}

.completion-stats {
  margin-bottom: 20px;
}
.stats-bar {
  height: 6px;
  background: #EEE;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}
.stats-fill {
  height: 100%;
  background: var(--orange, #FF4500);
  border-radius: 3px;
  transition: width 0.3s;
}
.stats-text {
  font-family: var(--font-mono, monospace);
  font-size: 0.7rem;
  color: #999;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-card {
  border: 1px solid var(--border, #E5E5E5);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}
.category-card.expanded {
  border-color: #CCC;
}
.category-card.partially {
  border-left: 3px solid var(--orange, #FF4500);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.15s;
}
.category-header:hover { background: #F9F9F9; }

.cat-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}
.cat-icon { font-size: 1rem; }
.cat-name {
  font-family: var(--font-mono, monospace);
  font-size: 0.8rem;
  font-weight: 600;
}
.cat-count {
  font-family: var(--font-mono, monospace);
  font-size: 0.65rem;
  color: #999;
  background: #F0F0F0;
  padding: 1px 6px;
  border-radius: 3px;
}

.cat-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.cat-check-all {
  display: flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-mono, monospace);
  font-size: 0.65rem;
  color: #999;
  cursor: pointer;
}
.cat-check-all input { accent-color: var(--orange, #FF4500); }
.expand-arrow {
  font-size: 0.6rem;
  color: #CCC;
  transition: transform 0.2s;
}

.category-body {
  max-height: 600px;
  overflow-y: auto;
  border-top: 1px solid var(--border, #E5E5E5);
}

/* 项目行 */
.item-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid #F5F5F5;
  transition: all 0.15s;
  animation: itemIn 0.3s ease backwards;
}
.item-row:last-child { border-bottom: none; }
.item-row:hover { background: #FAFAFA; }
.item-row.unchecked {
  opacity: 0.4;
}
.item-row.unchecked:hover { opacity: 0.7; }

@keyframes itemIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.item-check input {
  accent-color: var(--orange, #FF4500);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.item-content {
  flex: 1;
  min-width: 0;
}
.item-label {
  font-family: var(--font-mono, monospace);
  font-size: 0.7rem;
  color: #999;
  margin-bottom: 2px;
}
.item-value {
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 置信度点 */
.confidence-dots {
  display: flex;
  gap: 2px;
}
.confidence-dots .dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #DDD;
}
.confidence-dots .dot.active {
  background: var(--orange, #FF4500);
}

.item-actions {
  display: flex;
  gap: 4px;
}
.icon-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.icon-btn.confirm { background: #E8F5E9; color: #4CAF50; }
.icon-btn.confirm:hover { background: #C8E6C9; }
.icon-btn.edit { background: #FFF3E0; color: #FF9800; }
.icon-btn.edit:hover { background: #FFE0B2; }
.icon-btn.save { background: #E8F5E9; color: #4CAF50; }
.icon-btn.cancel { background: #FFEBEE; color: #F44336; }
.icon-btn.cancel:hover { background: #FFCDD2; }

.item-edit {
  margin-top: 4px;
}
.item-select, .item-input {
  width: 100%;
  padding: 4px 8px;
  border: 1px solid var(--border, #E5E5E5);
  border-radius: 4px;
  font-size: 0.8rem;
  outline: none;
}
.item-select:focus, .item-input:focus {
  border-color: var(--orange, #FF4500);
}

/* 追加自定义 */
.custom-add-area {
  margin-top: 16px;
  border-top: 1px solid var(--border, #E5E5E5);
  padding-top: 16px;
}
.add-custom-btn {
  font-family: var(--font-mono, monospace);
  font-size: 0.75rem;
  color: var(--orange, #FF4500);
  background: none;
  border: 1px dashed var(--orange, #FF4500);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s;
}
.add-custom-btn:hover { background: rgba(255, 69, 0, 0.05); }

.custom-add-form {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.custom-add-form .field-input { flex: 1; }

.custom-items-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.custom-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #F9F9F9;
  border-radius: 4px;
  font-size: 0.8rem;
}
.custom-label {
  font-family: var(--font-mono, monospace);
  font-size: 0.65rem;
  color: #999;
}
.custom-value { flex: 1; }

/* ========== 响应式 ========== */
@media (max-width: 640px) {
  .form-grid { grid-template-columns: 1fr; }
  .cultivation-panel { max-height: 95vh; }
  .step-content { padding: 16px; }
  .mbti-options { flex-wrap: wrap; }
  .mbti-option { min-width: calc(50% - 4px); }
}

/* ========== 新增样式：选项详情 ========== */
.option-detail {
  margin-top: 8px;
  padding: 10px 12px;
  background: #F9F9F9;
  border-radius: 6px;
  text-align: left;
  width: 100%;
}
.option-desc {
  font-size: 0.75rem;
  color: #555;
  line-height: 1.5;
  margin-bottom: 6px;
}
.option-traits {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}
.trait-tag {
  font-family: var(--font-mono, monospace);
  font-size: 0.6rem;
  color: var(--orange, #FF4500);
  background: rgba(255, 69, 0, 0.08);
  padding: 1px 6px;
  border-radius: 3px;
}
.option-reason {
  font-size: 0.7rem;
  color: #888;
  font-style: italic;
  border-top: 1px solid #EEE;
  padding-top: 6px;
  line-height: 1.4;
}
.option-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

/* MBTI 选项 */
.mbti-name {
  font-size: 0.65rem;
  color: #999;
  margin-top: 2px;
}
.mbti-option.expanded {
  border-color: var(--orange, #FF4500) !important;
  background: rgba(255, 69, 0, 0.05) !important;
}
.select-this {
  margin-top: 6px;
  width: 100%;
  text-align: center;
}

/* 卡片展开 */
.guess-card.expanded {
  border-color: #CCC;
}
.confidence-badge {
  font-family: var(--font-mono, monospace);
  font-size: 0.65rem;
  color: var(--orange, #FF4500);
  background: rgba(255, 69, 0, 0.08);
  padding: 1px 6px;
  border-radius: 3px;
  margin-left: auto;
}
.expand-arrow {
  font-size: 0.6rem;
  color: #CCC;
  transition: transform 0.2s;
  margin-left: 8px;
}
.card-detail {
  padding: 12px 0;
}
.current-value {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.value-label {
  font-family: var(--font-mono, monospace);
  font-size: 0.7rem;
  color: #999;
}
.value-name {
  font-weight: 600;
  font-size: 0.9rem;
}

/* 编辑选项 */
.edit-area {
  margin-top: 10px;
}
.edit-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.edit-option {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 8px 12px;
  border: 1px solid var(--border, #E5E5E5);
  border-radius: 6px;
  background: #FAFAFA;
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
  width: 100%;
  font-family: inherit;
}
.edit-option:hover {
  border-color: var(--orange, #FF4500);
  background: #FFF;
}
.edit-option.selected {
  border-color: var(--orange, #FF4500);
  background: rgba(255, 69, 0, 0.05);
}
.edit-opt-name {
  font-weight: 600;
  font-size: 0.8rem;
  color: var(--black, #000);
}
.edit-opt-desc {
  font-size: 0.7rem;
  color: #999;
  margin-top: 2px;
  line-height: 1.3;
}

/* Step 3 推理依据 */
.item-reason {
  margin-top: 6px;
  padding: 8px 10px;
  background: #F9F9F9;
  border-radius: 4px;
  border-left: 2px solid var(--orange, #FF4500);
}
.reason-text {
  font-size: 0.72rem;
  color: #666;
  line-height: 1.4;
}

/* Step 3 垂直编辑选项 */
.edit-options-vertical {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.edit-options-vertical .edit-option {
  width: auto;
  padding: 4px 10px;
  font-size: 0.75rem;
}

/* 出生时间提示 */
.field-hint.optional {
  color: #BBB;
  font-style: italic;
}
</style>
