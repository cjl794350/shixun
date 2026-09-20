# -*- coding: utf-8 -*-
"""关键词提取与词频统计模块（基于 jieba）。"""
import re
from collections import Counter

import jieba
import jieba.analyse

from .text_processor import STOPWORDS

# 关闭 jieba 日志输出
jieba.setLogLevel(60)


def _is_valid_word(word):
    """判断是否为有效词：长度>=2、非纯数字、非纯符号、非停用词。"""
    w = word.strip()
    if len(w) < 2:
        return False
    if w in STOPWORDS:
        return False
    if w.isdigit():
        return False
    if re.fullmatch(r'[\W_]+', w):
        return False
    return True


def extract_keywords(text, topk=20):
    """使用 jieba 的 TF-IDF 算法提取关键词，返回 [{'keyword','weight'}, ...]。"""
    tags = jieba.analyse.extract_tags(text, topK=topk, withWeight=True)
    result = []
    for word, weight in tags:
        if _is_valid_word(word):
            result.append({'keyword': word, 'weight': round(float(weight), 4)})
    return result


def extract_textrank_keywords(text, topk=10):
    """使用 jieba 的 TextRank 算法提取关键词（作为补充参考）。"""
    tags = jieba.analyse.textrank(text, topK=topk, withWeight=True)
    return [{'keyword': w, 'weight': round(float(t), 4)}
            for w, t in tags if _is_valid_word(w)]


def word_frequency(text, topk=30):
    """统计词频，返回 [{'word','count'}, ...]（降序）。"""
    words = jieba.lcut(text)
    counter = Counter()
    for w in words:
        if _is_valid_word(w):
            counter[w] += 1
    return [{'word': w, 'count': c} for w, c in counter.most_common(topk)]
