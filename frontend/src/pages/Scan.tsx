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
    <main className="min-h-screen px-6 py-10">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-600 hover:text-gray-900 underline">
            홈으로
          </Link>
          <h1 className="text-3xl font-bold">교재 스캔</h1>
        </div>

        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className="visually-hidden"
        >
          {stage === "ocr" && "OCR 처리 중입니다"}
          {stage === "vocab" && "핵심어를 추출하고 있습니다"}
          {stage === "ready" &&
            `추출 완료. 섹션 ${sections.length}개, 핵심어 ${keywords.length}개.`}
          {stage === "error" && `오류: ${error}`}
        </div>

        <section
          aria-labelledby="upload-heading"
          className="bg-white rounded-xl shadow p-6 mb-6"
        >
          <h2 id="upload-heading" className="text-xl font-semibold mb-4">
            이미지 업로드
          </h2>
          <label className="block mb-4">
            <span className="sr-only">교재 이미지 파일 선택</span>
            <input
              type="file"
              accept="image/*"
              onChange={onFileChange}
              aria-label="교재 이미지 파일 선택"
            />
          </label>
          {preview && (
            <img
              src={preview}
              alt="업로드한 교재 미리보기"
              className="max-h-80 rounded border"
            />
          )}
          <button
            onClick={onExtract}
            disabled={!file || stage === "ocr" || stage === "vocab"}
            className="mt-4 px-5 py-3 bg-blue-700 hover:bg-blue-800 text-white rounded disabled:bg-gray-300"
          >
            {stage === "ocr"
              ? "OCR 처리 중..."
              : stage === "vocab"
                ? "핵심어 추출 중..."
                : "OCR + 핵심어 추출"}
          </button>
          {error && (
            <p role="alert" className="mt-3 text-red-700">
              {error}
            </p>
          )}
        </section>

        {sections.length > 0 && (
          <section
            aria-labelledby="sections-heading"
            className="bg-white rounded-xl shadow p-6 mb-6"
          >
            <h2 id="sections-heading" className="text-lg font-semibold mb-3">
              섹션 분류 ({sections.length})
            </h2>
            <ul className="space-y-2 list-none p-0">
              {sections.map((s, i) => (
                <li
                  key={i}
                  className={`px-3 py-2 rounded text-sm ${SECTION_COLOR[s.type]}`}
                >
                  <span className="text-xs font-mono text-gray-600 mr-2">
                    [{s.type}]
                  </span>
                  {s.text}
                </li>
              ))}
            </ul>
          </section>
        )}

        {keywords.length > 0 && (
          <section
            aria-labelledby="keywords-heading"
            className="bg-white rounded-xl shadow p-6"
          >
            <h2 id="keywords-heading" className="text-lg font-semibold mb-3">
              핵심어 ({selectedIdx.size} / {keywords.length} 선택됨)
            </h2>
            <div
              role="group"
              aria-label="핵심어 선택"
              className="flex flex-wrap gap-2 mb-5"
            >
              {keywords.map((k, i) => {
                const checked = selectedIdx.has(i);
                return (
                  <button
                    key={i}
                    onClick={() => toggle(i)}
                    role="checkbox"
                    aria-checked={checked}
                    aria-label={`${k.word}, 점수 ${k.score.toFixed(3)}`}
                    className={`px-3 py-2 rounded-full text-sm transition ${
                      checked
                        ? "bg-emerald-700 text-white"
                        : "bg-gray-100 text-gray-800 border border-gray-300"
                    }`}
                  >
                    {k.word}
                  </button>
                );
              })}
            </div>
            <button
              onClick={goToTraining}
              disabled={selectedIdx.size === 0}
              className="px-5 py-3 bg-emerald-700 hover:bg-emerald-800 text-white rounded disabled:bg-gray-300"
            >
              선택한 단어로 훈련 시작
            </button>
          </section>
        )}
      </div>
    </main>
  );
}
