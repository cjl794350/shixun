<script setup>
defineProps({ items: Array })
const emit = defineEmits(['view', 'delete', 'refresh'])

function truncate(s, n) {
  return s && s.length > n ? s.slice(0, n) + '…' : s
}
</script>

<template>
  <div class="card">
    <div class="card-head">
      <h2>🗂️ 历史分析记录</h2>
      <button class="btn btn-ghost btn-sm" @click="emit('refresh')">刷新</button>
    </div>
    <div class="history-table-wrap">
      <table class="history-table">
        <thead>
          <tr>
            <th>#</th><th>文件名</th><th>页数</th><th>字数</th><th>段落</th><th>上传时间</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!items || !items.length">
            <td colspan="7" class="empty">暂无记录，请先上传分析</td>
          </tr>
          <tr v-for="(d, i) in items" :key="d.id">
            <td>{{ i + 1 }}</td>
            <td :title="d.original_name">{{ truncate(d.original_name, 30) }}</td>
            <td>{{ d.page_count }}</td>
            <td>{{ d.char_count }}</td>
            <td>{{ d.para_count }}</td>
            <td>{{ d.create_time }}</td>
            <td>
              <span class="link" @click="emit('view', d.id)">查看</span>
              &nbsp;|&nbsp;
              <span class="link" style="color:#ef4444" @click="emit('delete', d.id)">删除</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
