import service from './index'

/**
 * Step 2: AI亮底牌 - 基于基础事实推测部分数据
 */
export const guessStep2 = (data) => {
  return service.post('/api/cultivation/guess-step2', data)
}

/**
 * Step 3: AI深猜 - 基于前两步数据推测全部~70项
 */
export const guessStep3 = (data) => {
  return service.post('/api/cultivation/guess-step3', data)
}
