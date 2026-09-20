# -*- coding: utf-8 -*-
"""文本预处理模块：清洗、分句、分段。"""
import re

# 常见中文停用词（精简版）
STOPWORDS = {
    '的', '了', '是', '在', '和', '与', '及', '或', '等', '这', '那', '之', '其',
    '一个', '一种', '我们', '他们', '她们', '你们', '进行', '通过', '可以', '能够',
    '以及', '但是', '因为', '所以', '如果', '然后', '而且', '并且', '对于', '关于',
    '这个', '那个', '这些', '那些', '自己', '本文', '研究', '方法', '结果', '结论',
    '具有', '没有', '不是', '就是', '还是', '也是', '都是', '主要', '相关', '其中',
    'a', 'an', 'the', 'of', 'and', 'or', 'to', 'in', 'on', 'for', 'with', 'is',
    'are', 'was', 'were', 'be', 'been', 'this', 'that', 'these', 'those',
}


def normalize_text(raw_text):
    """清洗原始文本：统一换行、去除控制字符、压缩空白。"""
    text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    # 去除控制字符（保留换行与制表符转空格）
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    # 合并 3 个以上连续换行为 2 个（保留段落分隔）
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 行内多余空格
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def split_sentences(text):
    """按中文句末标点切分句子，返回非空句子列表。"""
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return []
    # 保留句末标点，以 。！？；!?; 为切分点
    parts = re.split(r'(?<=[。！？；!?;])', text)
    sentences = [p.strip() for p in parts if p.strip() and len(p.strip()) >= 2]
    return sentences


def split_paragraphs(raw_text):
    """从原始文本中切分段落。

    综合三种信号识别段落边界：
      1. 空行；
      2. 行首缩进（全角空格「　」或 2 个以上半角空格）——中文论文段首常见；
      3. 句末标点结尾（兜底）。
    段落内部把 PDF 换行引起的硬换行拼接起来。
    """
    text = normalize_text(raw_text)
    paragraphs = _split_by_indent_or_blank(text)

    # 兜底：几乎没分出段落时，按句末标点切分
    if len(paragraphs) <= 1:
        paragraphs = _split_by_sentence_end(text)

    # 最终兜底：按每 4 句一组切分
    if len(paragraphs) <= 1:
        sentences = split_sentences(text)
        paragraphs = [''.join(sentences[i:i + 4]).strip()
                      for i in range(0, len(sentences), 4)]

    return [p for p in paragraphs if p and len(p) >= 15]


def _is_indent_start(line):
    """判断一行是否为段首（以全角空格或 2 个以上半角空格/制表符开头）。"""
    return (line.startswith('　') or line.startswith('\t')
            or line.startswith('    ') or line.startswith('  '))


def _is_heading_line(lines, i):
    """判断是否为独立标题行：短、非句末标点结尾、后一行缩进或为空。"""
    line = lines[i].strip()
    if not 2 <= len(line) <= 15:
        return False
    if re.search(r'[。！？；!?;]$', line):
        return False
    nxt = lines[i + 1].strip() if i + 1 < len(lines) else ''
    return _is_indent_start(nxt) or nxt == ''


def _split_by_indent_or_blank(text):
    blocks = re.split(r'\n\s*\n', text)
    out = []
    for block in blocks:
        lines = [l.rstrip() for l in block.split('\n') if l.strip()]
        cur = []
        for i, line in enumerate(lines):
            if _is_heading_line(lines, i):
                if cur:
                    out.append(''.join(cur))
                    cur = []
                continue
            if _is_indent_start(line) and cur:
                out.append(''.join(cur))
                cur = []
            cur.append(line.strip())
        if cur:
            out.append(''.join(cur))
    return out


def _split_by_sentence_end(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    out = []
    cur = []
    for line in lines:
        cur.append(line)
        if re.search(r'[。！？；!?;]$', line):
            out.append(''.join(cur))
            cur = []
    if cur:
        out.append(''.join(cur))
    return out
