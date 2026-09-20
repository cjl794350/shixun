# -*- coding: utf-8 -*-
"""PDF 解析模块：使用 PyMuPDF (fitz) 提取 PDF 文本、页数与段落块。"""
import fitz  # PyMuPDF


class PdfParseError(Exception):
    pass


def parse_pdf(file_path):
    """解析 PDF 文件，返回 (full_text, page_count)。

    full_text 为逐页拼接的纯文本，页与页之间以换行分隔。
    """
    try:
        doc = fitz.open(file_path)
    except Exception as exc:  # noqa: BLE001
        raise PdfParseError(f'无法打开 PDF 文件: {exc}')

    page_count = doc.page_count
    pages = []
    try:
        for page in doc:
            pages.append(page.get_text('text'))
    finally:
        doc.close()

    full_text = '\n'.join(pages)
    return full_text, page_count
