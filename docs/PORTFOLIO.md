# 점글이 v4 — 포트폴리오

> 시각장애 수험생의 "음성 학습 vs 시험장 점자 문제지" 매체 격차를 3셀 점자 속도 훈련과 수학 멀티모달 음성 해설로 해소하는 하이브리드 수능 학습 도구.

본 문서는 점글이 v4의 **의사결정 근거와 트레이드오프**를 정리한 엔지니어링 서사다. 기능 목록과 실행 가이드는 [README](../README.md)를 참고.

---

## 1. 해결하려는 문제

시각장애 수험생은 평소 공부를 **음성**(TTS, 스크린리더)으로 하고, 시험장에서는 **점자 문제지**를 받는다. 두 매체가 다르기 때문에 시험장에서 점자 한 글자씩 더듬어 읽느라 지문 독해에 필요한 시간을 전부 쓰지 못하는 사용자가 많다는 사실이 이 프로젝트의 출발점이다.

기존 해법들은 두 방향 중 하나였다.

- **시험장 보조기기 도입** — 40셀 점자 디스플레이 같은 큰 장비는 비싸고 시험장에 들고 갈 수 없거나 제한이 있다.
- **점자 학습 앱** — 단순 알파벳 암기 위주라 "시험 속도" 관점의 훈련이 없다.

점글이 v4는 세 번째 방향을 택했다. **핵심어만 3셀 점자로 손에 익혀 독해 속도를 높이는 훈련 도구.** 지문 전체를 점자로 출력하려 하지 않고, OCR로 뽑아낸 핵심어 10~15개만 손가락에 새기는 것을 목표로 한다. 기기 제약과 시간 제약 둘 다를 수용하는 접근이다.

수학은 점자 수식 표기가 현실적으로 개인 프로젝트에서 다루기 어려워서, 이 격차를 **CNN 수식 감지 + Claude Vision 자연어 설명 + TTS**로 우회한다. 수학은 데모 범위이고 국어가 메인이다.

---

## 2. 타겟 사용자와 제약

### 사용자

- 시각장애 수험생 (수능특강 국어·수학 학습 중)
- 보조자(부모·선생님)가 시각적 UI로 기기·앱을 세팅하고, 학습자는 스크린리더 + 키보드 + 3셀 점자 모듈로 조작한다

### 하드웨어 제약

- **JY-SOFT 3셀 점자 모듈**이 본인이 실제로 연결·검증해본 유일한 기기
- 6셀 모듈은 미검증이라 v5로 보류
- Arduino Uno/Nano + pyserial로 Python ↔ 하드웨어 통신

### 시간 제약

- 개인 포트폴리오 프로젝트, 2주 압축 스프린트
- 수능 학습 도구로 실사용 검증할 기회는 없음. 구현 품질로 "이 사람은 이 문제를 진지하게 봤다"를 증명하는 게 목표

이 제약이 이후 모든 의사결정의 근거가 된다.

---

## 3. 철학 — "뼈대만 만든다. 살은 v5에서"

프로젝트를 시작하면서 가장 먼저 세운 원칙은 **"무엇을 만들지보다 무엇을 만들지 않을지 먼저 정한다"** 였다. 2주 안에 기능 3개를 깊게 쌓는 게, 기능 10개를 얕게 늘어놓는 것보다 심사관 평가·실사용 가치 양쪽에서 우위가 있다고 판단했다.

의식적으로 v5로 미룬 것들:

| 제외 | 이유 |
|---|---|
| 수학 점자 표기 | 한국 점자 수학 규정 복잡도 과다, 2주로 불가능 |
| 6셀 확장 | 본인 미검증 하드웨어, 배포 신뢰도 낮음 |
| 수학 그래프·도형 촉각 출력 | 기계공학 범위, 스코프 초과 |
| 40셀 점자 디스플레이 연동 | 가격·시험장 제한 |
| 사용자 계정·책 라이브러리 | 단일 사용자 가정으로 충분 |
| 학습 이력·진도 그래프 | 지속 사용 후에야 가치 발생 |
| 북마크·노트 | 학습 도구가 아니라 에디터로 변질 위험 |
| 실시간 촬영 모드 | OCR 품질 부족 시 문제 악화 |
| 교사 대시보드 | 사용자 1명 전제 |
| 영어·탐구 확장 | 국어·수학으로 먼저 증명 |

이 "의식적 배제" 목록은 README에도 포함해서 심사관이 스코프 관리 의도를 즉시 볼 수 있게 했다.

---

## 4. 기술 스택과 선택 근거

### 백엔드 — Django 4.2 + DRF

대안: FastAPI (비동기 성능), Flask (최소주의).

Django를 선택한 이유:

1. **v3 재활용** — 이전 버전 점글이가 Django 4.2로 이미 구축돼 있었고, 모델·URL·인증 기반을 재사용하면 2주 스프린트에서 2~3일을 절약할 수 있었다.
2. **관리자 UI** — `python manage.py createsuperuser` 후 세션 데이터를 바로 확인할 수 있어 포트폴리오 시연 시점에 DB 조회 도구를 따로 만들 필요가 없다.
3. **ORM + Migrations** — 훈련 세션 모델(`Session`, `WordAttempt`)의 반응 시간·정답률 집계가 단순 쿼리로 끝남.

FastAPI의 비동기 이점은 이 프로젝트의 부하(단일 사용자, OCR 몇 초)로는 불필요했다.

### 프론트엔드 — React 19 + Vite + TypeScript + Tailwind

- **React 19**는 최신 `useTransition` / `use()` API를 시도해볼 가치가 있었지만, 실제로는 이 프로젝트 규모에서 큰 차이는 없었다. 사용한 이유는 단순히 Vite 템플릿 기본이라서.
- **TanStack Query**를 `package.json`에 넣었지만 실제로는 직접 axios 호출을 썼다 — 각 페이지의 상태 기계가 단순해서 Query의 캐싱·리페치 이점을 살릴 규모가 아니었다. 이 선택은 의식적 단순화이고, 규모가 커지면 Query로 이전.
- **Zustand**는 "Scan 페이지에서 뽑은 핵심어를 SpeedTraining으로 넘기는" 작은 범위에만 사용. URL 파라미터나 React Router loader로도 가능했지만, 페이지 전환 시 데이터 손실이 시각장애 사용자에게는 큰 혼란이 될 수 있어 스토어 유지.
- **Tailwind**는 디자인 시스템 구축보다 빠른 유틸리티 반복이 필요한 국면이라 선택.

### OCR — EasyOCR vs Tesseract

EasyOCR을 선택. 이유:

- 한국어 인식 정확도가 Tesseract보다 눈에 띄게 좋음 (수능특강 조판의 세리프·크기 다양성에 강함)
- `easyocr.Reader(['ko'], gpu=False)` 한 줄로 초기화
- 첫 실행 시 모델 ~100MB 다운로드는 부담이지만, 한 번 캐시되면 이후는 몇 초 내

단점: `verbose=True` 기본값이 Windows `cp949` 콘솔에서 progress bar `█` 문자 때문에 `UnicodeEncodeError`를 발생시켜 `/api/textbook/extract/` 엔드포인트가 500을 반환하는 문제를 실제로 겪음. `verbose=False`로 수정해서 해결. 이런 크로스 플랫폼 에지 케이스가 포트폴리오 스크린샷보다 실제 엔지니어링 경험을 증명한다고 본다.

### 핵심어 추출 — Sentence-BERT vs TF-IDF

두 전략을 둘 다 구현하고 API로 선택 가능하게 했다.

- **TF-IDF** (`sklearn.feature_extraction.text.TfidfVectorizer`): 빠름, 의미 이해 없음, 수백ms 내 응답
- **Sentence-BERT** (`jhgan/ko-sbert-nli`): 느림(첫 호출 ~45초, 이후 ~3초), 의미 기반, 문장 임베딩과 후보 단어 임베딩의 코사인 유사도

벤치마크 스크립트 대신 사용자가 전략을 선택하게 두는 접근. 실제로 데모 시연에는 TF-IDF가 충분하고, SBERT는 "의미 기반 추출이 가능하다"는 가능성 제시 역할.

### 수학 감지 — ResNet18 Transfer Learning

- `torchvision.models.resnet18(weights=None)` + `nn.Linear(512, 2)` 마지막 fc 교체
- 2-class: `text`(본문) vs `formula`(수식)
- 입력: 수학 페이지에서 잘라낸 크롭 이미지 (224×224)
- 학습 데이터: 수능특강 수학 페이지 20~30장 수집·라벨링 예정 (현재 가중치 미학습 상태, 스켈레톤만)

학습 전이지만 학습 파이프라인과 Django 엔드포인트를 미리 만들어놓아서 데이터가 확보되면 즉시 `torch.save(model.state_dict(), 'weights/formula_detector.pth')` 한 줄로 배포 가능.

### 수학 해설 — Claude Vision + LangChain LCEL

```python
chain = (
    ChatPromptTemplate.from_messages([
        SystemMessage(content=VISION_SYSTEM_PROMPT),
        HumanMessage(content=[
            {"type": "image", "source": {"type": "base64", ...}},
            {"type": "text", "text": "..."}
        ]),
    ])
    | ChatAnthropic(model="claude-sonnet-4-6", max_tokens=512)
    | StrOutputParser()
)
```

시스템 프롬프트는 "시각장애 수험생을 위한 한국어 수학 튜터" 역할 정의 + 기호 한국어 풀이 규칙(`∫ → '적분'`, `Σ → '시그마'`) + TTS 친화적 문장 요구.

LangChain LCEL(`|` 파이프 연산자)을 사용한 이유는 체인 가독성이지만, 사실 `anthropic` SDK 직접 호출로도 충분했다. LangChain은 후속 작업(few-shot 예시 추가, 체인 분기)을 열어두는 선택.

### 하드웨어 — JY-SOFT 3셀 + Arduino + pyserial

- Python → pyserial → Arduino Uno/Nano → `braille.h` 라이브러리 → 3셀 점자 모듈
- 프로토콜: 3바이트(3셀 × 6점)를 한 번에 전송, 각 바이트의 하위 6비트가 점 패턴
- 싱글톤 `BrailleHardwareManager`로 포트 재연결 비용 절약

실기기 없이 테스트가 가능하도록 `connect()`가 실패하면 `False`를 반환하고 뷰는 503을 내린다. CI는 `pyserial`만 설치된 상태로 이 실패 경로를 단위 테스트로 검증한다.

### 한국 점자 매핑 — KS X 9211 2017 개정

이 프로젝트에서 가장 중요한 의사결정 하나가 여기 있다. 섹션 5에서 자세히.

---

## 5. 주요 의사결정과 트레이드오프

### (1) v3 → v4 전면 재작성 vs 점진 확장

v3(이전 점글이)는 `braille_map = {"가": [1,0,0,0,0,0], "나": [1,0,1,0,0,0], ...}` 형태로 **9자 하드코딩**만 있었다. "사랑해"를 출력하면 점자 패턴이 사실 틀린 상태였다.

선택: 전면 재작성.

근거:

- v3의 자모 분해 개념이 없어서 확장할 기반이 없었다
- OCR, 핵심어 추출, 훈련 세션, 수학 모드 전부 새 앱이 필요했음
- Django 설정·URL 라우팅·프론트엔드 페이지는 재사용 가능

결과: `backend/jeomgeuli_backend/` 설정과 `apps/braille/` 틀만 v3에서 가져오고, 나머지 5개 앱은 처음부터 작성. 프론트엔드는 v3의 `Learn.tsx`, `Review.tsx`, `Explore.tsx`, `FreeConvert.tsx`를 전부 삭제하고 Home / Scan / SpeedTraining / SessionReport / MathDemo / BrailleConverter 6개로 재구성.

### (2) 한국 점자 매핑: 웹 검색 실패 → 내부 자산 발견

v4 초기에 `apps/braille/utils.py`의 초성·중성·종성 매핑 테이블에 `# TODO: 검증` 주석을 가득 달아둔 상태로 진행했다. 정확성이 불안한 상태에서 훈련 세션을 돌리면 "잘못된 점자를 틀리게 익히는" 최악의 결과가 나올 수 있었다.

**1차 시도 — 공식 문서·웹 검색:**

- 국립국어원 "한국 점자 규정 2017 개정" PDF → 다운로드 타임아웃
- 위키피디아 한국어판 "한글 점자" 문서 → 점자 배치가 전부 이미지 파일, 텍스트 추출 불가
- 영어 위키피디아 "Korean Braille" 문서 → LLM이 요약해서 값을 반환했는데 ㅘ·ㅙ가 동일하게 나오는 등 명백한 오류 포함
- 나무위키 "한글 점자" 문서 → 403 Forbidden

이 단계에서 2시간 이상 소요. 웹 자료만으로는 정확한 값을 못 얻는 상황이었다.

**2차 시도 — 내부 자산:**

작업 중 사용자가 `c:\Users\user\Desktop\jeomgeuli-suneung-helper/` 폴더 존재를 알려주었다. 이전에 만든 FastAPI 기반 "점글이 수능 버전"이었고, `firmware/braille_3cell/BrailleMap.h`에 **한국 점자 전체 매핑이 이미 검증된 상태로 Arduino C++ `PROGMEM` 상수 테이블로 구현돼 있었다**:

- 초성 19개 (쌍자음은 된소리표 + 기본 자음 2셀 구조까지)
- 중성 21개 (복모음 6개 ㅒㅘㅙㅝㅞㅟ 는 "첫 셀 + ㅐ" 2셀 구조)
- 종성 27개 + 받침 없음 (겹받침은 두 받침 이어쓰기 2셀)
- 약자 26개 (가·나·다·마·바·사·자·카·타·파·하 + 것·억·언·얼·연·열·영·옥·온·옹·운·울·은·을·인)
- 숫자 + 수표(점 3,4,5,6)
- 영문자 + 로마자표(점 3,5,6)

그리고 `BrailleConverter.cpp`의 변환 로직에서 **초성 ㅇ은 음가가 없으므로 출력 생략**(`cho != 11` 가드), **약자 우선 매칭**, **복모음 2셀 분기 인덱스** 등 규정 해석까지 전부 구현돼 있었다.

결정: Arduino C++ 테이블을 **Python dict로 1:1 포팅**. 로직도 그대로 옮김.

결과:

- `apps/braille/utils.py`의 모든 `# TODO` 마커 제거
- 35개 단위 테스트로 자모 분해·약자 우선·초성 ㅇ 생략·복모음 2셀·겹받침·쌍자음·숫자·영문자·회귀 전부 커버
- `decompose_hangul("아")` → `("ㅇ", "ㅏ", "")` 이지만 `char_to_braille("아")` → `[[1,1,0,0,0,1]]` (ㅏ 1셀만)
- `char_to_braille("사랑")` → 4셀 (사 약자 1 + 랑 ㄹ+ㅏ+ㅇ 3)
- `char_to_braille("값")` → 4셀 (ㄱ + ㅏ + ㅂ + ㅅ, ㅄ 겹받침)

교훈: **"처음부터 만들지 말고 내부 자산을 먼저 찾아라"**는 진부한 조언이지만, 이번 프로젝트에서 실제로 2시간을 잃고 나서야 적용할 수 있었다. 다음 세션부터 활용할 수 있도록 메모리에 기록으로 남김 (`reference_korean_braille_map.md`).

### (3) 시연용 데모 모드 추가

포트폴리오 심사관이 앱을 돌려볼 환경을 가정했을 때, 다음 세 가지가 없을 가능성이 높았다:

1. **Arduino JY-SOFT 3셀 모듈** — 거의 확실히 없음
2. **ANTHROPIC_API_KEY** — 심사관 개인 키를 받아야 가능
3. **브라우저 마이크 권한 + HTTPS** — 로컬 `http://localhost:5173`에서는 Web Speech API STT가 제한적

이 세 가지 중 하나만 빠져도 "교재 스캔 → 핵심어 → 속도 훈련 → 리포트" 흐름 전체가 막힌다.

해결: **Home에 "빠른 시연" 섹션 + SpeedTraining에 수동 채점 모드 추가**.

- `frontend/src/data/demoSamples.ts`에 국어 지문 3개(문학 해석, 생태계, 근대화)와 각각의 핵심어 리스트를 하드코딩
- Home 페이지 하단에서 샘플 버튼 클릭 → Zustand 스토어에 주입 → `/training` 이동
- SpeedTraining에 `inputMode` 라디오: `voice` (브라우저 STT) / `manual` (정답·오답 버튼)
- `sendHardware` 기본값을 `true` → `false`로 변경

결과: 심사관이 `npm run dev` + `python manage.py runserver` 두 명령만으로 Arduino·API 키·마이크 없이 전체 훈련 흐름과 리포트 페이지를 볼 수 있다.

트레이드오프: 데모 모드는 "실제 시나리오"와 다르다. README의 "빠른 시연" 섹션에서 이걸 명시해서 심사관이 "내가 본 게 실사용 경로인지 데모 우회 경로인지"를 구분할 수 있게 했다.

### (4) 접근성 1차 개선 — 정체성과 UI의 정합성

v4 초기 스캐폴드는 일반적인 마우스 웹 앱이었다. 그런데 타겟 사용자가 시각장애 수험생이므로 이 UI는 **보조자용**이고, 학습자가 쓸 "음성 + 키보드" 인터페이스가 빠진 상태였다.

범위를 1차 개선으로 한정:

- `index.css` 전면 재작성 — Vite 기본 템플릿 CSS를 지우고 focus ring 항상 표시, 17px 기본 폰트, `prefers-reduced-motion` 존중
- Semantic HTML — 모든 페이지에 `<main>`, `<nav>`, `<section aria-labelledby>`
- ARIA live regions — OCR 진행 상태, 훈련 중 단어 안내, 리포트 정답률 자동 아나운스
- SpeedTraining 키보드 단축키 — `Enter`(시작), `Space`(다시 듣기), `S`(건너뛰기), `Esc`(종료)
- TTS 자동 안내 — 새 단어 출제 시 "N번째 단어. 답을 말해주세요", 정답/오답 피드백
- 버튼 대비 강화 — Tailwind `-500/-600` 계열을 `-700/-800`으로 올려 WCAG AA 달성
- ErrorBoundary + 404 페이지에 `role="alert"` — 스크린리더가 에러 상황을 즉시 아나운스

의식적 제외: 키보드 전용 훈련 모드(마우스 없이도 시작부터 끝까지 가능), 고대비 테마 토글, 폰트 크기 조절 UI. v5로 보류.

교훈: 접근성은 "나중에 추가하는 기능"이 아니라 **프로젝트 정체성과 UI가 일치하는지에 대한 검증**이다. 타겟 사용자가 시각장애인이라고 적어놓고 마우스 전용 UI를 만들면, 그건 포트폴리오로서 모순이 된다.

### (5) GitHub Actions CI — 최소 의존성 전략

CI 워크플로우를 쓸 때 가장 고민한 건 "어떤 파이썬 패키지를 설치할까"였다. 전체 `requirements.txt`에는 `torch`, `easyocr`, `sentence-transformers`, `langchain` 등 무거운 것들이 포함돼 있어서, 그대로 설치하면 CI 1회 실행에 5~10분이 걸린다.

분석: braille·textbook parser·training 세션 로직·hardware 싱글톤·vocabulary TF-IDF는 전부 **torch·easyocr·sentence-transformers 없이** 테스트 가능하다. 왜냐하면 무거운 패키지들은 전부 함수 내부 `lazy import`로 감싸뒀기 때문.

결정: 최소 의존성만 설치.

```yaml
pip install \
  "Django==4.2.24" \
  "djangorestframework==3.15.2" \
  "django-cors-headers==4.4.0" \
  "python-dotenv==1.0.1" \
  "hgtk>=0.2.1" \
  "opencv-python-headless>=4.8.0" \
  "numpy>=1.24.0" \
  "scikit-learn>=1.3.0" \
  "pyserial>=3.5"
```

결과: CI 백엔드 잡 25초, 프론트엔드 잡 15초, 총 ~40초 내외. 매 커밋마다 86개 단위 테스트가 자동 실행.

트레이드오프: SBERT, EasyOCR, torch 경로는 CI에서 검증하지 않는다. 이 부분은 로컬 수동 스모크 테스트와 포트폴리오 문서(이 문서)에서 "동작 확인됨" 증거를 대체.

---

## 6. 구현 결과 지표

### 백엔드

- **6 Django 앱**: `braille`, `textbook`, `vocabulary`, `training`, `hardware`, `math_demo`
- **19 REST 엔드포인트**:
  - `/api/braille/`: convert, convert_text, convert_word, decompose (4)
  - `/api/textbook/`: extract, classify (2)
  - `/api/vocabulary/`: extract (1)
  - `/api/training/sessions/`: create, get, show, answer, finish (5)
  - `/api/hardware/`: status, connect, clear, send, send_text (5)
  - `/api/math/`: detect, explain (2)
- **86 단위 테스트** (braille 35 + textbook 15 + vocabulary 9 + training 12 + hardware 15)
- **점자 매핑**: 초성 19 + 중성 21 + 종성 27 + 약자 26 + 숫자 10 + 영문자 26 (KS X 9211 2017 개정 전체)

### 프론트엔드

- **6 페이지**: Home, Scan, SpeedTraining, SessionReport, MathDemo, BrailleConverter (+ NotFound)
- **7 API 모듈**: axiosInstance, brailleAPI, textbookAPI, vocabularyAPI, trainingAPI, hardwareAPI, mathAPI
- **ErrorBoundary** 전역 적용, `role="alert"`
- **접근성**: 키보드 단축키 4종, ARIA live regions, focus ring, 17px 기본 폰트, WCAG AA 대비
- **프로덕션 빌드**: 96 modules, 297KB JS / 97KB gzip

### CI / DevOps

- **GitHub Actions**: push/PR마다 백엔드 테스트 + 프론트엔드 빌드
- **총 소요 시간**: ~40초
- **최소 의존성 전략**: 9개 패키지만 설치 (전체 requirements.txt의 ~10%)
- **6 커밋 전부 CI 그린**

### 하드웨어 통합

- **Arduino 스케치**: `arduino/braille_receiver/braille_receiver.ino`
- **프로토콜**: 9600 baud, 3바이트 chunk, `braille.h` 라이브러리
- **싱글톤 매니저**: `BrailleHardwareManager` with auto port detection + 503 fallback

---

## 7. 접근성 체크리스트

| 항목 | 상태 | 구현 위치 |
|---|---|---|
| 키보드로 전체 조작 가능 | ✓ (훈련) / 부분 (스캔·수학) | `SpeedTraining.tsx` 키보드 핸들러 |
| 스크린리더 라이브 리전 | ✓ | 각 페이지 `role="status" aria-live="polite"` |
| 포커스 링 항상 표시 | ✓ | `index.css :focus-visible` |
| 기본 폰트 17px | ✓ | `index.css :root font-size` |
| `prefers-reduced-motion` 존중 | ✓ | `index.css @media` |
| WCAG AA 버튼 대비 | ✓ | Tailwind `-700/-800` 계열 |
| 에러 상태 `role="alert"` | ✓ | ErrorBoundary, NotFound, 각 페이지 |
| 시맨틱 HTML | ✓ | `<main>`, `<nav>`, `<section aria-labelledby>` |
| TTS 자동 안내 | ✓ | SpeedTraining 단어 출제·채점 피드백 |
| 스크린리더 전용 상태 메시지 | ✓ | `.visually-hidden` 유틸 |
| 고대비 테마 토글 | ✗ (v5) | — |
| 폰트 크기 조절 UI | ✗ (v5) | — |
| 전체 페이지 키보드 네비게이션 검증 | 부분 (v5 완성) | — |

---

## 8. 한계와 다음 단계 (v5)

### 검증되지 않은 부분

1. **수학 CNN 실학습** — ResNet18 파이프라인은 완성됐지만 가중치는 학습 전. 수능특강 수학 페이지 20~30장 촬영 + 수식/본문 크롭 라벨링이 필요.
2. **Claude Vision 실호출** — 엔드포인트와 LCEL 체인은 구현됐지만 `ANTHROPIC_API_KEY` 없이는 CI에서 검증 불가. 로컬에서 1~2장 확인만 했다.
3. **실기기 E2E** — CI는 하드웨어 실패 경로(503)만 검증. 실제 Arduino로 "사랑"이 3셀 시퀀스로 출력되는지 수동 확인만 함.
4. **실제 시각장애 사용자 피드백** — 없음. 포트폴리오는 "이 사람이 이 문제를 얼마나 진지하게 봤는지"만 보여주고, 실사용 검증은 v5 이후.

### v5 로드맵

우선순위 높음:

- 수학 데이터 수집 + ResNet18 fine-tune (1~2일 분량)
- 실 점자 사용자 1명 인터뷰 (속도 훈련 컨셉 자체에 대한 검증)
- 수능특강 국어 실제 페이지 OCR 튜닝 (OCR 결과가 섹션 파서 룰과 매칭되는지)

우선순위 중간:

- 6셀 모듈 지원 (더 긴 단어·문장 한 번에 표시)
- 수학 점자 표기 초보판 (기본 사칙연산만)
- 훈련 이력·진도 그래프

우선순위 낮음:

- 사용자 계정·책 라이브러리
- 교사 대시보드
- 영어·탐구 확장

---

## 9. 파일 구조 요약

```
jeomgeuli_v4/
├── backend/                 Django 4.2 + DRF
│   ├── jeomgeuli_backend/   설정, URL 라우팅
│   └── apps/
│       ├── braille/         점자 매핑 + 4 엔드포인트 + 35 테스트
│       ├── textbook/        EasyOCR + 섹션 파서 + 15 테스트
│       ├── vocabulary/      TF-IDF + Sentence-BERT + 9 테스트
│       ├── training/        세션 모델 + 5 엔드포인트 + 12 테스트
│       ├── hardware/        BrailleHardwareManager + 5 엔드포인트 + 15 테스트
│       └── math_demo/       ResNet18 + Claude Vision
├── frontend/                React 19 + Vite + TS + Tailwind
│   └── src/
│       ├── api/             7 API 모듈
│       ├── components/      BrailleCell, ErrorBoundary
│       ├── data/            demoSamples
│       ├── hooks/           useSTT, useTTS (Web Speech API)
│       ├── pages/           6 페이지 + NotFound
│       ├── store/           Zustand trainingStore
│       └── router.tsx       ErrorBoundary로 감싼 catch-all 라우터
├── arduino/
│   └── braille_receiver/    JY-SOFT 3셀 Arduino 스케치
├── .github/workflows/ci.yml CI
├── docs/
│   └── PORTFOLIO.md         이 문서
└── README.md                기능 목록 + 설치 + 빠른 시연 경로
```

---

## 10. 내가 이 프로젝트에서 배운 것

1. **스코프 관리가 가장 큰 엔지니어링 스킬이다.** 제외 목록을 먼저 만들지 않으면 2주 프로젝트가 2개월 프로젝트가 된다.
2. **내부 자산을 먼저 찾아라.** 웹 검색·LLM 추론보다 이미 검증된 기존 코드가 훨씬 빠르고 정확하다. 한국 점자 매핑에서 실제로 겪었다.
3. **"동작한다"와 "테스트가 증명한다"는 다르다.** 로컬에서 잘 돌던 OCR 엔드포인트가 Windows cp949 콘솔에서 `UnicodeEncodeError`로 500을 반환하는 걸 테스트를 쓰면서 발견했다. 같은 패턴의 버그(이모지 print)가 hardware serial_manager에도 있었다.
4. **포트폴리오는 "완성도 + 의도"의 곱이다.** 기능 10개를 얕게 쌓는 것보다 기능 3개를 깊게 쌓고 "왜 이렇게 만들었는지"를 문서로 남기는 게 심사관에게 더 설득력 있다.
5. **접근성은 기능 체크리스트가 아니라 정체성 검증이다.** "시각장애 사용자를 위한 앱"이라고 적어놓고 마우스 전용 UI를 만들면, 그건 포트폴리오로서 자가당착이다.

---

## 문의

이 프로젝트의 의사결정이나 구현에 대해 궁금한 점은 [이슈](https://github.com/gggmlduswjs/jeomgeuli_v4/issues)로 남겨주세요.
