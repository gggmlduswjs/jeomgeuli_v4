"""
수학 모드 API

엔드포인트:
    POST /api/math/detect/   — 크롭 이미지 → CNN 감지 (text/formula)
    POST /api/math/explain/  — 수식 크롭 이미지 → Claude Vision 자연어 설명
"""
import os
import tempfile
from pathlib import Path

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .ml.formula_detector import FormulaDetector
from .pipeline import explain_formula


def _save_temp_image(image_file) -> str:
    suffix = Path(image_file.name).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        for chunk in image_file.chunks():
            tmp.write(chunk)
        return tmp.name


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def detect(request):
    """
    요청: multipart — image (file)
    응답: {"label": "formula"|"text", "confidence": 0.97}
    """
    image_file = request.FILES.get("image")
    if image_file is None:
        return Response(
            {"error": "image 파일이 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    path = _save_temp_image(image_file)
    try:
        weights = Path(settings.BASE_DIR) / "weights" / "formula_detector.pth"
        detector = FormulaDetector(weights_path=weights)
        label, conf = detector.predict(path)
        return Response({"label": label, "confidence": conf})
    except Exception as e:
        return Response(
            {"error": f"감지 실패: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def explain(request):
    """
    요청: multipart — image (file), 수식 크롭 이미지
    응답: {"explanation": "한국어 자연어 설명"}
    """
    image_file = request.FILES.get("image")
    if image_file is None:
        return Response(
            {"error": "image 파일이 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    path = _save_temp_image(image_file)
    try:
        text = explain_formula(path)
        return Response({"explanation": text})
    except Exception as e:
        return Response(
            {"error": f"Claude Vision 호출 실패: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
