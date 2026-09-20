<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  file: Object,
  loading: Boolean
})
const emit = defineEmits(['select', 'clear', 'analyze'])

const dragging = ref(false)
const fileInput = ref(null)

const fileName = computed(() => props.file?.name || '')
const fileSize = computed(() => (props.file ? formatSize(props.file.size) : ''))

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

function onDrop(e) {
  dragging.value = false
  const f = e.dataTransfer.files[0]
  if (f) emit('select', f)
}

function onPick(e) {
  const f = e.target.files[0]
  if (f) emit('select', f)
  e.target.value = ''
}
</script>

<template>
  <div
    class="upload-card"
    :class="{ dragover: dragging }"
    @dragover.prevent="dragging = true"
    @dragleave.prevent="dragging = false"
    @drop.prevent="onDrop"
    @click="fileInput.click()"
  >
    <div class="upload-inner">
      <div class="upload-icon">
        <svg viewBox="0 0 24 24" width="44" height="44" fill="none" stroke="currentColor" stroke-width="1.6">
          <path d="M12 16V4m0 0l-4 4m4-4l4 4" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M4 15v3a2 2 0 002 2h12a2 2 0 002-2v-3" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <p class="upload-title">将论文 PDF 拖拽到此处，或点击选择文件</p>
      <p class="upload-sub">支持单文件 PDF，最大 16MB · 本地解析，数据不出本机</p>
      <input type="file" ref="fileInput" accept=".pdf" hidden @change="onPick" />
      <button class="btn btn-primary" @click.stop="fileInput.click()">选择文件</button>
    </div>
  </div>

  <div v-if="file" class="file-badge">
    <span class="file-name">{{ fileName }}</span>
    <span class="file-size">{{ fileSize }}</span>
    <button class="btn btn-primary" :disabled="loading" @click="emit('analyze')">开始智能分析</button>
    <button class="btn btn-ghost" @click="emit('clear')">移除</button>
  </div>
</template>
