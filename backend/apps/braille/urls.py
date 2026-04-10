"""
점자 변환 API URL 라우팅

경로:
    /api/braille/convert          — v3 호환 (하드코딩 룩업)
    /api/braille/convert_text     — v4 자모 분해 기반 변환
    /api/braille/convert_word     — v4 단어 + 메타데이터
    /api/braille/decompose        — 자모 분해만 (디버깅용)
"""

from django.urls import path
from .views import (
    convert_braille,
    convert_text,
    convert_word,
    decompose,
)

urlpatterns = [
    path('convert/', convert_braille, name='convert_braille'),
    path('convert_text/', convert_text, name='convert_text'),
    path('convert_word/', convert_word, name='convert_word'),
    path('decompose/', decompose, name='decompose'),
]
