<template>
  <router-view />
</template>

<script setup>
import { watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const i18n = useI18n()

const pageTitles = {
  Home: 'MiroFish - 预测万物',
  Process: 'MiroFish - 模拟中',
  Simulation: 'MiroFish - 模拟运行',
  SimulationRun: 'MiroFish - 模拟运行',
  Report: 'MiroFish - 报告生成',
  Interaction: 'MiroFish - 深度互动',
}

function updateTitle() {
  const base = pageTitles[route.name]
  document.title = base || 'MiroFish - 预测万物'
}

watch(() => route.name, updateTitle)
watch(i18n.locale, updateTitle)
onMounted(updateTitle)

// MainView will call window.__updateTabTitle(stepNum) to show step
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'JetBrains Mono', 'Space Grotesk', 'Noto Sans SC', monospace;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #000000;
  background-color: #ffffff;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #000000;
}

::-webkit-scrollbar-thumb:hover {
  background: #333333;
}

/* 全局按钮样式 */
button {
  font-family: inherit;
}
</style>
