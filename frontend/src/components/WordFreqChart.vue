<script setup>
import { computed } from 'vue'

const props = defineProps({ freq: Array })

const rows = computed(() => {
  const list = props.freq || []
  if (!list.length) return []
  const max = list[0].count || 1
  return list.map(f => ({
    ...f,
    pct: ((f.count / max) * 100).toFixed(1)
  }))
})
</script>

<template>
  <div class="freq-chart">
    <p v-if="!rows.length" class="empty">（无）</p>
    <div v-for="(f, i) in rows" :key="i" class="freq-row">
      <span class="freq-word" :title="f.word">{{ f.word }}</span>
      <div class="freq-track"><div class="freq-bar" :style="{ width: f.pct + '%' }"></div></div>
      <span class="freq-count">{{ f.count }}</span>
    </div>
  </div>
</template>
