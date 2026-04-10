import { Link, useNavigate } from "react-router-dom";
import { DEMO_SAMPLES } from "../data/demoSamples";
import { useTrainingStore } from "../store/trainingStore";

type MenuItem = {
  to: string;
  title: string;
  subtitle: string;
  color: string;
};

const MENU: MenuItem[] = [
  {
    to: "/scan",
    title: "1. 교재 스캔",
    subtitle: "수능특강 페이지를 촬영하면 OCR로 지문을 추출하고 핵심어를 뽑아줍니다.",
    color: "bg-blue-700 hover:bg-blue-800",
  },
  {
    to: "/training",
    title: "2. 속도 훈련",
    subtitle: "핵심어를 3셀 점자 모듈로 출력하고 음성 답변으로 반응 시간을 측정합니다.",
    color: "bg-emerald-700 hover:bg-emerald-800",
  },
  {
    to: "/math",
    title: "3. 수학 모드",
    subtitle: "수식 이미지를 CNN으로 감지하고 Claude Vision이 한국어로 읽어줍니다.",
    color: "bg-violet-700 hover:bg-violet-800",
  },
  {
    to: "/braille",
    title: "4. 점자 변환기",
    subtitle: "텍스트를 한국 점자 표준으로 변환해 셀 단위로 확인합니다.",
    color: "bg-slate-700 hover:bg-slate-800",
  },
];

export default function Home() {
  const navigate = useNavigate();
  const { setSourceText, setKeywords } = useTrainingStore();

  const loadSample = (id: string) => {
    const sample = DEMO_SAMPLES.find((s) => s.id === id);
    if (!sample) return;
    setSourceText(sample.sourceText);
    setKeywords(sample.keywords);
    navigate("/training");
  };

  return (
    <main className="min-h-screen px-6 py-12">
      <div className="max-w-3xl mx-auto">
        <header className="mb-10">
          <h1 className="text-4xl font-bold mb-2">점글이 v4</h1>
          <p className="text-gray-700">
            시각장애 수험생을 위한 핵심어 점자 속도 훈련 도구와 수학 멀티모달 보조.
          </p>
        </header>

        <nav aria-label="주요 기능" className="mb-10">
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-4 list-none p-0">
            {MENU.map((item, i) => {
              const descId = `menu-desc-${i}`;
              return (
                <li key={item.to}>
                  <Link
                    to={item.to}
                    aria-describedby={descId}
                    className={`block rounded-xl p-6 text-white transition ${item.color}`}
                  >
                    <div className="text-xl font-semibold">{item.title}</div>
                    <div id={descId} className="text-sm mt-2 leading-relaxed opacity-95">
                      {item.subtitle}
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <section
          aria-labelledby="demo-heading"
          className="bg-amber-50 border border-amber-200 rounded-xl p-6"
        >
          <h2 id="demo-heading" className="text-lg font-semibold mb-2">
            빠른 시연
          </h2>
          <p className="text-sm text-gray-700 mb-4">
            교재 사진·Arduino 기기·API 키가 없어도 샘플 지문으로 훈련 흐름을 바로
            확인할 수 있습니다.
          </p>
          <ul className="grid grid-cols-1 md:grid-cols-3 gap-2 list-none p-0">
            {DEMO_SAMPLES.map((sample) => (
              <li key={sample.id}>
                <button
                  onClick={() => loadSample(sample.id)}
                  aria-label={`샘플 "${sample.title}"로 훈련 시작. 핵심어 ${sample.keywords.length}개`}
                  className="w-full text-left bg-white hover:bg-amber-100 border border-amber-300 rounded-lg p-4 transition"
                >
                  <div className="font-medium text-gray-900">{sample.title}</div>
                  <div className="text-xs text-gray-600 mt-1">
                    핵심어 {sample.keywords.length}개
                  </div>
                </button>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </main>
  );
}
