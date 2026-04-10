"""
ResNet18 Transfer Learning 수식 감지기

2-class 분류기:
    class 0 = text (본문)
    class 1 = formula (수식)

입력:
    수학 페이지에서 잘라낸 후보 크롭 (PIL Image 또는 경로)

출력:
    (label: str, confidence: float)

학습 노트북:
    backend/ml_experiments/formula_detector_train.ipynb (Day 6 작업)
학습 데이터:
    backend/data/math_raw/01_formula/*.jpg
    backend/data/math_raw/02_text/*.jpg
가중치:
    backend/weights/formula_detector.pth
"""
from pathlib import Path
from typing import List, Tuple, Optional, Union

CLASS_NAMES = ["text", "formula"]

# ImageNet 통계 (ResNet 사전학습 기준)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def _build_model(num_classes: int = 2):
    """ResNet18 + 마지막 fc 교체."""
    import torch.nn as nn
    from torchvision.models import resnet18

    model = resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


def _build_transform():
    from torchvision import transforms
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


class FormulaDetector:
    """수식 감지기 (싱글톤)"""

    _instance: Optional["FormulaDetector"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, weights_path: Optional[Union[str, Path]] = None):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self.weights_path = Path(weights_path) if weights_path else None
        self._model = None
        self._transform = None
        self._device = None

    def _ensure_loaded(self):
        if self._model is not None:
            return
        import torch

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = _build_model(num_classes=len(CLASS_NAMES)).to(self._device)

        if self.weights_path and self.weights_path.exists():
            state = torch.load(self.weights_path, map_location=self._device)
            self._model.load_state_dict(state)
        # 가중치 없으면 랜덤 초기화 — Day 6 학습 전에는 데모 용도로만 사용

        self._model.eval()
        self._transform = _build_transform()

    def predict(self, image) -> Tuple[str, float]:
        """
        Args:
            image: PIL.Image 또는 파일 경로

        Returns:
            (label, confidence)
        """
        import torch
        from PIL import Image

        self._ensure_loaded()

        if isinstance(image, (str, Path)):
            image = Image.open(image).convert("RGB")
        elif hasattr(image, "convert"):
            image = image.convert("RGB")
        else:
            raise TypeError("image는 경로 또는 PIL.Image여야 합니다.")

        tensor = self._transform(image).unsqueeze(0).to(self._device)
        with torch.no_grad():
            logits = self._model(tensor)
            probs = torch.softmax(logits, dim=1)[0]
            idx = int(torch.argmax(probs).item())
            conf = float(probs[idx].item())

        return CLASS_NAMES[idx], conf

    def predict_batch(self, images: List) -> List[Tuple[str, float]]:
        return [self.predict(img) for img in images]
