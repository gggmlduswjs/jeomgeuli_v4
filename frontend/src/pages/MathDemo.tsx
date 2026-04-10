import { useState } from "react";
import { Link } from "react-router-dom";
import { detectCrop, explainFormula, type DetectResult } from "../api/mathAPI";
import { useTTS } from "../hooks/useTTS";

type Stage = "idle" | "detecting" | "explaining" | "done" | "error";

export default function MathDemo() {
  const { speak } = useTTS();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [stage, setStage] = useState<Stage>("idle");
  const [detect, setDetect] = useState<DetectResult | null>(null);
  const [explanation, setExplanation] = useState<string>("");
  const [error, setError] = useState<string>("");

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setDetect(null);
    setExplanation("");
    setStage("idle");
    setError("");
  };

  const onRun = async () => {
    if (!file) return;
    setError("");
    try {
      setStage("detecting");
      const d = await detectCrop(file);
      setDetect(d);

      if (d.label === "formula") {
        setStage("explaining");
        const text = await explainFormula(file);
        setExplanation(text);
      }
      setStage("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "실행 실패");
      setStage("error");
    }
  };

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-600 hover:text-gray-900 underline">
            홈으로
          </Link>
          <h1 className="text-3xl font-bold">수학 모드 (데모)</h1>
        </div>

        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className="sr-only"
        >
          {stage === "detecting" && "CNN 감지 중"}
          {stage === "explaining" && "Claude Vision 호출 중"}
          {stage === "done" && detect &&
            `${detect.label === "formula" ? "수식" : "본문"} 감지 완료, 신뢰도 ${(
              detect.confidence * 100
            ).toFixed(0)}퍼센트`}
          {stage === "error" && `오류: ${error}`}
        </div>

        <p className="text-gray-700 mb-6">
          수학 페이지에서 수식 부분을 잘라낸 이미지를 업로드하면, CNN 감지기가 수식
          여부를 판별하고 Claude Vision이 한국어로 읽어줍니다.
        </p>

        <section
          aria-labelledby="math-upload-heading"
          className="bg-white rounded-xl shadow p-6 mb-6"
        >
          <h2 id="math-upload-heading" className="text-xl font-semibold mb-4">
            크롭 이미지 업로드
          </h2>
          <label className="block mb-4">
            <span className="sr-only">수식 크롭 이미지 파일 선택</span>
            <input
              type="file"
              accept="image/*"
              onChange={onFileChange}
              aria-label="수식 크롭 이미지 파일 선택"
            />
          </label>
          {preview && (
            <img
              src={preview}
              alt="업로드한 수식 크롭 미리보기"
              className="max-h-64 rounded border mb-4"
            />
          )}
          <button
            onClick={onRun}
            disabled={!file || stage === "detecting" || stage === "explaining"}
            className="px-5 py-3 bg-violet-700 hover:bg-violet-800 text-white rounded disabled:bg-gray-300"
          >
            {stage === "detecting"
              ? "감지 중..."
              : stage === "explaining"
                ? "Claude Vision 호출 중..."
                : "감지 + 설명 실행"}
          </button>
          {error && (
            <p role="alert" className="mt-3 text-red-700">
              {error}
            </p>
          )}
        </section>

        {detect && (
          <section
            aria-labelledby="detect-heading"
            className="bg-white rounded-xl shadow p-6 mb-6"
          >
            <h2 id="detect-heading" className="text-lg font-semibold mb-2">
              CNN 감지 결과
            </h2>
            <div className="flex items-center gap-4">
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  detect.label === "formula"
                    ? "bg-violet-200 text-violet-900"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                {detect.label === "formula" ? "수식" : "본문"}
              </span>
              <span className="text-sm text-gray-700">
                신뢰도 {(detect.confidence * 100).toFixed(1)}%
              </span>
            </div>
          </section>
        )}

        {explanation && (
          <section
            aria-labelledby="explain-heading"
            className="bg-violet-50 rounded-xl p-6"
          >
            <div className="flex items-center justify-between mb-3">
              <h2 id="explain-heading" className="text-lg font-semibold">
                자연어 설명
              </h2>
              <button
                onClick={() => speak(explanation)}
                aria-label="설명을 음성으로 재생"
                className="px-3 py-2 bg-violet-700 hover:bg-violet-800 text-white rounded text-sm"
              >
                음성 재생
              </button>
            </div>
            <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">
              {explanation}
            </p>
          </section>
        )}
      </div>
    </main>
  );
}
