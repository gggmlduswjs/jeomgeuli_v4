from rest_framework import serializers
from .models import Session, WordAttempt


class WordAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordAttempt
        fields = [
            "id",
            "index",
            "word",
            "braille_cells",
            "user_answer",
            "is_correct",
            "response_ms",
            "whisper_logprob",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SessionSerializer(serializers.ModelSerializer):
    attempts = WordAttemptSerializer(many=True, read_only=True)
    accuracy = serializers.FloatField(read_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "source_text",
            "level",
            "cell_duration_sec",
            "total_words",
            "correct_count",
            "avg_response_ms",
            "accuracy",
            "created_at",
            "finished_at",
            "attempts",
        ]
        read_only_fields = [
            "id",
            "total_words",
            "correct_count",
            "avg_response_ms",
            "created_at",
            "finished_at",
        ]
