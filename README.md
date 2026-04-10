# 점글이 v4 — 음성↔점자 격차 해결기 + 수학 멀티모달 보조

시각장애 수험생이 국어 핵심어는 3셀 점자 모듈로 손에 익혀 시험장 점자 문제지를 빠르게 읽고, 수학 수식은 CNN 감지 + Claude Vision 자연어 설명으로 음성 학습할 수 있게 해주는 하이브리드 수능 학습 도구.

**국어 모드 메인 + 수학 모드 보조. 과목 특성에 맞게 다른 접근.**

---

## 철학

> **"뼈대만 만든다. 살은 v5에서."**

## 왜 이 문제를 푸는가

- 시각장애 수험생 **평소 학습**: 음성 (TTS, 스크린리더)
- 시각장애 수험생 **시험장**: 점자 문제지
- **격차**: 음성으로 알던 내용을 점자로 느리게 읽어 시험 시간 부족
- **해결**: 핵심어만 3셀 점자로 손에 익히는 속도 훈련

수학은 점자 수식 변환이 현실적으로 어렵기 때문에 **CNN 수식 감지 + Claude Vision 자연어 설명 + TTS 음성**으로 우회.

---

## 기능

### 국어 모드 (메인, 8개)

1. 수능특강 국어 페이지 사진 업로드
2. OpenCV 전처리 + EasyOCR 한국어 텍스트 추출
3. Sentence-BERT + TF-IDF 핵심어 추출
4. TTS 지문 낭독
5. 한국 점자 표준 변환 (KS X 9211, 자모 분해 + 받침)
6. **3셀 JY-SOFT 하드웨어 순차 출력** (Arduino + pyserial)
7. Whisper 답변 체크 + 반응 시간 측정
8. 속도 훈련 세션 + 레벨링 + 리포트

### 수학 모드 (데모, 3개)

9. 수학 페이지 업로드
10. **CNN 수식 영역 감지기** (ResNet18 Transfer Learning, 2-class)
11. **Claude Vision 수식 자연어 설명** → TTS

### 보조 실험

- Scikit-learn Random Forest + HOG vs CNN 비교 (실제 앱 데이터)
- MNIST 기반 Transfer Learning 이해 노트북

---

## 기술 스택

### Backend (Django 4.2)

- Python 3.11+ / Django / DRF
- EasyOCR (한국어)
- Sentence-BERT (`jhgan/ko-sbert-nli`)
- Anthropic Claude + Claude Vision (LangChain LCEL)
- OpenAI Whisper API
- gTTS
- PyTorch + torchvision (ResNet18 수식 감지기)
- scikit-learn + scikit-image (RF + HOG 비교)
- pyserial (Arduino 통신)
- hgtk (자모 분해)

### Frontend (React 19)

- Vite + TypeScript
- Tailwind CSS
- TanStack Query
- Zustand

### Hardware

- **JY-SOFT 3셀 점자 표시 모듈**
- Arduino Uno/Nano
- 라이브러리: `braille.h` (JY-SOFT 제공)
- 전원: 5V 2A 어댑터 또는 7.4V 리튬 배터리

---

## 의식적으로 제외 (v5)

- 수학 점자 표기 (한국 점자 수학 규정 — 복잡도 과다)
- 6셀 확장 (본인 미검증)
- 수학 그래프·도형 촉각 출력
- 40셀 점자 디스플레이 연동
- 사용자 계정·책 라이브러리
- 학습 이력·진도 그래프
- 북마크·노트
- 실시간 촬영 모드
- 교사 대시보드
- 영어·탐구 확장

---

## 폴더 구조

```
jeomgeuli_v4/
├── backend/                   # Django 백엔드
│   ├── jeomgeuli_backend/     # Django 설정
│   ├── apps/
│   │   ├── braille/           # 점자 변환 (v3 확장: 자모 분해)
│   │   ├── common/            # 공통 유틸
│   │   ├── textbook/          # OCR + 섹션 분류
│   │   ├── vocabulary/        # 핵심어 추출
│   │   ├── training/          # 훈련 세션 관리
│   │   ├── hardware/          # 3셀 하드웨어 통신
│   │   └── math_demo/         # 수학 모드 (CNN + Vision)
│   ├── data/                  # 수집 데이터
│   │   ├── textbook_raw/      # 국어 지문 사진
│   │   └── math_raw/          # 수학 페이지 + 크롭
│   │       ├── 01_formula/    # 수식 크롭 (CNN 학습용)
│   │       └── 02_text/       # 본문 크롭 (CNN 학습용)
│   ├── weights/               # CNN 모델 가중치
│   ├── results/               # 실험 결과 (비교표 등)
│   ├── ml_experiments/        # Jupyter 노트북
│   ├── requirements.txt
│   ├── manage.py
│   └── .env.example
├── frontend/                  # React 프론트엔드
│   └── src/
│       ├── api/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       └── store/
├── arduino/
│   └── braille_receiver/      # Arduino 스케치
│       └── braille_receiver.ino
├── docs/                      # 기획 문서
└── README.md
```

---

## 설치 + 실행

### 1. 백엔드

```bash
cd backend

# 가상환경
python -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows

# 의존성
pip install -r requirements.txt

# 환경변수
cp .env.example .env
# .env 편집해서 API 키 입력

# DB 마이그레이션
python manage.py migrate

# 서버 실행
python manage.py runserver
```

### 2. 프론트엔드

```bash
cd frontend

npm install
npm run dev
```

### 3. Arduino (하드웨어)

1. Arduino IDE 설치
2. `arduino/braille_receiver/braille_receiver.ino` 열기
3. JY-SOFT 제공 `braille.h` 라이브러리 추가
4. Arduino Uno/Nano에 업로드
5. JY-SOFT 3셀 모듈 연결 (DATA=2, LATCH=3, CLOCK=4)
6. 5V 2A 어댑터 연결
7. USB로 PC에 연결
8. `.env`의 `SERIAL_PORT` 확인

### 4. 테스트

```bash
# 점자 변환 테스트
cd backend
python manage.py test apps.braille

# API 테스트 (서버 실행 후)
curl -X POST http://localhost:8000/api/braille/convert_text/ \
  -H "Content-Type: application/json" \
  -d '{"text": "사랑"}'
```

---

## 개발 일정 (6일 스프린트, Week 3)

| Day | 작업 |
|---|---|
| 월 | CNN 이론 + 한국 점자 기초 + MNIST 샘플 1회 실행 |
| 화 | `braille/utils.py` 자모 분해 구현 + 단위 테스트 |
| 수 | EasyOCR + 핵심어 추출 + LangChain LCEL |
| 목 | **3셀 하드웨어 통합** (Arduino + pyserial) |
| 금 | 훈련 세션 UI + Whisper 답변 체크 + 국어 E2E |
| 토 | 수학 페이지 촬영·크롭 + ResNet18 수식 감지기 학습 |
| 일 | Claude Vision 통합 + Scikit-learn 비교 + v3 정리 |

---

## v3 → v4 변경점

### 삭제
- `chat/`, `intent/`, `learn/`, `review/` Django 앱
- `Explore.tsx`, `Learn.tsx`, `Review.tsx`, `FreeConvert.tsx` 페이지
- `ReviewCard.tsx` 컴포넌트
- 하드코딩된 OpenAI API 키

### 확장
- `braille/utils.py`: 9자 하드코딩 → 한국 점자 표준 자모 분해
- `braille/views.py`: 단일 엔드포인트 → 4개 (convert, convert_text, convert_word, decompose)

### 신규
- `apps/textbook/` — OCR + 섹션 분류
- `apps/vocabulary/` — 핵심어 추출
- `apps/training/` — 훈련 세션
- `apps/hardware/` — 3셀 하드웨어 통신
- `apps/math_demo/` — 수학 모드 (CNN + Vision)
- `arduino/braille_receiver/` — Arduino 스케치

---

## 참조

- 한국 점자 규정 (2017 개정): 국립국어원
- KS X 9211
- JY-SOFT 점자 표시 모듈: smartstore.naver.com/jy-soft
- `braille.h` 라이브러리: JY-SOFT 제공
- 상세 기획: `../G---------Obsidian/10. Planner/코드잇/점글이/점글이_v4_기획.md`

---

## 라이선스

개인 프로젝트 (포트폴리오용). 비영리 학습 목적 사용만 허용.
