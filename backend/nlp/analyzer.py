# -*- coding: utf-8 -*-
"""综合分析器：串联分段、分句、摘要、关键词、词频与段落分析，产出统一结果。"""
import re

import numpy as np

from .text_processor import split_paragraphs, split_sentences
from .summarizer import score_sentences, summarize
from .keyword_extract import extract_keywords, word_frequency


def _minmax_normalize(values):
    """将分数归一化到 0~100（保留两位小数）。"""
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return []
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return [round(100.0 if arr.size == 1 else 50.0, 2) for _ in arr]
    return [round(float((v - lo) / (hi - lo) * 100.0), 2) for v in arr]


class PaperAnalyzer:
    """对一篇论文文本执行完整分析，输出结构化结果。"""

    def __init__(self, raw_text):
        self.raw_text = raw_text or ''
        self.paragraphs = split_paragraphs(self.raw_text)
        # 连续文本：用于句子级评分与关键词/摘要
        self.continuous = re.sub(r'\s+', ' ', ' '.join(self.paragraphs)).strip()

    def run(self):
        result = {
            'stats': self._stats(),
            'summary': self._summary(),
            'keywords': extract_keywords(self.continuous, topk=20),
            'word_freq': word_frequency(self.continuous, topk=30),
            'paragraphs': self._paragraph_analysis(),
        }
        return result

    def _stats(self):
        sentences = split_sentences(self.continuous)
        return {
            'para_count': len(self.paragraphs),
            'sentence_count': len(sentences),
            'char_count': len(self.continuous),
        }

    def _summary(self):
        return summarize(self.continuous)

    def _paragraph_analysis(self):
        sentences, scores = score_sentences(self.continuous)
        sent_score = dict(zip(sentences, scores))

        items = []
        for idx, para in enumerate(self.paragraphs, start=1):
            para_sentences = split_sentences(para)
            if not para_sentences:
                continue
            raw_scores = [sent_score.get(s, 0.0) for s in para_sentences]
            # 关键句：取句子分数最高的句子
            best = para_sentences[int(np.argmax(raw_scores))] if raw_scores else ''
            items.append({
                'para_no': idx,
                'content': para,
                'sentence_count': len(para_sentences),
                'char_count': len(para),
                'score': float(round(float(sum(raw_scores)), 6)),
                'key_sentence': best,
            })

        # 段落重要度归一化到 0~100
        if items:
            norm = _minmax_normalize([it['score'] for it in items])
            for it, nv in zip(items, norm):
                it['score'] = nv
        return items
