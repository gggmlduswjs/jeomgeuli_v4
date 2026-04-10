"""
JY-SOFT 3셀 점자 모듈 시리얼 통신 매니저 (싱글톤)

통신:
    Django (Python) → pyserial → Arduino Uno/Nano → braille.h → 3셀 모듈

프로토콜:
    - Baud rate: 9600
    - 한 번에 3셀 (한 한글 글자) 전송
    - 바이트 3개: 각 바이트의 하위 6비트 = 점자 패턴
    - 셀 사이 구분자: 없음 (고정 3바이트)
    - 클리어 명령: [0x00, 0x00, 0x00]

Arduino 스케치: ../../arduino/braille_receiver/braille_receiver.ino
"""

import time
from typing import List, Optional


class BrailleHardwareManager:
    """3셀 점자 모듈 싱글톤 매니저"""

    _instance: Optional["BrailleHardwareManager"] = None
    _serial = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, port: str = None, baud: int = 9600):
        if not hasattr(self, '_initialized'):
            self.port = port or self._auto_detect_port()
            self.baud = baud
            self._initialized = True

    def _auto_detect_port(self) -> str:
        """
        OS별 기본 시리얼 포트 추정.
        TODO: pyserial.tools.list_ports로 자동 감지 개선
        """
        import platform
        system = platform.system()
        if system == "Windows":
            return "COM3"
        elif system == "Darwin":  # macOS
            return "/dev/tty.usbmodem1101"
        else:  # Linux
            return "/dev/ttyUSB0"

    def connect(self) -> bool:
        """시리얼 포트 열기"""
        try:
            import serial
            self._serial = serial.Serial(self.port, self.baud, timeout=2)
            time.sleep(2)  # Arduino 부팅 대기
            return True
        except Exception as e:
            print(f"[hardware] 시리얼 연결 실패: {e}")
            self._serial = None
            return False

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def disconnect(self):
        if self._serial:
            self._serial.close()
            self._serial = None

    def send_cells(self, cells: List[List[int]]) -> bool:
        """
        3셀 단위로 점자 패턴 전송.

        Args:
            cells: 점자 셀 리스트. 각 셀은 [p1, p2, p3, p4, p5, p6].
                   3셀씩 나눠서 전송. 3의 배수가 아니면 빈 셀로 패딩.

        Returns:
            전송 성공 여부
        """
        if not self.is_connected():
            if not self.connect():
                return False

        # 3셀씩 청크 분할
        padded = list(cells)
        while len(padded) % 3 != 0:
            padded.append([0, 0, 0, 0, 0, 0])

        for i in range(0, len(padded), 3):
            chunk = padded[i:i+3]
            bytes_data = bytes(self._pattern_to_byte(cell) for cell in chunk)
            try:
                self._serial.write(bytes_data)
                self._serial.flush()
            except Exception as e:
                print(f"[hardware] 시리얼 전송 실패: {e}")
                return False

        return True

    def clear(self) -> bool:
        """모든 점 꺼짐"""
        return self.send_cells([[0, 0, 0, 0, 0, 0]] * 3)

    def _pattern_to_byte(self, pattern: List[int]) -> int:
        """
        6점 패턴 → 1바이트.

        Pattern: [p1, p2, p3, p4, p5, p6]
        Byte bits: p1=bit0, p2=bit1, p3=bit2, p4=bit3, p5=bit4, p6=bit5
        """
        byte = 0
        for i, p in enumerate(pattern[:6]):
            if p:
                byte |= (1 << i)
        return byte


def send_word_with_delay(cells: List[List[int]], duration: float = 2.0) -> bool:
    """
    단어를 3셀씩 순차 출력 + 각 청크 사이 지연.
    훈련 세션에서 사용.

    Args:
        cells: 단어 전체 점자 셀
        duration: 각 3셀 청크 표시 시간 (초)

    Returns:
        성공 여부
    """
    manager = BrailleHardwareManager()

    if not manager.is_connected() and not manager.connect():
        return False

    # 3셀씩 나눠서 표시
    for i in range(0, len(cells), 3):
        chunk = cells[i:i+3]
        while len(chunk) < 3:
            chunk.append([0, 0, 0, 0, 0, 0])

        manager.send_cells(chunk)
        time.sleep(duration)

    manager.clear()
    return True
