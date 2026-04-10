"""
한국 점자 변환 테스트

매핑은 jeomgeuli-suneung-helper/firmware/braille_3cell/BrailleMap.h 에서 포팅.
KS X 9211 (2017 개정) 기준:
    - 초성 ㅇ 생략
    - 복모음 6개(ㅒㅘㅙㅝㅞㅟ) 2셀
    - 겹받침 2셀
    - 약자 26개 우선 매칭

실행: python manage.py test apps.braille
"""

from django.test import TestCase
from .utils import (
    ABBREVIATIONS,
    CHOSEONG_BRAILLE,
    COMPOUND_VOWEL_SECOND,
    ENGLISH_LETTERS,
    JONGSEONG_BRAILLE,
    JUNGSEONG_BRAILLE,
    NUMBER_SIGN,
    NUMBERS,
    ROMAN_LETTER_SIGN,
    _decompose_unicode,
    char_to_braille,
    decompose_hangul,
    text_to_braille,
    text_to_braille_with_meta,
)


class DecomposeHangulTest(TestCase):
    def test_basic_decompose(self):
        self.assertEqual(decompose_hangul('가'), ('ㄱ', 'ㅏ', ''))
        self.assertEqual(decompose_hangul('나'), ('ㄴ', 'ㅏ', ''))
        self.assertEqual(decompose_hangul('해'), ('ㅎ', 'ㅐ', ''))

    def test_with_jongseong(self):
        self.assertEqual(decompose_hangul('강'), ('ㄱ', 'ㅏ', 'ㅇ'))
        self.assertEqual(decompose_hangul('랑'), ('ㄹ', 'ㅏ', 'ㅇ'))
        self.assertEqual(decompose_hangul('학'), ('ㅎ', 'ㅏ', 'ㄱ'))

    def test_double_consonant(self):
        self.assertEqual(decompose_hangul('까'), ('ㄲ', 'ㅏ', ''))
        self.assertEqual(decompose_hangul('따'), ('ㄸ', 'ㅏ', ''))

    def test_double_jongseong(self):
        self.assertEqual(decompose_hangul('값'), ('ㄱ', 'ㅏ', 'ㅄ'))
        self.assertEqual(decompose_hangul('없'), ('ㅇ', 'ㅓ', 'ㅄ'))

    def test_non_hangul(self):
        self.assertEqual(decompose_hangul('a'), (None, None, None))
        self.assertEqual(decompose_hangul('1'), (None, None, None))

    def test_unicode_fallback(self):
        self.assertEqual(_decompose_unicode('가'), ('ㄱ', 'ㅏ', ''))
        self.assertEqual(_decompose_unicode('랑'), ('ㄹ', 'ㅏ', 'ㅇ'))
        self.assertEqual(_decompose_unicode('a'), (None, None, None))


class AbbreviationTest(TestCase):
    """약자 26개 우선 매칭"""

    def test_single_cell_abbreviations(self):
        """CV 약자 11개 — 모두 1셀"""
        for abbr in ['가', '나', '다', '마', '바', '사', '자', '카', '타', '파', '하']:
            with self.subTest(abbr=abbr):
                self.assertEqual(len(char_to_braille(abbr)), 1)

    def test_geot_is_two_cells(self):
        """'것' 만 2셀 약자"""
        result = char_to_braille('것')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [0, 0, 0, 0, 1, 1])  # 점 5, 6
        self.assertEqual(result[1], [0, 1, 1, 1, 0, 0])  # 점 2, 3, 4

    def test_eok_series(self):
        """'억·언·얼·연·열·영' 1셀 약자"""
        for abbr in ['억', '언', '얼', '연', '열', '영']:
            with self.subTest(abbr=abbr):
                self.assertEqual(len(char_to_braille(abbr)), 1)

    def test_ga_pattern(self):
        """'가' = 점 1, 2, 4, 6"""
        self.assertEqual(char_to_braille('가'), [[1, 1, 0, 1, 0, 1]])

    def test_abbreviation_takes_priority_over_decomposition(self):
        """'사'는 약자로 1셀이지 ㅅ+ㅏ 2셀이 아니다"""
        self.assertEqual(len(char_to_braille('사')), 1)

    def test_abbreviation_count(self):
        self.assertEqual(len(ABBREVIATIONS), 26)


class InitialIeungOmitTest(TestCase):
    """초성 ㅇ 생략 규정"""

    def test_a_omits_choseong(self):
        """'아' = ㅇ(생략) + ㅏ(1,2,6) = 1셀"""
        result = char_to_braille('아')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [1, 1, 0, 0, 0, 1])  # ㅏ

    def test_eung_is_two_cells(self):
        """'응' = ㅇ생략 + ㅡ + ㅇ받침 = 2셀"""
        result = char_to_braille('응')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], JUNGSEONG_BRAILLE['ㅡ'][0])
        self.assertEqual(result[1], JONGSEONG_BRAILLE['ㅇ'][0])

    def test_choseong_ieung_mapping_is_empty(self):
        """테이블에서도 ㅇ 초성 = 빈 리스트"""
        self.assertEqual(CHOSEONG_BRAILLE['ㅇ'], [])


class CompoundVowelTest(TestCase):
    """복모음 6개 — 첫 셀 + ㅐ 2셀 구조"""

    def test_compound_vowels_two_cells(self):
        for v in ['ㅒ', 'ㅘ', 'ㅙ', 'ㅝ', 'ㅞ', 'ㅟ']:
            with self.subTest(vowel=v):
                self.assertEqual(len(JUNGSEONG_BRAILLE[v]), 2)
                self.assertEqual(JUNGSEONG_BRAILLE[v][1], COMPOUND_VOWEL_SECOND)

    def test_wa_character(self):
        """'와' = ㅇ생략 + ㅘ(2셀) = 2셀"""
        result = char_to_braille('와')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [1, 1, 1, 0, 0, 1])     # ㅘ 첫 셀 1,2,3,6
        self.assertEqual(result[1], [1, 1, 1, 0, 1, 0])     # ㅐ 1,2,3,5

    def test_gwa_character(self):
        """'과' = ㄱ(1) + ㅘ(2) = 3셀"""
        result = char_to_braille('과')
        self.assertEqual(len(result), 3)


class JongseongTest(TestCase):
    """종성 — 단일·겹받침"""

    def test_simple_jongseong(self):
        """'강' = ㄱ + ㅏ + ㅇ(받침) = 3셀"""
        result = char_to_braille('강')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[2], [0, 1, 1, 0, 1, 1])  # ㅇ 종성 2,3,5,6

    def test_double_jongseong_values(self):
        """'값' = ㄱ + ㅏ + ㅄ(2셀) = 4셀"""
        result = char_to_braille('값')
        self.assertEqual(len(result), 4)

    def test_jongseong_ieung_differs_from_initial(self):
        """종성 ㅇ(2,3,5,6) != 초성 ㅇ(없음)"""
        self.assertEqual(JONGSEONG_BRAILLE['ㅇ'], [[0, 1, 1, 0, 1, 1]])
        self.assertEqual(CHOSEONG_BRAILLE['ㅇ'], [])


class DoubleConsonantInitialTest(TestCase):
    """쌍자음 초성 — 된소리표 + 기본 자음"""

    def test_kka(self):
        """'까' = ㄲ(6+4 = 2셀) + ㅏ(1) = 3셀"""
        result = char_to_braille('까')
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], [0, 0, 0, 0, 0, 1])  # 된소리표 점 6
        self.assertEqual(result[1], [0, 0, 0, 1, 0, 0])  # ㄱ 점 4
        self.assertEqual(result[2], [1, 1, 0, 0, 0, 1])  # ㅏ


class NumberTest(TestCase):
    def test_digit_emits_number_sign(self):
        """'1' = 수표 + 1 = 2셀"""
        result = char_to_braille('1')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], NUMBER_SIGN)
        self.assertEqual(result[1], NUMBERS['1'])

    def test_zero(self):
        result = char_to_braille('0')
        self.assertEqual(result[1], NUMBERS['0'])


class EnglishTest(TestCase):
    def test_letter_emits_roman_sign(self):
        """'a' = 로마자표 + a = 2셀"""
        result = char_to_braille('a')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], ROMAN_LETTER_SIGN)
        self.assertEqual(result[1], ENGLISH_LETTERS['a'])

    def test_uppercase_uses_lowercase_pattern(self):
        """대문자는 소문자 패턴을 재사용 (v4는 대문자표 미구현)"""
        self.assertEqual(char_to_braille('A')[1], ENGLISH_LETTERS['a'])


class TextToBrailleTest(TestCase):
    def test_sarang(self):
        """'사랑' = 사(약자 1셀) + 랑(ㄹ+ㅏ+ㅇ 3셀) = 4셀"""
        result = text_to_braille('사랑')
        self.assertEqual(len(result), 4)

    def test_with_space(self):
        """'사 랑' = 1 + 1(공백) + 3 = 5셀"""
        result = text_to_braille('사 랑')
        self.assertEqual(len(result), 5)

    def test_hangul_with_punctuation(self):
        """'사랑.' = 4 + 1 = 5셀"""
        result = text_to_braille('사랑.')
        self.assertEqual(len(result), 5)

    def test_empty(self):
        self.assertEqual(text_to_braille(''), [])


class MetaConversionTest(TestCase):
    def test_abbreviation_role(self):
        """약자는 role='abbreviation'"""
        result = text_to_braille_with_meta('사')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['role'], 'abbreviation')
        self.assertEqual(result[0]['jamo'], '사')

    def test_decomposition_structure(self):
        """약자 아닌 글자 — '랑' = ㄹ + ㅏ + ㅇ"""
        result = text_to_braille_with_meta('랑')
        roles = [item['role'] for item in result]
        self.assertEqual(roles, ['choseong', 'jungseong', 'jongseong'])
        self.assertEqual(result[0]['jamo'], 'ㄹ')
        self.assertEqual(result[1]['jamo'], 'ㅏ')
        self.assertEqual(result[2]['jamo'], 'ㅇ')

    def test_initial_ieung_omitted_in_meta(self):
        """'아' 메타데이터에 초성 ㅇ 항목이 없다"""
        result = text_to_braille_with_meta('아')
        roles = [item['role'] for item in result]
        self.assertNotIn('choseong', roles)
        self.assertEqual(roles, ['jungseong'])

    def test_number_meta(self):
        result = text_to_braille_with_meta('3')
        self.assertEqual([item['role'] for item in result], ['number_sign', 'number'])


class RegressionTest(TestCase):
    """v3 하위 호환"""

    def test_v3_braille_map_preserved(self):
        from .utils import braille_map
        self.assertIn('가', braille_map)
        self.assertIn('사', braille_map)
        self.assertIn(' ', braille_map)
