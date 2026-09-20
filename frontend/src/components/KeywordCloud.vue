<script setup>
import { computed } from 'vue'

const props = defineProps({ keywords: Array })

const PALETTE = [
  'linear-gradient(135deg,#3b82f6,#06b6d4)', 'linear-gradient(135deg,#8b5cf6,#ec4899)',
  'linear-gradient(135deg,#10b981,#22d3ee)', 'linear-gradient(135deg,#f59e0b,#ef4444)',
  'linear-gradient(135deg,#6366f1,#3b82f6)', 'linear-gradient(135deg,#ec4899,#f97316)',
  'linear-gradient(135deg,#14b8a6,#84cc16)', 'linear-gradient(135deg,#f43f5e,#a855f7)'
]

const sized = computed(() => {
  const kw = props.keywords || []
  if (!kw.length) return []
  const weights = kw.map(k => k.weight)
  const min = Math.min(...weights)
  const max = Math.max(...weights)
  const range = (max - min) || 1
  return kw.map((k, i) => ({
    text: k.keyword,
    size: Math.round(13 + ((k.weight - min) / range) * 13),
    bg: PALETTE[i % PALETTE.length]
  }))
})
</script>

<template>
  <div class="keyword-cloud">
    <p v-if="!sized.length" class="empty">（无）</p>
    <span
      v-for="(k, i) in sized"
      :key="i"
      class="kw-tag"
      :style="{ fontSize: k.size + 'px', background: k.bg }"
    >{{ k.text }}</span>
  </div>
</template>
