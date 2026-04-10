"""
jeomgeuli v4 URL 라우팅

국어 모드 (메인):
  /api/braille/    — 점자 변환
  /api/textbook/   — 지문 OCR + 섹션 분류
  /api/vocabulary/ — 핵심어 추출
  /api/training/   — 훈련 세션
  /api/hardware/   — 3셀 하드웨어 제어

수학 모드 (데모):
  /api/math/       — CNN 수식 감지 + Claude Vision 설명
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/braille/', include('apps.braille.urls')),
    path('api/textbook/', include('apps.textbook.urls')),
    path('api/vocabulary/', include('apps.vocabulary.urls')),
    path('api/training/', include('apps.training.urls')),
    path('api/hardware/', include('apps.hardware.urls')),
    path('api/math/', include('apps.math_demo.urls')),
]
