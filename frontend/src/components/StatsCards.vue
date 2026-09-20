<script setup>
import { computed } from 'vue'

const props = defineProps({
  stats: Object,
  pageCount: [Number, String]
})

const items = computed(() => [
  { num: props.pageCount ?? '-', label: 'PDF 页数' },
  { num: props.stats?.char_count ?? 0, label: '正文字符数' },
  { num: props.stats?.sentence_count ?? 0, label: '句子总数' },
  { num: props.stats?.para_count ?? 0, label: '段落总数' }
])
</script>

<template>
  <div class="stats-grid">
    <div v-for="(i, idx) in items" :key="idx" class="stat-card">
      <div class="stat-num">{{ i.num }}</div>
      <div class="stat-label">{{ i.label }}</div>
    </div>
  </div>
</template>
