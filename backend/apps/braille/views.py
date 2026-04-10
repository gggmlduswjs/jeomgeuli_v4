"""
점자 변환 API

Endpoints:
    POST /api/braille/convert          — 기존 v3 호환 (한 글자 단위)
    POST /api/braille/convert_text     — v4 신규 (문장 + 자모 분해)
    POST /api/braille/convert_word     — v4 신규 (단어 + 메타데이터)
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .utils import (
    braille_map,
    char_to_braille,
    text_to_braille,
    text_to_braille_with_meta,
    decompose_hangul,
)


@api_view(["POST"])
def convert_braille(request):
    """
    v3 호환: 문자 단위 하드코딩 룩업.
    새 코드는 convert_text 또는 convert_word 권장.
    """
    text = request.data.get("text", "")
    result = []
    for char in text:
        pattern = braille_map.get(char, [0, 0, 0, 0, 0, 0])
        result.append({"char": char, "pattern": pattern})
    return Response({"result": result})


@api_view(["POST"])
def convert_text(request):
    """
    v4: 한국 점자 표준 자모 분해 기반 변환.

    Request:
        { "text": "사랑해" }

    Response:
        {
            "text": "사랑해",
            "cells": [[0,0,0,0,0,1], [1,1,0,0,0,1], ...],
            "cell_count": 7
        }
    """
    text = request.data.get("text", "")
    if not text:
        return Response(
            {"error": "text 필드가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST
        )

    cells = text_to_braille(text)
    return Response({
        "text": text,
        "cells": cells,
        "cell_count": len(cells),
    })


@api_view(["POST"])
def convert_word(request):
    """
    v4: 단어 변환 + 자모별 메타데이터.
    훈련 세션에서 "이 셀이 어떤 글자의 어떤 자모인지" 필요할 때 사용.

    Request:
        { "text": "사랑" }

    Response:
        {
            "text": "사랑",
            "decomposition": [
                {"char": "사", "role": "choseong", "jamo": "ㅅ", "pattern": [...]},
                {"char": "사", "role": "jungseong", "jamo": "ㅏ", "pattern": [...]},
                {"char": "랑", "role": "choseong", "jamo": "ㄹ", "pattern": [...]},
                {"char": "랑", "role": "jungseong", "jamo": "ㅏ", "pattern": [...]},
                {"char": "랑", "role": "jongseong", "jamo": "ㅇ", "pattern": [...]}
            ],
            "cell_count": 5
        }
    """
    text = request.data.get("text", "")
    if not text:
        return Response(
            {"error": "text 필드가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST
        )

    decomposition = text_to_braille_with_meta(text)
    return Response({
        "text": text,
        "decomposition": decomposition,
        "cell_count": len(decomposition),
    })


@api_view(["POST"])
def decompose(request):
    """
    v4: 자모 분해만 (점자 변환 없이).
    디버깅·테스트용.

    Request:
        { "text": "사랑" }

    Response:
        {
            "text": "사랑",
            "decomposed": [
                {"char": "사", "cho": "ㅅ", "jung": "ㅏ", "jong": ""},
                {"char": "랑", "cho": "ㄹ", "jung": "ㅏ", "jong": "ㅇ"}
            ]
        }
    """
    text = request.data.get("text", "")
    if not text:
        return Response(
            {"error": "text 필드가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = []
    for char in text:
        cho, jung, jong = decompose_hangul(char)
        result.append({
            "char": char,
            "cho": cho or "",
            "jung": jung or "",
            "jong": jong or "",
        })

    return Response({
        "text": text,
        "decomposed": result,
    })
