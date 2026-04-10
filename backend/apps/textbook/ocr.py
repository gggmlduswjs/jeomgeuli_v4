"""
한국어 OCR 래퍼 (EasyOCR 기반)

용도:
    - 국어 수능특강 지문 페이지 → 텍스트 추출
    - 수학 수능특강 페이지 → 텍스트 추출 (math_demo 앱과 공유)

설치:
    pip install easyocr opencv-python Pillow

⚠️ 첫 실행 시 EasyOCR이 모델 다운로드함 (약 100MB)
"""

from typing import List, Tuple, Optional
import cv2
import numpy as np
from pathlib import Path


class KoreanOCR:
    """EasyOCR 한국어 래퍼 (싱글톤)"""

    _instance: Optional["KoreanOCR"] = None
    _reader = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _ensure_reader(self):
        """지연 로드 (첫 사용 시만 초기화).

        verbose=False: Windows cp949 콘솔에서 progress bar(\u2588) 인코딩
        실패를 방지.
        """
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(['ko'], gpu=False, verbose=False)
        return self._reader

    def extract_text(self, image_path: str) -> List[Tuple[str, float]]:
        """
        이미지에서 한국어 텍스트 추출.

        Args:
            image_path: 이미지 파일 경로

        Returns:
            [(텍스트, 신뢰도), ...] 리스트
        """
        reader = self._ensure_reader()
        results = reader.readtext(image_path, detail=1)

        # detail=1일 때 반환: [(bbox, text, confidence), ...]
        return [(text, confidence) for _, text, confidence in results]

    def extract_text_with_boxes(self, image_path: str) -> List[dict]:
        """
        이미지에서 텍스트 + 위치 정보 추출.

        Returns:
            [{"text": str, "bbox": [[x1,y1],...], "confidence": float}, ...]
        """
        reader = self._ensure_reader()
        results = reader.readtext(image_path, detail=1)
        return [
            {"text": text, "bbox": bbox, "confidence": conf}
            for bbox, text, conf in results
        ]


def preprocess_image(image_path: str, output_path: Optional[str] = None) -> np.ndarray:
    """
    OCR 전 이미지 전처리.

    - 그레이스케일 변환
    - 대비 향상 (CLAHE)
    - 노이즈 제거
    - (옵션) 원근 보정

    Args:
        image_path: 입력 이미지 경로
        output_path: 저장 경로 (없으면 반환만)

    Returns:
        전처리된 이미지 (numpy array)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"이미지를 읽을 수 없음: {image_path}")

    # 그레이스케일
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE로 대비 향상
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 노이즈 제거 (Bilateral filter)
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)

    if output_path:
        cv2.imwrite(output_path, denoised)

    return denoised
