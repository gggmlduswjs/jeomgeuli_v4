"""
훈련 세션 API

흐름:
    1) POST /api/training/sessions/           세션 생성 (level, source_text)
    2) POST /api/training/sessions/{id}/show/ 단어 표시 (text → 점자 → 하드웨어)
    3) POST /api/training/sessions/{id}/answer/ 답변 채점 (Whisper STT는 프론트에서)
    4) POST /api/training/sessions/{id}/finish/ 세션 종료 + 집계
    5) GET  /api/training/sessions/{id}/      리포트 조회
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.braille.utils import text_to_braille
from apps.hardware.serial_manager import send_word_with_delay

from .models import Session, WordAttempt
from .serializers import SessionSerializer, WordAttemptSerializer


@api_view(["POST"])
def create_session(request):
    """
    요청: {"level": 1, "cell_duration_sec": 2.0, "source_text": "..."}
    """
    level = int(request.data.get("level", 1))
    duration = float(request.data.get("cell_duration_sec", 2.0))
    source_text = request.data.get("source_text", "")

    if level not in (1, 2, 3, 4):
        return Response(
            {"error": "level은 1~4여야 합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    session = Session.objects.create(
        level=level,
        cell_duration_sec=duration,
        source_text=source_text,
    )
    return Response(
        SessionSerializer(session).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def get_session(request, session_id: int):
    session = get_object_or_404(Session, pk=session_id)
    return Response(SessionSerializer(session).data)


@api_view(["POST"])
def show_word(request, session_id: int):
    """
    단어를 점자로 변환 → 3셀 하드웨어에 출력 → 시도 레코드 생성.

    요청: {"word": "사랑", "send_hardware": true}
    응답: 생성된 WordAttempt + 출력된 braille_cells
    """
    session = get_object_or_404(Session, pk=session_id)
    word = request.data.get("word", "").strip()
    send_hw = bool(request.data.get("send_hardware", True))

    if not word:
        return Response(
            {"error": "word 필드가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cells = text_to_braille(word)
    if not cells:
        return Response(
            {"error": f"'{word}'를 점자로 변환할 수 없습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 다음 인덱스
    next_index = session.attempts.count()
    attempt = WordAttempt.objects.create(
        session=session,
        index=next_index,
        word=word,
        braille_cells=cells,
    )

    hw_ok = None
    if send_hw:
        hw_ok = send_word_with_delay(cells, duration=session.cell_duration_sec)

    return Response(
        {
            "attempt": WordAttemptSerializer(attempt).data,
            "hardware_sent": hw_ok,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def submit_answer(request, session_id: int):
    """
    요청: {
        "attempt_id": 123,
        "user_answer": "사랑",
        "response_ms": 1842,
        "whisper_logprob": -0.12
    }
    """
    session = get_object_or_404(Session, pk=session_id)

    attempt_id = request.data.get("attempt_id")
    user_answer = request.data.get("user_answer", "").strip()
    response_ms = request.data.get("response_ms")
    logprob = request.data.get("whisper_logprob")

    if attempt_id is None:
        return Response(
            {"error": "attempt_id 필드가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    attempt = get_object_or_404(
        WordAttempt,
        pk=attempt_id,
        session=session,
    )

    attempt.user_answer = user_answer
    attempt.is_correct = user_answer == attempt.word
    if response_ms is not None:
        attempt.response_ms = int(response_ms)
    if logprob is not None:
        attempt.whisper_logprob = float(logprob)
    attempt.save()

    return Response(WordAttemptSerializer(attempt).data)


@api_view(["POST"])
def finish_session(request, session_id: int):
    """세션 종료 + 집계 (정답 수, 평균 반응 시간)."""
    session = get_object_or_404(Session, pk=session_id)

    attempts = list(session.attempts.all())
    session.total_words = len(attempts)
    session.correct_count = sum(1 for a in attempts if a.is_correct)

    timed = [a.response_ms for a in attempts if a.response_ms is not None]
    session.avg_response_ms = sum(timed) / len(timed) if timed else None

    session.finished_at = timezone.now()
    session.save()

    return Response(SessionSerializer(session).data)
