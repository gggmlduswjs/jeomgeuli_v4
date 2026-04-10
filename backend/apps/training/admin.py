from django.contrib import admin
from .models import Session, WordAttempt


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "level",
        "total_words",
        "correct_count",
        "avg_response_ms",
        "created_at",
        "finished_at",
    )
    list_filter = ("level",)


@admin.register(WordAttempt)
class WordAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "index",
        "word",
        "user_answer",
        "is_correct",
        "response_ms",
    )
    list_filter = ("is_correct",)
    search_fields = ("word", "user_answer")
