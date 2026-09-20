import axios from 'axios'

// baseURL 使用相对路径 /api，由 Vite dev server 代理到后端 Flask（见 vite.config.js）
const http = axios.create({
  baseURL: '/api',
  timeout: 120000
})

// 统一抽取后端返回的 data
function unwrap(res) {
  const body = res.data
  if (body && body.code !== 0) {
    throw new Error(body.message || '请求失败')
  }
  return body ? body.data : null
}

export const uploadDocument = async (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return unwrap(await http.post('/documents/upload', fd))
}

export const listDocuments = async () => {
  const data = unwrap(await http.get('/documents'))
  return data.items || []
}

export const getDocument = async (id) => unwrap(await http.get(`/documents/${id}`))

export const deleteDocument = async (id) => unwrap(await http.delete(`/documents/${id}`))

export const getStats = async () => unwrap(await http.get('/stats'))
