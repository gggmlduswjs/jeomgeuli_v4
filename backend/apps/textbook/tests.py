"""
textbook 앱 단위 테스트

외부 의존성 없는 부분(섹션 파서 룰)만 커버한다.
EasyOCR 실제 호출 테스트는 CI에서 의존성·시간·모델 다운로드 부담으로 제외.
"""
from django.test import TestCase

from .parser import (
    SectionType,
    classify_section,
    extract_body_text,
    split_into_sections,
)


class ClassifySectionTest(TestCase):
    def test_body_default(self):
        """룰 매칭 안 되는 줄은 본문"""
        self.assertEqual(
            classify_section("이것은 평범한 본문 한 줄입니다."),
            SectionType.BODY,
        )

    def test_question_number_dot(self):
        self.assertEqual(
            classify_section("1. 다음 중 가장 적절한 것은?"),
            SectionType.QUESTION,
        )

    def test_question_number_paren(self):
        self.assertEqual(
            classify_section("2) 윗글의 내용으로 옳은 것은?"),
            SectionType.QUESTION,
        )

    def test_choice_circled_numbers(self):
        for ch in ["①", "②", "③", "④", "⑤"]:
            with self.subTest(choice=ch):
                self.assertEqual(
                    classify_section(f"{ch} 첫 번째 보기"),
                    SectionType.CHOICE,
                )

    def test_explanation_keyword(self):
        self.assertEqual(
            classify_section("해설: 이 문제의 정답은 ②번이다."),
            SectionType.EXPLANATION,
        )
        self.assertEqual(
            classify_section("정답: ③"),
            SectionType.EXPLANATION,
        )

    def test_empty_line(self):
        self.assertEqual(classify_section(""), SectionType.UNKNOWN)
        self.assertEqual(classify_section("   "), SectionType.UNKNOWN)


class SplitIntoSectionsTest(TestCase):
    def test_merges_consecutive_body_lines(self):
        """본문 연속 줄은 하나의 섹션으로 병합"""
        lines = [
            "문학 작품의 해석은 다양하다.",
            "독자의 경험이 개입된다.",
            "시대적 배경도 중요하다.",
        ]
        sections = split_into_sections(lines)
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0]["type"], "body")
        self.assertIn("문학", sections[0]["text"])
        self.assertIn("시대적", sections[0]["text"])

    def test_splits_at_question(self):
        lines = [
            "본문 한 줄.",
            "1. 첫 번째 문제",
            "① 보기 하나",
            "② 보기 둘",
        ]
        sections = split_into_sections(lines)
        types = [s["type"] for s in sections]
        self.assertEqual(types, ["body", "question", "choice", "choice"])

    def test_returns_empty_for_empty_input(self):
        self.assertEqual(split_into_sections([]), [])


class ExtractBodyTextTest(TestCase):
    def test_joins_only_body_sections(self):
        sections = [
            {"type": "body", "text": "본문 단락 1"},
            {"type": "question", "text": "1. 문제"},
            {"type": "body", "text": "본문 단락 2"},
            {"type": "choice", "text": "① 보기"},
        ]
        body = extract_body_text(sections)
        self.assertIn("본문 단락 1", body)
        self.assertIn("본문 단락 2", body)
        self.assertNotIn("문제", body)
        self.assertNotIn("보기", body)

    def test_no_body_returns_empty(self):
        sections = [
            {"type": "question", "text": "1. 문제"},
            {"type": "choice", "text": "① 보기"},
        ]
        self.assertEqual(extract_body_text(sections), "")
