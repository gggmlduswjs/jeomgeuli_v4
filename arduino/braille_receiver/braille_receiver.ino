/*
 * JY-SOFT 3셀 점자 모듈 시리얼 수신기
 *
 * 프로토콜:
 *   Django(Python) → pyserial → Arduino → braille.h → 3셀 모듈
 *   - Baud: 9600
 *   - 한 번에 3바이트 수신 (3셀 × 6점)
 *   - 각 바이트 하위 6비트 = 점자 패턴
 *   - 클리어: [0x00, 0x00, 0x00]
 *
 * 핀 (JY-SOFT 기본):
 *   DATA  → 2
 *   LATCH → 3
 *   CLOCK → 4
 *
 * 전원:
 *   5V 어댑터 (2A 이상 권장)
 *   또는 7.4V 리튬 배터리 / 18650 × 2
 */

#include "braille.h"

// 핀 설정
const int DATA_PIN = 2;
const int LATCH_PIN = 3;
const int CLOCK_PIN = 4;

// 연결된 모듈 수 (3셀 = 1세트 = no_module 3)
const int NUM_MODULES = 3;

// braille.h 라이브러리 인스턴스
braille bra(DATA_PIN, LATCH_PIN, CLOCK_PIN, NUM_MODULES);

// 수신 버퍼
byte buffer[3];
int buffer_idx = 0;

void setup() {
  Serial.begin(9600);
  bra.begin();

  // 부팅 시 전체 끄기
  for (int cell = 0; cell < NUM_MODULES; cell++) {
    for (int dot = 0; dot < 6; dot++) {
      bra.off(cell, dot);
    }
  }
  bra.refresh();

  Serial.println("READY");
}

void loop() {
  // 3바이트 단위로 처리
  if (Serial.available() >= 3) {
    Serial.readBytes(buffer, 3);

    // 각 셀에 패턴 적용
    for (int cell = 0; cell < NUM_MODULES; cell++) {
      byte pattern = buffer[cell];
      for (int dot = 0; dot < 6; dot++) {
        if (pattern & (1 << dot)) {
          bra.on(cell, dot);
        } else {
          bra.off(cell, dot);
        }
      }
    }
    bra.refresh();

    // ACK
    Serial.println("OK");
  }
}
