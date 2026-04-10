"""
hardware 앱 뷰 — JY-SOFT 3셀 점자 모듈 제어

엔드포인트:
    POST /api/hardware/status/  — 연결 상태 확인
    POST /api/hardware/connect/ — 시리얼 포트 재연결
    POST /api/hardware/clear/   — 모든 점 끄기
    POST /api/hardware/send/    — 셀 패턴 직접 전송
    POST /api/hardware/send_text/ — 텍스트 → 점자 변환 → 3셀 순차 출력
"""
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serial_manager import BrailleHardwareManager, send_word_with_delay
from apps.braille.utils import text_to_braille


def _manager() -> BrailleHardwareManager:
    """settings의 SERIAL_PORT/BAUD로 매니저 초기화."""
    return BrailleHardwareManager(
        port=getattr(settings, "SERIAL_PORT", None),
        baud=getattr(settings, "SERIAL_BAUD", 9600),
    )


@api_view(["GET", "POST"])
def hw_status(request):
    m = _manager()
    return Response(
        {
            "port": m.port,
            "baud": m.baud,
            "connected": m.is_connected(),
        }
    )


@api_view(["POST"])
def connect(request):
    m = _manager()
    ok = m.connect()
    return Response(
        {"connected": ok, "port": m.port},
        status=status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@api_view(["POST"])
def clear(request):
    m = _manager()
    ok = m.clear()
    return Response(
        {"ok": ok},
        status=status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@api_view(["POST"])
def send(request):
    """
    요청: {"cells": [[1,0,0,0,0,0], [0,1,0,0,0,0], ...]}
    """
    cells = request.data.get("cells")
    if not isinstance(cells, list) or not cells:
        return Response(
            {"error": "cells (list of [p1..p6]) 필드가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        normalized = [[int(bool(x)) for x in cell[:6]] for cell in cells]
    except (TypeError, ValueError):
        return Response(
            {"error": "cells 원소는 6개 정수 배열이어야 합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    m = _manager()
    ok = m.send_cells(normalized)
    return Response(
        {"ok": ok, "sent_cells": len(normalized)},
        status=status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE,
    )


@api_view(["POST"])
def send_text(request):
    """
    요청: {"text": "사랑", "duration": 2.0}
    한글 텍스트를 점자로 변환해서 3셀씩 순차 출력.
    """
    text = request.data.get("text", "")
    duration = float(
        request.data.get(
            "duration", getattr(settings, "DEFAULT_CELL_DURATION_SEC", 2.0)
        )
    )

    if not isinstance(text, str) or not text.strip():
        return Response(
            {"error": "text 필드가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cells = text_to_braille(text)
    if not cells:
        return Response(
            {"error": "변환 가능한 점자 셀이 없습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ok = send_word_with_delay(cells, duration=duration)
    return Response(
        {
            "ok": ok,
            "text": text,
            "total_cells": len(cells),
            "chunks": (len(cells) + 2) // 3,
            "duration_per_chunk": duration,
        },
        status=status.HTTP_200_OK if ok else status.HTTP_503_SERVICE_UNAVAILABLE,
    )
