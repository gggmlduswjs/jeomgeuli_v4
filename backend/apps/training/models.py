"""
훈련 세션 데이터 모델

흐름:
    Session (1회 훈련)
      ├── WordAttempt (핵심어 1개 시도)
      │     - 하드웨어에 3셀 출력
      │     - 사용자가 음성으로 답변 (Whisper STT)
      │     - 정답 여부 + 반응 시간 기록
      └── ...
"""
from django.db import models


class Session(models.Model):
    """훈련 세션 1회"""

    LEVEL_CHOICES = [
        (1, "Level 1 — 2자 단어 / 3.0s"),
        (2, "Level 2 — 3자 단어 / 2.5s"),
        (3, "Level 3 — 3자 단어 / 2.0s"),
        (4, "Level 4 — 4자+ / 1.5s"),
    ]

    source_text = models.TextField(
        blank=True,
        help_text="이 세션의 원본 지문 (OCR 결과)",
    )
    level = models.IntegerField(choices=LEVEL_CHOICES, default=1)
    cell_duration_sec = models.FloatField(default=2.0)

    # 집계 (종료 시 갱신)
    total_words = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    avg_response_ms = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Session #{self.pk} Lv{self.level} ({self.created_at:%Y-%m-%d %H:%M})"

    @property
    def accuracy(self) -> float:
        if self.total_words == 0:
            return 0.0
        return self.correct_count / self.total_words


class WordAttempt(models.Model):
    """세션 내 단어 1개 시도"""

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    index = models.IntegerField(help_text="세션 내 순번 (0-base)")

    word = models.CharField(max_length=32, help_text="출제 단어")
    braille_cells = models.JSONField(
        help_text="[[p1..p6], ...] 실제 출력된 점자 셀 배열",
    )

    # 답변
    user_answer = models.CharField(max_length=64, blank=True)
    is_correct = models.BooleanField(default=False)
    response_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="출력 완료 시점~답변 수신까지 ms",
    )
    whisper_logprob = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["session", "index"]
        unique_together = [("session", "index")]

    def __str__(self):
        mark = "O" if self.is_correct else "X"
        return f"[{mark}] {self.word} (sess {self.session_id} #{self.index})"
