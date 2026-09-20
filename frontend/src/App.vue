<script setup>
import { ref, onMounted } from 'vue'
import UploadPanel from './components/UploadPanel.vue'
import StatsCards from './components/StatsCards.vue'
import KeywordCloud from './components/KeywordCloud.vue'
import WordFreqChart from './components/WordFreqChart.vue'
import ParagraphList from './components/ParagraphList.vue'
import HistoryTable from './components/HistoryTable.vue'
import { uploadDocument, listDocuments, getDocument, deleteDocument } from './api'

const VIEW_KEY = 'pdf-summary-view'
const savedView = localStorage.getItem(VIEW_KEY)
const currentView = ref(['analyze', 'history', 'about'].includes(savedView) ? savedView : 'analyze')
const selectedFile = ref(null)
const loading = ref(false)
const loadingText = ref('')
const result = ref(null)
const history = ref([])

const toastMsg = ref('')
const toastErr = ref(false)
let toastTimer = null
function toast(msg, err = false) {
  toastMsg.value = msg
  toastErr.value = err
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 2600)
}

function switchView(v) {
  currentView.value = v
  localStorage.setItem(VIEW_KEY, v)
  if (v === 'history') loadHistory()
}

onMounted(() => {
  if (currentView.value === 'history') loadHistory()
})

function onSelect(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    toast('仅支持 PDF 文件', true)
    return
  }
  selectedFile.value = file
  result.value = null
}

function onClear() {
  selectedFile.value = null
  result.value = null
}

async function onAnalyze() {
  if (!selectedFile.value) { toast('请先选择 PDF 文件', true); return }
  loading.value = true
  result.value = null
  const steps = [
    '正在解析 PDF 并提取文本…',
    '正在分词并计算关键词…',
    '正在运行 TextRank 摘要算法…',
    '正在执行逐段分析…'
  ]
  let step = 0
  loadingText.value = steps[0]
  const timer = setInterval(() => {
    step = Math.min(step + 1, steps.length - 1)
    loadingText.value = steps[step]
  }, 1200)
  try {
    result.value = await uploadDocument(selectedFile.value)
    toast('分析完成')
  } catch (e) {
    toast(e.message || '网络错误，请确认后端已启动', true)
  } finally {
    clearInterval(timer)
    loading.value = false
  }
}

async function loadHistory() {
  try {
    history.value = await listDocuments()
  } catch (e) {
    history.value = []
    toast('加载历史失败：' + (e.message || ''), true)
  }
}

async function onView(id) {
  try {
    const d = await getDocument(id)
    result.value = {
      page_count: d.page_count,
      stats: { char_count: d.char_count, sentence_count: d.sentence_count, para_count: d.para_count },
      summary: d.summary,
      keywords: d.keywords.map(k => ({ keyword: k.keyword, weight: k.weight })),
      word_freq: (d.keywords || []).slice(0, 15).map(k => ({ word: k.keyword, count: Math.round(k.weight * 1000) })),
      paragraphs: d.paragraphs
    }
    switchView('analyze')
    toast('已加载历史记录')
  } catch (e) {
    toast(e.message || '加载失败', true)
  }
}

async function onDelete(id) {
  if (!confirm('确定删除该记录吗？')) return
  try {
    await deleteDocument(id)
    toast('删除成功')
    loadHistory()
  } catch (e) {
    toast(e.message || '删除失败', true)
  }
}
</script>

<template>
  <header class="topbar">
    <div class="brand">
      <div class="brand-logo">PDF</div>
      <div class="brand-text">
        <h1>PDF 智能摘要工具</h1>
        <p>上传论文 · 自动生成摘要 / 关键词 / 段落分析</p>
      </div>
    </div>
    <nav class="nav">
      <button class="nav-btn" :class="{ active: currentView === 'analyze' }" @click="switchView('analyze')">上传分析</button>
      <button class="nav-btn" :class="{ active: currentView === 'history' }" @click="switchView('history')">历史记录</button>
      <button class="nav-btn" :class="{ active: currentView === 'about' }" @click="switchView('about')">关于系统</button>
    </nav>
  </header>

  <main class="container">
    <!-- 上传分析 -->
    <section v-if="currentView === 'analyze'" class="view">
      <UploadPanel
        :file="selectedFile"
        :loading="loading"
        @select="onSelect"
        @clear="onClear"
        @analyze="onAnalyze"
      />

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>{{ loadingText }}</p>
      </div>

      <div v-if="result">
        <StatsCards :stats="result.stats" :page-count="result.page_count" />

        <div class="card">
          <div class="card-head">
            <h2>📄 全文摘要</h2>
            <span class="tag-chip">TextRank 抽取式</span>
          </div>
          <p class="summary-text">{{ result.summary || '（无）' }}</p>
        </div>

        <div class="two-col">
          <div class="card">
            <div class="card-head"><h2>🏷️ 关键词</h2><span class="tag-chip">TF-IDF</span></div>
            <KeywordCloud :keywords="result.keywords || []" />
          </div>
          <div class="card">
            <div class="card-head"><h2>📊 词频统计 TOP 15</h2></div>
            <WordFreqChart :freq="(result.word_freq || []).slice(0, 15)" />
          </div>
        </div>

        <div class="card">
          <div class="card-head">
            <h2>📑 段落分析</h2>
            <span class="tag-chip">共 {{ (result.paragraphs || []).length }} 段</span>
          </div>
          <ParagraphList :paragraphs="result.paragraphs || []" />
        </div>
      </div>
    </section>

    <!-- 历史记录 -->
    <section v-else-if="currentView === 'history'" class="view">
      <HistoryTable :items="history" @view="onView" @delete="onDelete" @refresh="loadHistory" />
    </section>

    <!-- 关于系统 -->
    <section v-else class="view">
      <div class="card">
        <div class="card-head"><h2>ℹ️ 关于系统</h2></div>
        <div class="about-body">
          <p><strong>项目名称：</strong>PDF 智能摘要工具</p>
          <p><strong>技术栈：</strong>Python · Flask · PyMuPDF · jieba · NumPy · MySQL · Vue 3 · Vite</p>
          <p><strong>核心功能：</strong>上传论文 PDF，自动提取文本并生成全文摘要、关键词、词频统计与逐段分析。</p>
          <p><strong>核心算法：</strong>摘要采用 TextRank 图排序算法，关键词采用 TF-IDF 加权，分词采用 jieba。</p>
          <p><strong>系统架构：</strong>前后端分离，后端提供 RESTful API（端口 5000），前端 Vue 3 + Vite（端口 5173）。</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <p>PDF 智能摘要工具 · 专业综合实训项目 · 计算机与人工智能学院</p>
  </footer>

  <div class="toast" :class="{ show: toastMsg !== '', err: toastErr }">{{ toastMsg }}</div>
</template>
