import { useState } from "react";
import { Link } from "react-router-dom";
import { convertWord, type BrailleMetaEntry } from "../api/brailleAPI";
import { sendText } from "../api/hardwareAPI";
import BrailleCell from "../components/BrailleCell";

const ROLE_LABEL: Record<BrailleMetaEntry["role"], string> = {
  abbreviation: "약자",
  choseong: "초성",
  jungseong: "중성",
  jongseong: "종성",
  punctuation: "구두점",
  number_sign: "수표",
  number: "숫자",
  roman_sign: "로마자표",
  english: "영문",
};

export default function BrailleConverter() {
  const [text, setText] = useState("사랑해");
  const [meta, setMeta] = useState<BrailleMetaEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hwStatus, setHwStatus] = useState("");

  const onConvert = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await convertWord(text);
      setMeta(res.decomposition);
    } catch (e) {
      setError(e instanceof Error ? e.message : "변환 실패");
    } finally {
      setLoading(false);
    }
  };

  const onSendHardware = async () => {
    setHwStatus("전송 중...");
    try {
      const res = await sendText(text);
      setHwStatus(res.ok ? `전송 완료 (${res.total_cells}셀)` : "전송 실패");
    } catch (e) {
      setHwStatus(e instanceof Error ? `오류: ${e.message}` : "오류");
    }
  };

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-600 hover:text-gray-900 underline">
            홈으로
          </Link>
          <h1 className="text-3xl font-bold">점자 변환기</h1>
        </div>

        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className="sr-only"
        >
          {meta.length > 0 && `${meta.length}셀로 변환됨`}
          {hwStatus}
          {error && `오류: ${error}`}
        </div>

        <section
          aria-labelledby="input-heading"
          className="bg-white rounded-xl shadow p-6 mb-6"
        >
          <h2 id="input-heading" className="text-xl font-semibold mb-4">
            텍스트 입력
          </h2>
          <label className="block mb-4">
            <span className="sr-only">변환할 한글 텍스트</span>
            <input
              type="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full border border-gray-400 rounded px-4 py-3 text-lg"
              placeholder="변환할 한글"
              aria-label="변환할 한글 텍스트 입력"
            />
          </label>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={onConvert}
              disabled={loading || !text.trim()}
              className="px-5 py-3 bg-slate-700 hover:bg-slate-800 text-white rounded disabled:bg-gray-300"
            >
              {loading ? "변환 중..." : "변환"}
            </button>
            <button
              onClick={onSendHardware}
              disabled={!text.trim()}
              aria-label="3셀 하드웨어로 점자 전송"
              className="px-5 py-3 bg-emerald-700 hover:bg-emerald-800 text-white rounded disabled:bg-gray-300"
            >
              3셀 하드웨어 전송
            </button>
          </div>
          {hwStatus && <p className="mt-3 text-gray-700">{hwStatus}</p>}
          {error && (
            <p role="alert" className="mt-3 text-red-700">
              {error}
            </p>
          )}
        </section>

        {meta.length > 0 && (
          <section
            aria-labelledby="decomp-heading"
            className="bg-white rounded-xl shadow p-6"
          >
            <h2 id="decomp-heading" className="text-lg font-semibold mb-4">
              자모 분해 ({meta.length}셀)
            </h2>
            <ol className="flex flex-wrap gap-3 list-none p-0">
              {meta.map((m, i) => (
                <li key={i}>
                  <BrailleCell
                    pattern={m.pattern}
                    size="md"
                    label={`${m.jamo} · ${ROLE_LABEL[m.role]}`}
                  />
                </li>
              ))}
            </ol>
          </section>
        )}
      </div>
    </main>
  );
}
