"""
hardware 앱 테스트 — 3셀 점자 모듈 제어.

CI/테스트 환경에는 Arduino 미연결. connect() 실패 시 is_connected=False,
send/clear/send_text 는 503 반환하는 것까지 검증.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from .serial_manager import BrailleHardwareManager


class PatternToByteTest(TestCase):
    """BrailleHardwareManager._pattern_to_byte 비트 packing 검증"""

    def setUp(self):
        self.m = BrailleHardwareManager()

    def test_empty_pattern(self):
        self.assertEqual(self.m._pattern_to_byte([0, 0, 0, 0, 0, 0]), 0)

    def test_dot1_only(self):
        # p1 = bit 0 = 0b000001 = 1
        self.assertEqual(self.m._pattern_to_byte([1, 0, 0, 0, 0, 0]), 0b000001)

    def test_dot6_only(self):
        # p6 = bit 5 = 0b100000 = 32
        self.assertEqual(self.m._pattern_to_byte([0, 0, 0, 0, 0, 1]), 0b100000)

    def test_all_dots(self):
        self.assertEqual(self.m._pattern_to_byte([1, 1, 1, 1, 1, 1]), 0b111111)

    def test_ga_pattern(self):
        """약자 '가' = 점 1, 2, 4, 6 → bits 0, 1, 3, 5 = 0b101011 = 43"""
        self.assertEqual(
            self.m._pattern_to_byte([1, 1, 0, 1, 0, 1]),
            0b101011,
        )


class ManagerIsolationTest(TestCase):
    """싱글톤이지만 테스트 간 상태 격리 필요"""

    def setUp(self):
        # 싱글톤 상태 리셋
        BrailleHardwareManager._instance = None
        BrailleHardwareManager._serial = None

    def test_not_connected_by_default(self):
        m = BrailleHardwareManager()
        self.assertFalse(m.is_connected())

    def test_connect_fails_without_hardware(self):
        m = BrailleHardwareManager(port="COM_INVALID_XYZ")
        # pyserial 설치 여부와 무관하게 False 반환해야 함 (try-except)
        result = m.connect()
        self.assertFalse(result)
        self.assertFalse(m.is_connected())


class HardwareStatusViewTest(TestCase):
    def setUp(self):
        BrailleHardwareManager._instance = None
        BrailleHardwareManager._serial = None
        self.client = APIClient()

    def test_status_returns_not_connected(self):
        res = self.client.get("/api/hardware/status/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["connected"])
        self.assertIn("port", data)
        self.assertIn("baud", data)

    def test_connect_fails_gracefully(self):
        res = self.client.post("/api/hardware/connect/")
        # 실기기 없으므로 503
        self.assertEqual(res.status_code, 503)

    def test_clear_without_hardware_returns_503(self):
        res = self.client.post("/api/hardware/clear/")
        self.assertEqual(res.status_code, 503)


class HardwareSendViewTest(TestCase):
    def setUp(self):
        BrailleHardwareManager._instance = None
        BrailleHardwareManager._serial = None
        self.client = APIClient()

    def test_send_without_cells_returns_400(self):
        res = self.client.post("/api/hardware/send/", {}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_send_invalid_cell_format_returns_400(self):
        """cells 원소가 None이면 슬라이싱 시 TypeError → 400"""
        res = self.client.post(
            "/api/hardware/send/",
            {"cells": [None]},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_send_non_list_cells_returns_400(self):
        res = self.client.post(
            "/api/hardware/send/",
            {"cells": "not a list"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_send_valid_cells_503_without_hardware(self):
        res = self.client.post(
            "/api/hardware/send/",
            {"cells": [[1, 0, 0, 0, 0, 0]]},
            format="json",
        )
        # 유효한 요청이지만 실기기 없으므로 503
        self.assertEqual(res.status_code, 503)

    def test_send_text_without_text_returns_400(self):
        res = self.client.post("/api/hardware/send_text/", {}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_send_text_valid_503_without_hardware(self):
        res = self.client.post(
            "/api/hardware/send_text/",
            {"text": "사랑"},
            format="json",
        )
        self.assertEqual(res.status_code, 503)
