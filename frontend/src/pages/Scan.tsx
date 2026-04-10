import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { extractFromImage, type Section } from "../api/textbookAPI";
import { extractKeywords, type Keyword } from "../api/vocabularyAPI";
import { useTrainingStore } from "../store/trainingStore";

type Stage = "idle" | "ocr" | "vocab" | "ready" | "error";

const SECTION_COLOR: Record<Section["type"], string> = {
  body: "bg-white",
  question: "bg-amber-50",
  choice: "bg-blue-50",
  explanation: "bg-gray-100",
  unknown: "bg-red-50",
};

export default function Scan() {
  const navigate = useNavigate();
  const { setSourceText, setKeywords } = useTrainingStore();

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [stage, setStage] = useState<Stage>("idle");
  const [error, setError] = useState<string>("");

  const [sections, setSections] = useState<Section[]>([]);
  const [bodyText, setBodyText] = useState<string>("");
  const [keywords, setLocalKeywords] = useState<Keyword[]>([]);
  const [selectedIdx, setSelectedIdx] = useState<Set<number>>(new Set());

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setStage("idle");
    setSections([]);
    setBodyText("");
    setLocalKeywords([]);
    setSelectedIdx(new Set());
    setError("");
  };

  const onExtract = async () => {
    if (!file) return;
    setError("");
    try {
      setStage("ocr");
      const ocr = await extractFromImage(file, true);
      setSections(ocr.sections);
      setBodyText(ocr.body_text);

      setStage("vocab");
      const kws = await extractKeywords(ocr.body_text || ocr.raw_lines.join("\n"), 12);
      setLocalKeywords(kws);
      setSelectedIdx(new Set(kws.map((_, i) => i)));
      setStage("ready");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "알 수 없는 오류";
      setError(msg);
      setStage("error");
    }
  };

  const toggle = (idx: number) => {
    const next = new Set(selectedIdx);
    if (next.has(idx)) next.delete(idx);
    else next.add(idx);
    setSelectedIdx(next);
  };

  const goToTraining = () => {
    const selectedWords = keywords
      .filter((_, i) => selectedIdx.has(i))
      .map((k) => k.word);
    setSourceText(bodyText);
    setKeywords(selectedWords);
    navigate("/training");
  };

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-500 hover:text-gray-700">
            ← 홈
          </Link>
          <h1 className="text-3xl font-bold">교재 스캔</h1>
        </div>

        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <input
            type="file"
            accept="image/*"
            onChange={onFileChange}
            className="mb-4"
          />
          {preview && (
            <img
              src={preview}
              alt="업로드 미리보기"
              className="max-h-80 rounded border"
            />
          )}
          <button
            onClick={onExtract}
            disabled={!file || stage === "ocr" || stage === "vocab"}
            className="mt-4 px-5 py-2 bg-blue-600 text-white rounded disabled:bg-gray-300"
          >
            {stage === "ocr"
              ? "OCR 처리 중..."
              : stage === "vocab"
                ? "핵심어 추출 중..."
                : "OCR + 핵심어 추출"}
          </button>
          {error && <p className="mt-3 text-red-600 text-sm">{error}</p>}
        </div>

        {sections.length > 0 && (
          <div className="bg-white rounded-xl shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-3">섹션 분류</h2>
            <div className="space-y-2">
              {sections.map((s, i) => (
                <div
                  key={i}
                  className={`px-3 py-2 rounded text-sm ${SECTION_COLOR[s.type]}`}
                >
                  <span className="text-xs font-mono text-gray-500 mr-2">
                    [{s.type}]
                  </span>
                  {s.text}
                </div>
              ))}
            </div>
          </div>
        )}

        {keywords.length > 0 && (
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-3">
              핵심어 ({selectedIdx.size}/{keywords.length} 선택됨)
            </h2>
            <div className="flex flex-wrap gap-2 mb-5">
              {keywords.map((k, i) => (
                <button
                  key={i}
                  onClick={() => toggle(i)}
                  className={`px-3 py-1 rounded-full text-sm transition ${
                    selectedIdx.has(i)
                      ? "bg-emerald-600 text-white"
                      : "bg-gray-100 text-gray-500"
                  }`}
                  title={`score: ${k.score.toFixed(3)}`}
                >
                  {k.word}
                </button>
              ))}
            </div>
            <button
              onClick={goToTraining}
              disabled={selectedIdx.size === 0}
              className="px-5 py-2 bg-emerald-600 text-white rounded disabled:bg-gray-300"
            >
              선택한 단어로 훈련 시작 →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
