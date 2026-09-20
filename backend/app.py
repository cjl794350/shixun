# -*- coding: utf-8 -*-
"""PDF 智能摘要工具 —— Flask 后端服务。

提供 RESTful API：上传 PDF、查询历史、查看详情、删除、统计。
前后端分离：前端为独立静态工程，通过 HTTP 调用本服务（CORS 已开启）。
"""
import os
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS

import config
import db
from nlp.pdf_parser import parse_pdf, PdfParseError
from nlp.analyzer import PaperAnalyzer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
CORS(app)  # 允许所有来源跨域，便于前端独立部署

# 上传文件保存目录
UPLOAD_FOLDER = config.UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def ok(data=None, message='ok'):
    return jsonify({'code': 0, 'message': message, 'data': data})


def fail(message, code=1, http=400):
    return jsonify({'code': code, 'message': message, 'data': None}), http


def _allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health():
    return ok({'status': 'up', 'service': 'pdf-summary'})


@app.route('/api/documents/upload', methods=['POST'])
def upload():
    """上传 PDF 并立即执行分析，结果入库后返回。"""
    if 'file' not in request.files:
        return fail('未检测到上传文件')
    file = request.files['file']
    if file.filename == '':
        return fail('文件名为空')
    if not _allowed_file(file.filename):
        return fail('仅支持 PDF 文件')

    original_name = file.filename
    stored_name = f'{uuid.uuid4().hex}.pdf'
    file_path = os.path.join(UPLOAD_FOLDER, stored_name)
    file.save(file_path)
    file_size = os.path.getsize(file_path)

    try:
        full_text, page_count = parse_pdf(file_path)
        if not full_text or len(full_text.strip()) < 50:
            return fail('未能从 PDF 中提取到有效文本，可能是扫描版/图片型 PDF')
    except PdfParseError as exc:
        return fail(str(exc))

    # 执行 NLP 分析
    analyzer = PaperAnalyzer(full_text)
    result = analyzer.run()
    stats = result['stats']
    summary = result['summary']

    # 写入文档主表
    doc_id = db.execute_insert(
        "INSERT INTO pdf_document(original_name, stored_name, file_size, page_count,"
        " char_count, sentence_count, para_count, summary, status)"
        " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,2)",
        (original_name, stored_name, file_size, page_count,
         stats['char_count'], stats['sentence_count'], stats['para_count'], summary)
    )

    # 写入关键词表
    for kw in result['keywords']:
        db.execute(
            "INSERT INTO pdf_keyword(document_id, keyword, weight) VALUES(%s,%s,%s)",
            (doc_id, kw['keyword'], kw['weight'])
        )

    # 写入段落表
    for p in result['paragraphs']:
        db.execute(
            "INSERT INTO pdf_paragraph(document_id, para_no, content, sentence_count,"
            " char_count, score, key_sentence) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (doc_id, p['para_no'], p['content'], p['sentence_count'],
             p['char_count'], p['score'], p['key_sentence'])
        )

    return ok({
        'id': doc_id,
        'original_name': original_name,
        'page_count': page_count,
        'summary': summary,
        'keywords': result['keywords'],
        'stats': stats,
        'paragraphs': result['paragraphs'],
        'word_freq': result['word_freq'],
    }, message='分析完成')


@app.route('/api/documents', methods=['GET'])
def list_documents():
    """历史记录列表（不含段落明细，减少体积）。"""
    rows = db.query(
        "SELECT id, original_name, page_count, char_count, sentence_count,"
        " para_count, summary, create_time FROM pdf_document ORDER BY id DESC"
    )
    for r in rows:
        r['create_time'] = str(r['create_time'])
    return ok({'total': len(rows), 'items': rows})


@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """文档详情：摘要 + 关键词 + 段落分析 + 词频。"""
    doc = db.query_one(
        "SELECT id, original_name, page_count, char_count, sentence_count,"
        " para_count, summary, create_time FROM pdf_document WHERE id=%s",
        (doc_id,)
    )
    if not doc:
        return fail('文档不存在', http=404)
    doc['create_time'] = str(doc['create_time'])
    doc['keywords'] = db.query(
        "SELECT keyword, weight FROM pdf_keyword WHERE document_id=%s ORDER BY weight DESC",
        (doc_id,)
    )
    doc['paragraphs'] = db.query(
        "SELECT para_no, content, sentence_count, char_count, score, key_sentence"
        " FROM pdf_paragraph WHERE document_id=%s ORDER BY para_no",
        (doc_id,)
    )
    return ok(doc)


@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """删除文档及其关联的关键词、段落记录与文件。"""
    doc = db.query_one("SELECT stored_name FROM pdf_document WHERE id=%s", (doc_id,))
    if not doc:
        return fail('文档不存在', http=404)
    db.execute("DELETE FROM pdf_keyword WHERE document_id=%s", (doc_id,))
    db.execute("DELETE FROM pdf_paragraph WHERE document_id=%s", (doc_id,))
    db.execute("DELETE FROM pdf_document WHERE id=%s", (doc_id,))
    if doc.get('stored_name'):
        path = os.path.join(UPLOAD_FOLDER, doc['stored_name'])
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
    return ok(message='删除成功')


@app.route('/api/stats', methods=['GET'])
def stats():
    """全局统计：文档数、总段落数、总字数等。"""
    total = db.query_one("SELECT COUNT(*) AS c FROM pdf_document")['c']
    para = db.query_one("SELECT COUNT(*) AS c FROM pdf_paragraph")['c']
    chars = db.query_one("SELECT IFNULL(SUM(char_count),0) AS c FROM pdf_document")['c']
    return ok({'document_count': total, 'paragraph_count': para, 'total_chars': int(chars)})


if __name__ == '__main__':
    db.init_db()
    print(f'后端服务已启动: http://127.0.0.1:{config.SERVER_PORT}')
    app.run(host='0.0.0.0', port=config.SERVER_PORT, debug=False)
