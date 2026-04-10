/**
 * 포트폴리오 시연용 샘플 데이터
 *
 * 사용 맥락:
 *   - 심사관이 교재 사진·Arduino 기기·API 키 없이도 전체 흐름을 돌려볼 수 있게
 *   - OCR + 핵심어 추출 단계를 우회하고 바로 속도 훈련에 진입
 */

export type DemoSample = {
  id: string;
  title: string;
  subject: "korean" | "math";
  sourceText: string;
  keywords: string[];
};

export const DEMO_SAMPLES: DemoSample[] = [
  {
    id: "literature-interpretation",
    title: "문학 해석의 다양성",
    subject: "korean",
    sourceText:
      "문학 작품의 해석은 독자의 경험과 시대적 배경에 따라 달라진다. " +
      "특히 상징과 은유가 풍부한 시는 다양한 해석의 여지를 남긴다. " +
      "작가의 의도를 완전히 파악하기는 어렵지만, 텍스트 안에서 근거를 찾는 것이 중요하다.",
    keywords: ["문학", "해석", "독자", "시대", "상징", "은유", "작가", "근거"],
  },
  {
    id: "science-ecosystem",
    title: "생태계의 균형",
    subject: "korean",
    sourceText:
      "생태계는 수많은 생물과 무생물 요소가 복잡하게 상호작용하는 체계이다. " +
      "먹이사슬의 한 단계가 무너지면 전체 균형이 흔들리며, " +
      "인간의 개입은 이러한 연결고리에 큰 영향을 미친다.",
    keywords: ["생태계", "생물", "무생물", "먹이사슬", "균형", "인간", "개입", "영향"],
  },
  {
    id: "history-modernization",
    title: "근대화의 과정",
    subject: "korean",
    sourceText:
      "근대화는 단순한 서구화가 아니라 전통과 새로운 제도의 만남이다. " +
      "개항 이후 조선은 서양 문물을 받아들이면서도 주권을 지키려 노력했다. " +
      "이 시기의 개혁과 저항은 오늘날까지 이어지는 역사적 질문을 남긴다.",
    keywords: ["근대화", "서구화", "전통", "개항", "조선", "서양", "주권", "개혁"],
  },
];
