"""
vocabulary 앱 단위 테스트

- extract_tfidf: sklearn 기반, 빠름. CI에서 실행.
- extract_sbert: sentence-transformers ~500MB 모델. CI에서는 skip.
"""
from django.test import TestCase

from .extractor import VocabExtractor


SAMPLE_TEXT = (
    "문학 작품의 해석은 독자의 경험에 따라 달라진다. "
    "특히 상징과 은유가 풍부한 시는 다양한 해석의 여지를 남긴다. "
    "작가의 의도를 완전히 파악하기는 어렵지만 텍스트 안에서 근거를 찾는 것이 중요하다. "
    "비평가들은 시대적 맥락을 함께 고려하여 해석의 폭을 넓힌다."
)


class VocabExtractorTfidfTest(TestCase):
    def test_tfidf_returns_topk(self):
        extractor = VocabExtractor()
        result = extractor.extract_tfidf(SAMPLE_TEXT, top_k=5)
        self.assertEqual(len(result), 5)
        for word, score in result:
            self.assertIsInstance(word, str)
            self.assertGreaterEqual(score, 0.0)

    def test_tfidf_scores_descending(self):
        extractor = VocabExtractor()
        result = extractor.extract_tfidf(SAMPLE_TEXT, top_k=10)
        scores = [score for _, score in result]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_tokenize_filters_short_words(self):
        extractor = VocabExtractor()
        tokens = extractor._tokenize("나는 학교에 간다 하늘이")
        # 1글자 단어 '나'는 제외, 2글자 이상만 포함
        self.assertTrue(all(len(t) >= 2 for t in tokens))

    def test_candidates_only_hangul(self):
        extractor = VocabExtractor()
        candidates = extractor._extract_candidates("문학 작품과 literature 2024년")
        # 한글만 포함
        for c in candidates:
            self.assertTrue(all("\uac00" <= ch <= "\ud7a3" for ch in c))

    def test_extract_dispatches_strategy(self):
        extractor = VocabExtractor()
        result = extractor.extract(SAMPLE_TEXT, top_k=3, strategy="tfidf")
        self.assertEqual(len(result), 3)

    def test_extract_invalid_strategy_raises(self):
        extractor = VocabExtractor()
        with self.assertRaises(ValueError):
            extractor.extract(SAMPLE_TEXT, strategy="unknown")

    def test_extract_single_sentence_falls_back_to_counter(self):
        """문장 1개인 경우 단어 빈도 카운터로 폴백"""
        extractor = VocabExtractor()
        result = extractor.extract_tfidf("문학 해석 독자 문학 해석", top_k=3)
        # Counter 폴백이 동작했으면 빈도 기반 결과가 나온다
        words = [w for w, _ in result]
        self.assertIn("문학", words)
        self.assertIn("해석", words)


class VocabularyViewTest(TestCase):
    def test_extract_endpoint_returns_keywords(self):
        from rest_framework.test import APIClient

        client = APIClient()
        res = client.post(
            "/api/vocabulary/extract/",
            {"text": SAMPLE_TEXT, "top_k": 5, "strategy": "tfidf"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["strategy"], "tfidf")
        self.assertEqual(len(data["keywords"]), 5)
        for kw in data["keywords"]:
            self.assertIn("word", kw)
            self.assertIn("score", kw)

    def test_extract_endpoint_rejects_empty_text(self):
        from rest_framework.test import APIClient

        client = APIClient()
        res = client.post(
            "/api/vocabulary/extract/",
            {"text": "", "top_k": 5},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_extract_endpoint_rejects_unknown_strategy(self):
        from rest_framework.test import APIClient

        client = APIClient()
        res = client.post(
            "/api/vocabulary/extract/",
            {"text": SAMPLE_TEXT, "strategy": "bogus"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
