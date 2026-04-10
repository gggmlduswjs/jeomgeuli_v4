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
    <div className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-500 hover:text-gray-700">
            ← 홈
          </Link>
          <h1 className="text-3xl font-bold">점자 변환기</h1>
        </div>

        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="w-full border rounded px-4 py-2 text-lg mb-4"
            placeholder="변환할 한글"
          />
          <div className="flex gap-2">
            <button
              onClick={onConvert}
              disabled={loading || !text.trim()}
              className="px-5 py-2 bg-slate-600 text-white rounded disabled:bg-gray-300"
            >
              {loading ? "변환 중..." : "변환"}
            </button>
            <button
              onClick={onSendHardware}
              disabled={!text.trim()}
              className="px-5 py-2 bg-emerald-600 text-white rounded disabled:bg-gray-300"
            >
              3셀 하드웨어 전송
            </button>
          </div>
          {hwStatus && <p className="mt-3 text-sm text-gray-600">{hwStatus}</p>}
          {error && <p className="mt-3 text-red-600 text-sm">{error}</p>}
        </div>

        {meta.length > 0 && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4">
              자모 분해 ({meta.length}셀)
            </h2>
            <div className="flex flex-wrap gap-3">
              {meta.map((m, i) => (
                <BrailleCell
                  key={i}
                  pattern={m.pattern}
                  size="md"
                  label={`${m.jamo} · ${ROLE_LABEL[m.role]}`}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
