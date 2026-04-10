"""
training 앱 테스트 — 세션 CRUD + 단어 제출 + 채점 + finish 집계.

send_hardware=False 로 설정해서 실제 Arduino 연결 없이 흐름만 검증.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Session, WordAttempt


class SessionModelTest(TestCase):
    def test_create_session_defaults(self):
        s = Session.objects.create()
        self.assertEqual(s.level, 1)
        self.assertEqual(s.total_words, 0)
        self.assertEqual(s.correct_count, 0)
        self.assertIsNone(s.finished_at)

    def test_accuracy_zero_when_no_words(self):
        s = Session.objects.create()
        self.assertEqual(s.accuracy, 0.0)

    def test_accuracy_computed_from_counts(self):
        s = Session.objects.create(total_words=10, correct_count=7)
        self.assertAlmostEqual(s.accuracy, 0.7)


class WordAttemptModelTest(TestCase):
    def test_unique_session_index(self):
        s = Session.objects.create()
        WordAttempt.objects.create(
            session=s, index=0, word="사랑", braille_cells=[[1, 0, 0, 0, 0, 0]]
        )
        with self.assertRaises(Exception):  # IntegrityError
            WordAttempt.objects.create(
                session=s, index=0, word="다른단어", braille_cells=[]
            )


class SessionFlowViewTest(TestCase):
    """전체 세션 흐름: create → show → answer → finish"""

    def setUp(self):
        self.client = APIClient()

    def test_create_session(self):
        res = self.client.post(
            "/api/training/sessions/",
            {"level": 2, "cell_duration_sec": 2.5, "source_text": "테스트 지문"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["level"], 2)
        self.assertEqual(data["cell_duration_sec"], 2.5)
        self.assertEqual(data["total_words"], 0)

    def test_create_session_rejects_invalid_level(self):
        res = self.client.post(
            "/api/training/sessions/",
            {"level": 99},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_show_word_creates_attempt_without_hardware(self):
        create = self.client.post(
            "/api/training/sessions/",
            {"level": 1},
            format="json",
        )
        sid = create.json()["id"]

        res = self.client.post(
            f"/api/training/sessions/{sid}/show/",
            {"word": "사랑", "send_hardware": False},
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["attempt"]["word"], "사랑")
        self.assertEqual(data["attempt"]["index"], 0)
        # "사랑" = 사(약자 1) + 랑(ㄹ+ㅏ+ㅇ 3) = 4셀
        self.assertEqual(len(data["attempt"]["braille_cells"]), 4)
        self.assertIsNone(data["hardware_sent"])

    def test_show_word_rejects_empty(self):
        sid = self.client.post("/api/training/sessions/", {"level": 1}, format="json").json()["id"]
        res = self.client.post(
            f"/api/training/sessions/{sid}/show/",
            {"word": ""},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_show_word_index_increments(self):
        sid = self.client.post("/api/training/sessions/", {"level": 1}, format="json").json()["id"]

        first = self.client.post(
            f"/api/training/sessions/{sid}/show/",
            {"word": "문학", "send_hardware": False},
            format="json",
        ).json()
        second = self.client.post(
            f"/api/training/sessions/{sid}/show/",
            {"word": "해석", "send_hardware": False},
            format="json",
        ).json()

        self.assertEqual(first["attempt"]["index"], 0)
        self.assertEqual(second["attempt"]["index"], 1)

    def test_submit_answer_correct(self):
        sid = self.client.post("/api/training/sessions/", {"level": 1}, format="json").json()["id"]
        attempt_id = self.client.post(
            f"/api/training/sessions/{sid}/show/",
            {"word": "사랑", "send_hardware": False},
            format="json",
        ).json()["attempt"]["id"]

        res = self.client.post(
            f"/api/training/sessions/{sid}/answer/",
            {"attempt_id": attempt_id, "user_answer": "사랑", "response_ms": 1800},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["is_correct"])
        self.assertEqual(data["response_ms"], 1800)

    def test_submit_answer_incorrect(self):
        sid = self.client.post("/api/training/sessions/", {"level": 1}, format="json").json()["id"]
        attempt_id = self.client.post(
            f"/api/training/sessions/{sid}/show/",
            {"word": "사랑", "send_hardware": False},
            format="json",
        ).json()["attempt"]["id"]

        res = self.client.post(
            f"/api/training/sessions/{sid}/answer/",
            {"attempt_id": attempt_id, "user_answer": "사량"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["is_correct"])

    def test_finish_session_aggregates(self):
        """단어 2개 제출 후 finish 집계"""
        sid = self.client.post("/api/training/sessions/", {"level": 1}, format="json").json()["id"]

        words = ["문학", "해석"]
        answers = ["문학", "틀림"]
        expected_correct = 1
        response_times = [1500, 2300]

        for word, answer, rt in zip(words, answers, response_times):
            attempt_id = self.client.post(
                f"/api/training/sessions/{sid}/show/",
                {"word": word, "send_hardware": False},
                format="json",
            ).json()["attempt"]["id"]
            self.client.post(
                f"/api/training/sessions/{sid}/answer/",
                {"attempt_id": attempt_id, "user_answer": answer, "response_ms": rt},
                format="json",
            )

        res = self.client.post(f"/api/training/sessions/{sid}/finish/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_words"], 2)
        self.assertEqual(data["correct_count"], expected_correct)
        self.assertAlmostEqual(data["accuracy"], 0.5)
        self.assertAlmostEqual(data["avg_response_ms"], sum(response_times) / 2)
        self.assertIsNotNone(data["finished_at"])

    def test_get_session_returns_attempts(self):
        sid = self.client.post("/api/training/sessions/", {"level": 1}, format="json").json()["id"]
        self.client.post(
            f"/api/training/sessions/{sid}/show/",
            {"word": "사랑", "send_hardware": False},
            format="json",
        )
        res = self.client.get(f"/api/training/sessions/{sid}/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["attempts"]), 1)
        self.assertEqual(data["attempts"][0]["word"], "사랑")

    def test_get_nonexistent_session_404(self):
        res = self.client.get("/api/training/sessions/99999/")
        self.assertEqual(res.status_code, 404)
