/**
 * 地名自动完成组合式函数
 */

import { ref, computed, watch } from 'vue'
import type { AutoCompleteSuggestion } from '../types/location'

export function useLocationAutoComplete() {
  const input = ref('')
  const suggestions = ref<AutoCompleteSuggestion[]>([])
  const correctedInput = ref('')

  // 地名别名映射
  const aliasMap: Record<string, string> = {
    '帝都': '北京',
    '魔都': '上海',
    '花城': '广州',
    '羊城': '广州',
    '鹏城': '深圳',
    '春城': '昆明',
    '泉城': '济南',
    '榕城': '福州',
    '蓉城': '成都',
    '星城': '长沙',
    '江城': '武汉',
    '冰城': '哈尔滨',
    '山城': '重庆',
    '古城': '西安',
    '日光城': '拉萨'
  }

  // 输入纠正
  const correctInput = (text: string): string => {
    let corrected = text

    // 替换别名
    Object.entries(aliasMap).forEach(([alias, real]) => {
      corrected = corrected.replace(new RegExp(alias, 'g'), real)
    })

    // 处理箭头符号
    corrected = corrected.replace(/[→➜]/g, ',')
    
    // 处理其他分隔符
    corrected = corrected.replace(/[；;、]/g, ',')
    
    // 清理多余空格和逗号
    corrected = corrected.replace(/\s*,\s*/g, ',').trim()
    
    return corrected
  }

  // 监听输入变化
  watch(input, (newInput) => {
    const corrected = correctInput(newInput)
    if (corrected !== newInput) {
      correctedInput.value = corrected
    } else {
      correctedInput.value = ''
    }

    // 模拟自动完成建议
    if (newInput.length > 1) {
      const mockSuggestions: AutoCompleteSuggestion[] = []
      
      // 检查是否匹配别名
      Object.entries(aliasMap).forEach(([alias, real]) => {
        if (alias.includes(newInput) || real.includes(newInput)) {
          mockSuggestions.push({
            id: `${alias}-${real}`,
            name: `${alias} (${real})`,
            address: `${real}市`
          })
        }
      })

      suggestions.value = mockSuggestions.slice(0, 5)
    } else {
      suggestions.value = []
    }
  })

  // 选择建议
  const selectSuggestion = (suggestion: AutoCompleteSuggestion) => {
    // 提取真实地名
    const match = suggestion.name.match(/\(([^)]+)\)/)
    if (match) {
      input.value = match[1]
    } else {
      input.value = suggestion.name
    }
    suggestions.value = []
  }

  // 清空输入
  const clearInput = () => {
    input.value = ''
    suggestions.value = []
    correctedInput.value = ''
  }

  return {
    input,
    correctedInput,
    suggestions,
    selectSuggestion,
    clearInput
  }
}