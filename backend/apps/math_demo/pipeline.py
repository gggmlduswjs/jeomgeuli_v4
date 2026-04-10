"""
수학 페이지 처리 파이프라인 (LangChain LCEL)

흐름:
    1) 수학 페이지 이미지 + 후보 크롭 리스트
    2) FormulaDetector (CNN)로 "formula" 크롭만 필터
    3) 각 수식 크롭을 Claude Vision에 보내 자연어 설명 생성
    4) TTS 입력용 텍스트 반환 (gTTS는 프론트/다른 엔드포인트에서)

Claude Vision 호출은 LangChain LCEL 체인:
    prompt | ChatAnthropic | StrOutputParser
"""
import base64
import os
from pathlib import Path
from typing import List, Dict, Union

from django.conf import settings


VISION_SYSTEM_PROMPT = (
    "당신은 시각장애 수험생을 위한 수학 튜터입니다. "
    "수식 이미지를 보고 한국어로 자연스럽게 읽어주세요. "
    "규칙: "
    "1) 기호는 한국어로 풀어 읽습니다 (예: ∫ → '적분', Σ → '시그마', √ → '루트'). "
    "2) 상첨자·하첨자는 '제곱', '의' 등으로 풀어 설명합니다. "
    "3) 전체 식의 의미를 한 문장으로 요약합니다. "
    "4) TTS로 바로 들려줄 수 있게 자연스러운 음성 친화적 문장으로 작성합니다."
)


def _image_to_base64(image_path: Union[str, Path]) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def explain_formula(image_path: Union[str, Path]) -> str:
    """
    수식 이미지 1개 → Claude Vision 자연어 설명.

    LangChain LCEL 체인 사용.
    """
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.output_parsers import StrOutputParser

    api_key = getattr(settings, "ANTHROPIC_API_KEY", "") or os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")

    b64 = _image_to_base64(image_path)
    suffix = Path(image_path).suffix.lower().lstrip(".")
    media_type = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(suffix, "image/jpeg")

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=api_key,
        max_tokens=512,
        temperature=0.2,
    )

    messages = [
        SystemMessage(content=VISION_SYSTEM_PROMPT),
        HumanMessage(
            content=[
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64,
                    },
                },
                {
                    "type": "text",
                    "text": "이 수식을 시각장애 수험생이 음성으로 이해할 수 있게 한국어로 읽어주세요.",
                },
            ]
        ),
    ]

    chain = llm | StrOutputParser()
    return chain.invoke(messages)


def process_math_page(page_image_path: str, crop_paths: List[str]) -> List[Dict]:
    """
    수학 페이지 + 후보 크롭 리스트 → 수식 감지 + 설명.

    Args:
        page_image_path: 원본 페이지 이미지 (현재는 참고용)
        crop_paths: 후보 영역 크롭 이미지 경로들

    Returns:
        [
            {
                "crop_path": "...",
                "label": "formula" | "text",
                "confidence": 0.97,
                "explanation": "..." (formula일 때만)
            },
            ...
        ]
    """
    from .ml.formula_detector import FormulaDetector

    weights = Path(settings.BASE_DIR) / "weights" / "formula_detector.pth"
    detector = FormulaDetector(weights_path=weights)

    results = []
    for crop_path in crop_paths:
        label, conf = detector.predict(crop_path)
        entry = {
            "crop_path": str(crop_path),
            "label": label,
            "confidence": conf,
        }
        if label == "formula":
            try:
                entry["explanation"] = explain_formula(crop_path)
            except Exception as e:
                entry["explanation"] = None
                entry["error"] = f"Claude Vision 호출 실패: {e}"
        results.append(entry)

    return results
