"""
국어 지문 섹션 분류 (룰 기반)

지문 / 문제 / 보기 / 해설 구분.
CNN 분류기 없이 패턴 매칭으로 시작 (v4 초기 버전).

TODO v5: CNN 기반 레이아웃 분류기로 고도화
"""

import re
from typing import List, Dict
from enum import Enum


class SectionType(str, Enum):
    BODY = "body"          # 본문 지문
    QUESTION = "question"   # 문제 번호 + 문항
    CHOICE = "choice"       # 보기 (①②③④⑤)
    EXPLANATION = "explanation"  # 해설
    UNKNOWN = "unknown"


# 정규식 패턴
PATTERN_QUESTION_NUMBER = re.compile(r'^\d+[\.\)]\s')  # "1. " 또는 "1) "
PATTERN_CHOICE = re.compile(r'^[①②③④⑤⓵⓶⓷⓸⓹]')
PATTERN_EXPLANATION = re.compile(r'(정답|해설|풀이)\s*[:：]')


def classify_section(text: str) -> SectionType:
    """
    한 줄의 텍스트를 섹션 유형으로 분류.

    Args:
        text: 분류할 텍스트 한 줄

    Returns:
        SectionType
    """
    text = text.strip()
    if not text:
        return SectionType.UNKNOWN

    if PATTERN_CHOICE.match(text):
        return SectionType.CHOICE

    if PATTERN_QUESTION_NUMBER.match(text):
        return SectionType.QUESTION

    if PATTERN_EXPLANATION.search(text):
        return SectionType.EXPLANATION

    # 기본값: 본문
    return SectionType.BODY


def split_into_sections(lines: List[str]) -> List[Dict]:
    """
    텍스트 라인 리스트를 섹션별로 그룹화.

    Args:
        lines: OCR 결과 텍스트 라인들

    Returns:
        [
            {"type": "body", "text": "...여러 줄 본문..."},
            {"type": "question", "text": "1. 다음 중..."},
            {"type": "choice", "text": "① 첫 번째 보기"},
            ...
        ]
    """
    sections = []
    current_section = None

    for line in lines:
        line_type = classify_section(line)

        if current_section and current_section["type"] == line_type == SectionType.BODY:
            # 본문은 연속된 줄을 하나로 합침
            current_section["text"] += " " + line.strip()
        else:
            if current_section:
                sections.append(current_section)
            current_section = {
                "type": line_type.value,
                "text": line.strip(),
            }

    if current_section:
        sections.append(current_section)

    return sections


def extract_body_text(sections: List[Dict]) -> str:
    """
    섹션 리스트에서 본문만 추출하여 하나의 문자열로 반환.
    핵심어 추출의 입력으로 사용.
    """
    body_sections = [s["text"] for s in sections if s["type"] == SectionType.BODY.value]
    return "\n\n".join(body_sections)
