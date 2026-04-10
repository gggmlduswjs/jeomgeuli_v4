"""
textbook 앱 뷰 — 국어 지문 이미지 → OCR → 섹션 분류
"""
import os
import tempfile
from pathlib import Path

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .ocr import KoreanOCR, preprocess_image
from .parser import classify_section, split_into_sections, extract_body_text


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def extract(request):
    """
    이미지 업로드 → 한국어 OCR → 섹션 분류.

    요청:
        multipart/form-data: image (file), preprocess ("true"/"false")

    응답:
        {
            "raw_lines": ["줄1", "줄2", ...],
            "sections": [{"type": "body"|"question"|..., "text": "..."}, ...],
            "body_text": "본문만 합친 문자열"
        }
    """
    image_file = request.FILES.get("image")
    if image_file is None:
        return Response(
            {"error": "image 파일이 필요합니다 (multipart/form-data)."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    do_preprocess = str(request.data.get("preprocess", "false")).lower() == "true"

    # 임시 파일로 저장
    suffix = Path(image_file.name).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        for chunk in image_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        target_path = tmp_path
        if do_preprocess:
            pre_path = tmp_path + ".pre.png"
            preprocess_image(tmp_path, pre_path)
            target_path = pre_path

        ocr = KoreanOCR()
        results = ocr.extract_text(target_path)  # [(text, conf), ...]
        lines = [text for text, _ in results]

        sections = split_into_sections(lines)
        body_text = extract_body_text(sections)

        return Response(
            {
                "raw_lines": lines,
                "sections": sections,
                "body_text": body_text,
            }
        )
    except Exception as e:
        return Response(
            {"error": f"OCR 처리 실패: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


@api_view(["POST"])
def classify(request):
    """
    텍스트 한 줄 분류 (디버깅/UI 프리뷰용).

    요청: {"text": "1. 다음 글을 읽고 ..."}
    응답: {"type": "question"}
    """
    text = request.data.get("text", "")
    if not isinstance(text, str):
        return Response({"error": "text는 문자열이어야 합니다."}, status=400)
    return Response({"type": classify_section(text).value})
