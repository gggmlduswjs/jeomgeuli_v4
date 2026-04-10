import { Link } from "react-router-dom";

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
    subtitle: "수능특강 페이지 → OCR → 지문·핵심어 추출",
    color: "bg-blue-600 hover:bg-blue-700",
  },
  {
    to: "/training",
    title: "2. 속도 훈련",
    subtitle: "핵심어를 3셀 점자로 출력 + 음성 답변 체크",
    color: "bg-emerald-600 hover:bg-emerald-700",
  },
  {
    to: "/math",
    title: "3. 수학 모드 (데모)",
    subtitle: "수식 크롭 → CNN 감지 + Claude Vision 설명",
    color: "bg-violet-600 hover:bg-violet-700",
  },
  {
    to: "/braille",
    title: "4. 점자 변환기",
    subtitle: "텍스트 입력 → 점자 셀 미리보기",
    color: "bg-slate-600 hover:bg-slate-700",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 px-6 py-12">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-2">점글이 v4</h1>
        <p className="text-gray-600 mb-10">
          시각장애 수험생 핵심어 점자 속도 훈련 + 수학 멀티모달 보조
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {MENU.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`block rounded-xl p-6 text-white transition ${item.color}`}
            >
              <div className="text-xl font-semibold">{item.title}</div>
              <div className="text-sm mt-1 opacity-90">{item.subtitle}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
