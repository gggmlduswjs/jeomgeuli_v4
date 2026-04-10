"""
한국 점자 표준 (2017 개정 한국 점자 규정) 변환 모듈

매핑 출처:
    jeomgeuli-suneung-helper/firmware/braille_3cell/BrailleMap.h
    jeomgeuli-suneung-helper/firmware/braille_3cell/BrailleConverter.cpp
    (기존 수능 버전에서 Arduino용으로 검증된 테이블 — v4 Python 포팅)

점 배치:
    1 4
    2 5
    3 6
패턴 표기: [p1, p2, p3, p4, p5, p6]
예: [1, 0, 0, 1, 0, 0] = 점 1·4 활성화

주요 규정:
    1) 초성 ㅇ은 음가가 없으므로 점자로 출력하지 않는다 (cho_idx == 11).
       "아" → ㅏ만 출력 = 1셀
    2) 복모음 ㅒ·ㅘ·ㅙ·ㅝ·ㅞ·ㅟ 는 "첫 셀 + ㅐ(1,2,3,5)" 2셀 구조.
    3) 겹받침(ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄ)은 두 받침을 이어쓴다 (2셀).
    4) 쌍자음 초성(ㄲㄸㅃㅆㅉ)은 된소리표(점 6) + 기본 자음 (2셀).
    5) 약자 26개(가·나·다·마·바·사·자·카·타·파·하 + 것·억·언·얼·연·열·영·옥·온·옹·운·울·은·을·인)는
       한 글자 단위로 분해보다 우선 매칭된다.
    6) 숫자는 수표(점 3,4,5,6) + 숫자 패턴.
    7) 영문자는 로마자표(점 3,5,6) + 알파벳 패턴.
"""

from typing import List, Optional, Tuple


# ----------------------------------------------------------------------------
# 헬퍼: 점 번호 리스트 → [p1..p6] 패턴
# ----------------------------------------------------------------------------
def _dots(*numbers: int) -> List[int]:
    """점 번호들 → 6요소 패턴. _dots(1, 4) → [1,0,0,1,0,0]"""
    pattern = [0, 0, 0, 0, 0, 0]
    for n in numbers:
        if 1 <= n <= 6:
            pattern[n - 1] = 1
    return pattern


EMPTY_CELL: List[int] = [0, 0, 0, 0, 0, 0]

# 복모음 두 번째 셀 = ㅐ
COMPOUND_VOWEL_SECOND: List[int] = _dots(1, 2, 3, 5)


# ----------------------------------------------------------------------------
# 초성 19개 — 변환 시 ㅇ(index 11)은 생략됨
# ----------------------------------------------------------------------------
CHOSEONG_BRAILLE: dict = {
    'ㄱ': [_dots(4)],
    'ㄲ': [_dots(6), _dots(4)],                 # 된소리표 + ㄱ
    'ㄴ': [_dots(1, 4)],
    'ㄷ': [_dots(2, 4)],
    'ㄸ': [_dots(6), _dots(2, 4)],              # 된소리표 + ㄷ
    'ㄹ': [_dots(5)],
    'ㅁ': [_dots(1, 5)],
    'ㅂ': [_dots(4, 5)],
    'ㅃ': [_dots(6), _dots(4, 5)],              # 된소리표 + ㅂ
    'ㅅ': [_dots(6)],
    'ㅆ': [_dots(6), _dots(6)],                 # 된소리표 + ㅅ
    'ㅇ': [],                                   # 초성 ㅇ 음가 없음 → 출력 안 함
    'ㅈ': [_dots(4, 6)],
    'ㅉ': [_dots(6), _dots(4, 6)],              # 된소리표 + ㅈ
    'ㅊ': [_dots(5, 6)],
    'ㅋ': [_dots(1, 2, 4)],
    'ㅌ': [_dots(1, 2, 5)],
    'ㅍ': [_dots(1, 4, 5)],
    'ㅎ': [_dots(2, 4, 5)],
}

# ----------------------------------------------------------------------------
# 중성 21개 — 6개 복모음은 2셀 ("첫 셀 + ㅐ")
# ----------------------------------------------------------------------------
JUNGSEONG_BRAILLE: dict = {
    'ㅏ': [_dots(1, 2, 6)],
    'ㅐ': [_dots(1, 2, 3, 5)],
    'ㅑ': [_dots(3, 4, 5)],
    'ㅒ': [_dots(3, 4, 5), COMPOUND_VOWEL_SECOND],      # ㅑ + ㅐ
    'ㅓ': [_dots(2, 3, 4)],
    'ㅔ': [_dots(1, 3, 4, 5)],
    'ㅕ': [_dots(1, 5, 6)],
    'ㅖ': [_dots(3, 4)],
    'ㅗ': [_dots(1, 3, 6)],
    'ㅘ': [_dots(1, 2, 3, 6), COMPOUND_VOWEL_SECOND],
    'ㅙ': [_dots(1, 2, 3, 6), COMPOUND_VOWEL_SECOND],
    'ㅚ': [_dots(1, 3, 4, 5, 6)],
    'ㅛ': [_dots(3, 4, 6)],
    'ㅜ': [_dots(1, 3, 4)],
    'ㅝ': [_dots(1, 2, 3, 4), COMPOUND_VOWEL_SECOND],
    'ㅞ': [_dots(1, 2, 3, 4), COMPOUND_VOWEL_SECOND],
    'ㅟ': [_dots(1, 3, 4), COMPOUND_VOWEL_SECOND],
    'ㅠ': [_dots(1, 4, 6)],
    'ㅡ': [_dots(2, 4, 6)],
    'ㅢ': [_dots(2, 4, 5, 6)],
    'ㅣ': [_dots(1, 3, 5)],
}

# ----------------------------------------------------------------------------
# 종성 27개 + 받침 없음 — 겹받침은 2셀로 이어쓰기
# ----------------------------------------------------------------------------
JONGSEONG_BRAILLE: dict = {
    '': [],
    'ㄱ': [_dots(1)],
    'ㄲ': [_dots(1, 6)],                                  # 쌍받침 약자 (단일 셀)
    'ㄳ': [_dots(1), _dots(3)],                           # ㄱ + ㅅ
    'ㄴ': [_dots(2, 4, 5)],
    'ㄵ': [_dots(2, 4, 5), _dots(1, 3)],                  # ㄴ + ㅈ
    'ㄶ': [_dots(2, 4, 5), _dots(3, 5, 6)],               # ㄴ + ㅎ
    'ㄷ': [_dots(3, 5)],
    'ㄹ': [_dots(2)],
    'ㄺ': [_dots(2), _dots(1)],                           # ㄹ + ㄱ
    'ㄻ': [_dots(2), _dots(2, 6)],                        # ㄹ + ㅁ
    'ㄼ': [_dots(2), _dots(1, 2)],                        # ㄹ + ㅂ
    'ㄽ': [_dots(2), _dots(3)],                           # ㄹ + ㅅ
    'ㄾ': [_dots(2), _dots(2, 3, 6)],                     # ㄹ + ㅌ
    'ㄿ': [_dots(2), _dots(2, 5, 6)],                     # ㄹ + ㅍ
    'ㅀ': [_dots(2), _dots(3, 5, 6)],                     # ㄹ + ㅎ
    'ㅁ': [_dots(2, 6)],
    'ㅂ': [_dots(1, 2)],
    'ㅄ': [_dots(1, 2), _dots(3)],                        # ㅂ + ㅅ
    'ㅅ': [_dots(3)],
    'ㅆ': [_dots(3, 4)],                                  # 쌍받침 약자
    'ㅇ': [_dots(2, 3, 5, 6)],                            # 종성 ㅇ은 초성과 다름
    'ㅈ': [_dots(1, 3)],
    'ㅊ': [_dots(1, 2, 6)],
    'ㅋ': [_dots(2, 3, 5)],
    'ㅌ': [_dots(2, 3, 6)],
    'ㅍ': [_dots(2, 5, 6)],
    'ㅎ': [_dots(3, 5, 6)],
}

# ----------------------------------------------------------------------------
# 약자 26개 — 분해 전 우선 매칭
# ----------------------------------------------------------------------------
ABBREVIATIONS: dict = {
    '가': [_dots(1, 2, 4, 6)],
    '나': [_dots(1, 4)],
    '다': [_dots(2, 4)],
    '마': [_dots(1, 5)],
    '바': [_dots(4, 5)],
    '사': [_dots(1, 2, 3)],
    '자': [_dots(4, 6)],
    '카': [_dots(1, 2, 4)],
    '타': [_dots(1, 2, 5)],
    '파': [_dots(1, 4, 5)],
    '하': [_dots(2, 4, 5)],
    '것': [_dots(5, 6), _dots(2, 3, 4)],                  # 2셀
    '억': [_dots(1, 4, 5, 6)],
    '언': [_dots(2, 3, 4, 5, 6)],
    '얼': [_dots(2, 3, 4, 5)],
    '연': [_dots(1, 6)],
    '열': [_dots(1, 2, 5, 6)],
    '영': [_dots(1, 2, 4, 5, 6)],
    '옥': [_dots(1, 3, 4, 6)],
    '온': [_dots(1, 2, 3, 5, 6)],
    '옹': [_dots(1, 2, 3, 4, 5, 6)],
    '운': [_dots(1, 2, 4, 5)],
    '울': [_dots(1, 2, 3, 4, 6)],
    '은': [_dots(1, 3, 5, 6)],
    '을': [_dots(2, 3, 4, 6)],
    '인': [_dots(1, 3, 4, 5, 6)],
}

# ----------------------------------------------------------------------------
# 숫자 + 수표 (점 3,4,5,6)
# ----------------------------------------------------------------------------
NUMBER_SIGN: List[int] = _dots(3, 4, 5, 6)
NUMBERS: dict = {
    '0': _dots(2, 4, 5),
    '1': _dots(1),
    '2': _dots(1, 2),
    '3': _dots(1, 4),
    '4': _dots(1, 4, 5),
    '5': _dots(1, 5),
    '6': _dots(1, 2, 4),
    '7': _dots(1, 2, 4, 5),
    '8': _dots(1, 2, 5),
    '9': _dots(2, 4),
}

# ----------------------------------------------------------------------------
# 영문자 + 로마자표 (점 3,5,6)
# ----------------------------------------------------------------------------
ROMAN_LETTER_SIGN: List[int] = _dots(3, 5, 6)
ENGLISH_LETTERS: dict = {
    'a': _dots(1),
    'b': _dots(1, 2),
    'c': _dots(1, 4),
    'd': _dots(1, 4, 5),
    'e': _dots(1, 5),
    'f': _dots(1, 2, 4),
    'g': _dots(1, 2, 4, 5),
    'h': _dots(1, 2, 5),
    'i': _dots(2, 4),
    'j': _dots(2, 4, 5),
    'k': _dots(1, 3),
    'l': _dots(1, 2, 3),
    'm': _dots(1, 3, 4),
    'n': _dots(1, 3, 4, 5),
    'o': _dots(1, 3, 5),
    'p': _dots(1, 2, 3, 4),
    'q': _dots(1, 2, 3, 4, 5),
    'r': _dots(1, 2, 3, 5),
    's': _dots(2, 3, 4),
    't': _dots(2, 3, 4, 5),
    'u': _dots(1, 3, 6),
    'v': _dots(1, 2, 3, 6),
    'w': _dots(2, 4, 5, 6),
    'x': _dots(1, 3, 4, 6),
    'y': _dots(1, 3, 4, 5, 6),
    'z': _dots(1, 3, 5, 6),
}

# ----------------------------------------------------------------------------
# 구두점 · 공백
# ----------------------------------------------------------------------------
PUNCTUATION_BRAILLE: dict = {
    ' ': [EMPTY_CELL],
    '.': [_dots(2, 5, 6)],
    ',': [_dots(2)],
    '?': [_dots(2, 3, 6)],
    '!': [_dots(2, 3, 5)],
}


# ============================================================================
# 자모 분해
# ============================================================================

def decompose_hangul(char: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    한글 한 글자 → (초성, 중성, 종성). 한글 아니면 (None, None, None).

    >>> decompose_hangul('사')
    ('ㅅ', 'ㅏ', '')
    >>> decompose_hangul('랑')
    ('ㄹ', 'ㅏ', 'ㅇ')
    """
    try:
        import hgtk
        if not hgtk.checker.is_hangul(char):
            return (None, None, None)
        try:
            return hgtk.letter.decompose(char)
        except hgtk.exception.NotHangulException:
            return (None, None, None)
    except ImportError:
        return _decompose_unicode(char)


def _decompose_unicode(char: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """hgtk 없이 유니코드 기반 분해. 한글 완성형 0xAC00~0xD7A3."""
    if not char or len(char) != 1:
        return (None, None, None)

    code = ord(char)
    if not (0xAC00 <= code <= 0xD7A3):
        return (None, None, None)

    base = code - 0xAC00
    cho_idx = base // (21 * 28)
    jung_idx = (base % (21 * 28)) // 28
    jong_idx = base % 28

    CHO_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ',
                'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    JUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ',
                 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ',
                 'ㅡ', 'ㅢ', 'ㅣ']
    JONG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ',
                 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ',
                 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    return (CHO_LIST[cho_idx], JUNG_LIST[jung_idx], JONG_LIST[jong_idx])


# ============================================================================
# 한글 → 점자
# ============================================================================

def char_to_braille(char: str) -> List[List[int]]:
    """
    한 글자 → 점자 셀 리스트.

    우선순위:
        1) 약자 매칭 (가·사·것·억·...)
        2) 구두점·공백
        3) 한글 분해 후 초성·중성·종성 조합
           - 초성 ㅇ은 생략
           - 복모음은 2셀
           - 겹받침은 2셀
        4) 숫자 → 수표 + 숫자
        5) 영문자 → 로마자표 + 알파벳
        6) 그 외는 빈 셀
    """
    # 1. 약자
    if char in ABBREVIATIONS:
        return [list(cell) for cell in ABBREVIATIONS[char]]

    # 2. 구두점·공백
    if char in PUNCTUATION_BRAILLE:
        return [list(cell) for cell in PUNCTUATION_BRAILLE[char]]

    # 4. 숫자
    if char in NUMBERS:
        return [list(NUMBER_SIGN), list(NUMBERS[char])]

    # 5. 영문자 (대소문자 구분 X — 로마자표 + 소문자 패턴)
    lower = char.lower()
    if lower in ENGLISH_LETTERS:
        return [list(ROMAN_LETTER_SIGN), list(ENGLISH_LETTERS[lower])]

    # 3. 한글 분해
    cho, jung, jong = decompose_hangul(char)
    if cho is None:
        return [list(EMPTY_CELL)]

    patterns: List[List[int]] = []

    # 초성 ㅇ 생략
    if cho != 'ㅇ' and cho in CHOSEONG_BRAILLE:
        patterns.extend([list(cell) for cell in CHOSEONG_BRAILLE[cho]])

    if jung in JUNGSEONG_BRAILLE:
        patterns.extend([list(cell) for cell in JUNGSEONG_BRAILLE[jung]])

    if jong and jong in JONGSEONG_BRAILLE:
        patterns.extend([list(cell) for cell in JONGSEONG_BRAILLE[jong]])

    if not patterns:
        return [list(EMPTY_CELL)]

    return patterns


def text_to_braille(text: str) -> List[List[int]]:
    """문장 → 전체 점자 셀 시퀀스."""
    result: List[List[int]] = []
    for char in text:
        result.extend(char_to_braille(char))
    return result


def text_to_braille_with_meta(text: str) -> List[dict]:
    """
    문장 → 점자 + 메타데이터 (훈련 세션에서 "어떤 글자의 어떤 자모" 추적용).

    Returns:
        [
            {"char": "사", "role": "choseong", "jamo": "ㅅ", "pattern": [...]},
            ...
        ]
        약자로 매칭된 글자는 role="abbreviation", jamo=글자 자체.
    """
    result: List[dict] = []
    for char in text:
        # 약자
        if char in ABBREVIATIONS:
            for pattern in ABBREVIATIONS[char]:
                result.append({
                    "char": char,
                    "role": "abbreviation",
                    "jamo": char,
                    "pattern": list(pattern),
                })
            continue

        # 구두점
        if char in PUNCTUATION_BRAILLE:
            for pattern in PUNCTUATION_BRAILLE[char]:
                result.append({
                    "char": char,
                    "role": "punctuation",
                    "jamo": char,
                    "pattern": list(pattern),
                })
            continue

        # 숫자
        if char in NUMBERS:
            result.append({
                "char": char,
                "role": "number_sign",
                "jamo": "#",
                "pattern": list(NUMBER_SIGN),
            })
            result.append({
                "char": char,
                "role": "number",
                "jamo": char,
                "pattern": list(NUMBERS[char]),
            })
            continue

        # 영문자
        lower = char.lower()
        if lower in ENGLISH_LETTERS:
            result.append({
                "char": char,
                "role": "roman_sign",
                "jamo": "@",
                "pattern": list(ROMAN_LETTER_SIGN),
            })
            result.append({
                "char": char,
                "role": "english",
                "jamo": lower,
                "pattern": list(ENGLISH_LETTERS[lower]),
            })
            continue

        # 한글 분해
        cho, jung, jong = decompose_hangul(char)
        if cho is None:
            continue

        if cho != 'ㅇ' and cho in CHOSEONG_BRAILLE:
            for pattern in CHOSEONG_BRAILLE[cho]:
                result.append({
                    "char": char,
                    "role": "choseong",
                    "jamo": cho,
                    "pattern": list(pattern),
                })
        if jung in JUNGSEONG_BRAILLE:
            for pattern in JUNGSEONG_BRAILLE[jung]:
                result.append({
                    "char": char,
                    "role": "jungseong",
                    "jamo": jung,
                    "pattern": list(pattern),
                })
        if jong and jong in JONGSEONG_BRAILLE:
            for pattern in JONGSEONG_BRAILLE[jong]:
                result.append({
                    "char": char,
                    "role": "jongseong",
                    "jamo": jong,
                    "pattern": list(pattern),
                })

    return result


# ----------------------------------------------------------------------------
# v3 하위 호환 (단일 패턴 조회 — 레거시 엔드포인트에서 사용)
# ----------------------------------------------------------------------------
braille_map = {
    "가": ABBREVIATIONS["가"][0],
    "나": ABBREVIATIONS["나"][0],
    "다": ABBREVIATIONS["다"][0],
    "라": list(_dots(5)),   # ㄹ 초성만 (ㅏ는 별도) — v3는 자모 개념 없었음
    "마": ABBREVIATIONS["마"][0],
    "바": ABBREVIATIONS["바"][0],
    "사": ABBREVIATIONS["사"][0],
    "랑": list(_dots(5)),   # v3 레거시 — 실제는 다중 셀
    "해": list(_dots(2, 4, 5)),
    " ": list(EMPTY_CELL),
}
