"""
vocabulary 앱 뷰 — 핵심어 추출

POST /api/vocabulary/extract/
    {"text": "...", "top_k": 12, "strategy": "sbert"|"tfidf"}
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .extractor import VocabExtractor

# 싱글톤 인스턴스 (SBERT 모델 재사용)
_extractor = VocabExtractor()


@api_view(["POST"])
def extract(request):
    text = request.data.get("text", "")
    top_k = int(request.data.get("top_k", 12))
    strategy = request.data.get("strategy", "sbert")

    if not isinstance(text, str) or not text.strip():
        return Response(
            {"error": "text 필드가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if strategy not in ("sbert", "tfidf"):
        return Response(
            {"error": "strategy는 'sbert' 또는 'tfidf'여야 합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        keywords = _extractor.extract(text, top_k=top_k, strategy=strategy)
    except Exception as e:
        return Response(
            {"error": f"핵심어 추출 실패: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "strategy": strategy,
            "keywords": [
                {"word": word, "score": score} for word, score in keywords
            ],
        }
    )
