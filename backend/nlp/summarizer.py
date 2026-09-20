# -*- coding: utf-8 -*-
"""基于 TextRank 的抽取式自动摘要模块。

思路：
  1. 将文本切分为句子；
  2. 用 jieba 分词并为每个词计算 TF-IDF 权重；
  3. 用词权重构造句子向量，计算句子间余弦相似度，构建相似度图；
  4. 在图上迭代 PageRank 得到句子重要度；
  5. 按重要度选取若干句子，并按原文顺序拼接成摘要。
"""
import re

import numpy as np
import jieba
import jieba.analyse

from .text_processor import STOPWORDS, split_sentences

jieba.setLogLevel(60)


def _tokenize(sentence):
    words = jieba.lcut(sentence)
    out = []
    for w in words:
        w = w.strip()
        if len(w) < 2:
            continue
        if w in STOPWORDS or w.isdigit():
            continue
        if re.fullmatch(r'[\W_]+', w):
            continue
        out.append(w)
    return out


def _cosine(a, b):
    """两个词权重字典的余弦相似度。"""
    if not a or not b:
        return 0.0
    common = set(a.keys()) & set(b.keys())
    if not common:
        return 0.0
    num = sum(a[k] * b[k] for k in common)
    na = sum(v * v for v in a.values()) ** 0.5
    nb = sum(v * v for v in b.values()) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return num / (na * nb)


def _pagerank(matrix, damping=0.85, tol=1e-6, max_iter=100):
    """对相似度矩阵做 PageRank 迭代，返回每个节点的分数。"""
    n = matrix.shape[0]
    col_sum = matrix.sum(axis=0)
    col_sum[col_sum == 0] = 1.0
    m = matrix / col_sum  # 列归一化
    score = np.full(n, 1.0 / n)
    for _ in range(max_iter):
        new_score = (1 - damping) / n + damping * m.dot(score)
        if np.abs(new_score - score).sum() < tol:
            score = new_score
            break
        score = new_score
    return score


def _build_word_weights(text):
    """用 jieba TF-IDF 计算词权重字典。"""
    tags = jieba.analyse.extract_tags(text, topK=1000, withWeight=True)
    return {w: wt for w, wt in tags if len(w.strip()) >= 2}


def score_sentences(text):
    """返回 (sentences, scores)，sentences 为句子列表，scores 为对应 TextRank 分数。"""
    sentences = split_sentences(text)
    n = len(sentences)
    if n == 0:
        return [], np.array([])
    if n == 1:
        return sentences, np.array([1.0])

    word_weight = _build_word_weights(text)

    # 构造句子向量（词权重累加，缺失词给极小权重）
    vecs = []
    for s in sentences:
        vec = {}
        for w in _tokenize(s):
            vec[w] = vec.get(w, 0.0) + word_weight.get(w, 0.01)
        vecs.append(vec)

    # 相似度矩阵
    sim = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            v = _cosine(vecs[i], vecs[j])
            sim[i][j] = sim[j][i] = v

    scores = _pagerank(sim)
    return sentences, scores


def summarize(text, topn=None):
    """生成摘要。topn 为摘要句数，默认按文本长度自适应（3~6 句）。"""
    sentences, scores = score_sentences(text)
    if not sentences:
        return ''
    if topn is None:
        topn = max(3, min(6, len(sentences) // 6))
    topn = max(1, min(topn, len(sentences)))

    # 取分数最高的 topn 个句子下标，按原文顺序还原
    ranked = np.argsort(-scores)[:topn]
    ordered = sorted(ranked.tolist())
    return ''.join(sentences[i] for i in ordered)
