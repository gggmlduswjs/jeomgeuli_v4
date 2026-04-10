"""
핵심어 추출 (Sentence-BERT + TF-IDF 기반)

2가지 전략:
    1. TF-IDF 기반 중요도 (빠름, 의미 이해 X)
    2. Sentence-BERT 임베딩 기반 (느림, 의미 고려)

사용:
    extractor = VocabExtractor()
    keywords = extractor.extract("지문 내용...", top_k=12)
"""

from typing import List, Tuple
import re


class VocabExtractor:
    """핵심어 추출기"""

    def __init__(self, model_name: str = "jhgan/ko-sbert-nli"):
        self.model_name = model_name
        self._model = None

    def _ensure_model(self):
        """Sentence-BERT 지연 로드"""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def extract_tfidf(self, text: str, top_k: int = 12) -> List[Tuple[str, float]]:
        """
        TF-IDF 기반 핵심어 추출.

        Args:
            text: 분석할 텍스트
            top_k: 추출할 핵심어 수

        Returns:
            [(단어, 점수), ...] top_k개
        """
        from sklearn.feature_extraction.text import TfidfVectorizer

        # 문장 단위 분리 (TF-IDF는 문서 간 상대 빈도 기반이라 문장으로 분리 필요)
        sentences = re.split(r'[.!?]\s*', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            # 문장이 1개면 단어 빈도만 계산
            words = self._tokenize(text)
            from collections import Counter
            counter = Counter(words)
            return counter.most_common(top_k)

        vectorizer = TfidfVectorizer(
            tokenizer=self._tokenize,
            lowercase=False,
            token_pattern=None,
        )
        tfidf_matrix = vectorizer.fit_transform(sentences)

        # 평균 TF-IDF 점수
        import numpy as np
        avg_scores = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
        feature_names = vectorizer.get_feature_names_out()

        # 상위 k개
        top_indices = avg_scores.argsort()[-top_k:][::-1]
        return [(feature_names[i], float(avg_scores[i])) for i in top_indices]

    def extract_sbert(self, text: str, top_k: int = 12) -> List[Tuple[str, float]]:
        """
        Sentence-BERT 기반 핵심어 추출.

        각 후보 단어의 임베딩과 전체 지문 임베딩의 코사인 유사도로 점수화.

        Args:
            text: 분석할 텍스트
            top_k: 추출할 핵심어 수

        Returns:
            [(단어, 유사도), ...] top_k개
        """
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        model = self._ensure_model()

        # 후보 단어 (2~4글자 한국어 명사·대명사)
        candidates = self._extract_candidates(text)
        if not candidates:
            return []

        # 전체 지문 임베딩
        text_embedding = model.encode([text])

        # 각 후보 단어 임베딩
        candidate_embeddings = model.encode(candidates)

        # 코사인 유사도
        similarities = cosine_similarity(text_embedding, candidate_embeddings)[0]

        # 상위 k개
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [(candidates[i], float(similarities[i])) for i in top_indices]

    def extract(self, text: str, top_k: int = 12, strategy: str = "sbert") -> List[Tuple[str, float]]:
        """
        메인 추출 함수.

        Args:
            text: 분석할 텍스트
            top_k: 추출할 핵심어 수
            strategy: "sbert" (의미 기반) 또는 "tfidf" (빈도 기반)

        Returns:
            [(단어, 점수), ...] top_k개
        """
        if strategy == "sbert":
            return self.extract_sbert(text, top_k)
        elif strategy == "tfidf":
            return self.extract_tfidf(text, top_k)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _tokenize(self, text: str) -> List[str]:
        """
        간단 한국어 토큰화 (띄어쓰기 기준).
        TODO v5: KoNLPy (Mecab, Okt 등) 사용
        """
        return [w for w in re.split(r'\s+', text) if len(w) >= 2]

    def _extract_candidates(self, text: str, min_len: int = 2, max_len: int = 6) -> List[str]:
        """
        후보 단어 추출 (중복 제거).
        TODO v5: 형태소 분석 기반으로 명사만 추출
        """
        words = self._tokenize(text)
        candidates = set()
        for word in words:
            # 한글만 포함, 길이 제한
            cleaned = re.sub(r'[^가-힣]', '', word)
            if min_len <= len(cleaned) <= max_len:
                candidates.add(cleaned)
        return list(candidates)
