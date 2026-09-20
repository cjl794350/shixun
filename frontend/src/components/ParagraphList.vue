<script setup>
defineProps({ paragraphs: Array })
</script>

<template>
  <div class="para-list">
    <p v-if="!paragraphs || !paragraphs.length" class="empty">（无）</p>
    <div v-for="p in paragraphs" :key="p.para_no" class="para-item">
      <div class="para-head">
        <span class="para-no">{{ p.para_no }}</span>
        <div class="para-meta">
          <span>{{ p.sentence_count }} 句</span>
          <span>{{ p.char_count }} 字</span>
        </div>
        <div class="para-importance">
          重要度
          <div class="importance-track"><div class="importance-bar" :style="{ width: p.score + '%' }"></div></div>
          <span>{{ p.score }}</span>
        </div>
      </div>
      <div class="para-content">{{ p.content }}</div>
      <div class="para-key"><b>关键句：</b>{{ p.key_sentence || '（无）' }}</div>
    </div>
  </div>
</template>
