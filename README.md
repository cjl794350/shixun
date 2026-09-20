# PDF 智能摘要工具

上传论文 PDF，自动生成 **全文摘要**、**关键词**、**词频统计** 与 **逐段分析**。

- 前后端分离：后端 Flask 提供 RESTful API，前端为 Vue 3 + Vite 单页应用。
- 核心算法：jieba 分词 + TF-IDF 关键词提取 + TextRank 图排序抽取式摘要。
- 数据存储：MySQL。

## 技术栈

| 层 | 技术 | 开发工具 |
| --- | --- | --- |
| 后端 | Python 3 · Flask · Flask-CORS · PyMuPDF · jieba · NumPy · PyMySQL | PyCharm |
| 前端 | Vue 3 · Vite · Axios | VS Code |
| 数据库 | MySQL 8.0（utf8mb4，InnoDB） | Navicat / 命令行 |

## 目录结构

```
program/
├── backend/                    # 后端（PyCharm 打开此目录）
│   ├── app.py                  # Flask 入口（RESTful API）
│   ├── config.py               # 配置（数据库、端口、上传目录）
│   ├── db.py                   # MySQL 访问层（自动建库建表）
│   ├── nlp/
│   │   ├── pdf_parser.py       # PDF 文本提取
│   │   ├── text_processor.py   # 清洗 / 分句 / 分段
│   │   ├── keyword_extract.py  # 关键词 & 词频
│   │   ├── summarizer.py       # TextRank 摘要
│   │   └── analyzer.py         # 综合分析器
│   ├── requirements.txt
│   └── sql/init.sql            # 数据库建库脚本
├── frontend/                   # 前端（VS Code 打开此目录）
│   ├── package.json
│   ├── vite.config.js          # 含 /api 代理到后端
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       ├── api/index.js        # Axios 封装
│       └── components/         # 各功能组件
├── samples/
│   ├── generate_sample.py      # 生成样例论文 PDF
│   └── 多篇不同领域的样例论文.pdf（图像分类/情感分析/糖尿病预测/股票预测/图书推荐/入侵检测/空气质量预测）
└── README.md
```

## 快速开始

### 1. 初始化数据库（两种方式任选其一）

```bash
# 方式 A：直接执行 SQL 脚本
mysql -uroot -proot < backend/sql/init.sql

# 方式 B：启动后端时自动建库建表（db.py 的 init_db() 会幂等创建）
```

### 2. 后端 —— 在 PyCharm 中运行

1. PyCharm 打开 `backend` 目录（File → Open → 选择 `backend` 文件夹）。
2. 设置 Python 解释器：Settings → Project → Python Interpreter，选择你的 Anaconda/Python（需已安装依赖）。
3. 安装依赖（若未装）：
   ```bash
   pip install -r backend/requirements.txt
   ```
4. 右键 `app.py` → Run（或直接点绿色运行按钮），看到 `后端服务已启动: http://127.0.0.1:5000` 即成功。

> 后端监听 **5000** 端口。

### 3. 前端 —— 在 VS Code 中运行

1. VS Code 打开 `frontend` 目录（File → Open Folder → 选择 `frontend` 文件夹）。
2. 在 VS Code 终端（Terminal）执行：
   ```bash
   npm install        # 首次运行需安装依赖
   npm run dev        # 启动开发服务器
   ```
3. 浏览器访问终端提示的地址，默认 **http://localhost:5173**。

> 前端开发服务器监听 **5173** 端口，`/api` 请求已通过 Vite 代理自动转发到后端 5000 端口，无需手动配置跨域。

### 4. 使用

1. 打开前端页面，点击「选择文件」或拖拽 PDF 到上传区；
2. 点击「开始智能分析」；
3. 查看摘要、关键词云、词频统计与段落分析结果；
4. 切换到「历史记录」查看/删除历史分析。

## API 一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | /api/health | 健康检查 |
| POST | /api/documents/upload | 上传 PDF 并分析（multipart 字段名 `file`） |
| GET | /api/documents | 历史记录列表 |
| GET | /api/documents/{id} | 文档详情（摘要+关键词+段落） |
| DELETE | /api/documents/{id} | 删除文档 |
| GET | /api/stats | 全局统计 |

## 数据库表

- `pdf_document`：文档主表（文件名、页数、字数、摘要等）
- `pdf_keyword`：关键词及 TF-IDF 权重
- `pdf_paragraph`：逐段分析结果（句数、字数、重要度、关键句）

## 说明

- 扫描版/图片型 PDF（无文本层）无法提取文本，会提示失败。
- 摘要、关键词均为离线算法，无需联网或外部 API。
- 前端生产构建：`npm run build`（产物在 `frontend/dist`），开发用 `npm run dev`。
