import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  createSession,
  finishSession,
  showWord,
  submitAnswer,
  type Session,
  type WordAttempt,
} from "../api/trainingAPI";
import { useTrainingStore } from "../store/trainingStore";
import { useSTT } from "../hooks/useSTT";
import { useTTS } from "../hooks/useTTS";
import BrailleCell from "../components/BrailleCell";

type Phase = "setup" | "running" | "waiting_answer" | "done";

export default function SpeedTraining() {
  const navigate = useNavigate();
  const { keywords, sourceText, level, cellDurationSec, setLevel, setCellDurationSec } =
    useTrainingStore();

  const { text: sttText, listening, startListening } = useSTT();
  const { speak } = useTTS();

  const [phase, setPhase] = useState<Phase>("setup");
  const [session, setSession] = useState<Session | null>(null);
  const [wordIdx, setWordIdx] = useState(0);
  const [currentAttempt, setCurrentAttempt] = useState<WordAttempt | null>(null);
  const [sendHardware, setSendHardware] = useState(true);
  const [error, setError] = useState<string>("");

  const showStartTimeRef = useRef<number | null>(null);
  const submittedForAnswerRef = useRef<string | null>(null);

  const onStart = async () => {
    if (keywords.length === 0) {
      setError("훈련할 단어가 없습니다. 교재 스캔부터 시작하세요.");
      return;
    }
    setError("");
    try {
      const s = await createSession({
        level,
        cell_duration_sec: cellDurationSec,
        source_text: sourceText,
      });
      setSession(s);
      setPhase("running");
      setWordIdx(0);
      await presentWord(s.id, keywords[0]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "세션 생성 실패");
    }
  };

  const presentWord = async (sessionId: number, word: string) => {
    try {
      const { attempt } = await showWord(sessionId, word, sendHardware);
      setCurrentAttempt(attempt);
      showStartTimeRef.current = Date.now();
      submittedForAnswerRef.current = null;
      setPhase("waiting_answer");
      // 브라우저 STT 자동 시작
      setTimeout(() => startListening(), 300);
    } catch (e) {
      setError(e instanceof Error ? e.message : "단어 출력 실패");
    }
  };

  // STT 결과 수신 → 자동 제출
  useEffect(() => {
    if (
      phase !== "waiting_answer" ||
      !sttText ||
      !currentAttempt ||
      !session ||
      submittedForAnswerRef.current === sttText
    )
      return;

    submittedForAnswerRef.current = sttText;
    const responseMs = showStartTimeRef.current
      ? Date.now() - showStartTimeRef.current
      : undefined;

    submitAnswer(session.id, {
      attempt_id: currentAttempt.id,
      user_answer: sttText.trim(),
      response_ms: responseMs,
    })
      .then((updated) => {
        const correct = updated.is_correct;
        speak(correct ? "정답" : `오답. ${currentAttempt.word}`);
        // 다음 단어로
        setTimeout(() => {
          const nextIdx = wordIdx + 1;
          if (nextIdx >= keywords.length) {
            void onFinish();
          } else {
            setWordIdx(nextIdx);
            void presentWord(session.id, keywords[nextIdx]);
          }
        }, 1200);
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "답변 제출 실패");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sttText, phase]);

  const onFinish = async () => {
    if (!session) return;
    try {
      await finishSession(session.id);
      setPhase("done");
      navigate(`/training/report/${session.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "세션 종료 실패");
    }
  };

  const onSkip = async () => {
    if (!session) return;
    const nextIdx = wordIdx + 1;
    if (nextIdx >= keywords.length) await onFinish();
    else {
      setWordIdx(nextIdx);
      await presentWord(session.id, keywords[nextIdx]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-500 hover:text-gray-700">
            ← 홈
          </Link>
          <h1 className="text-3xl font-bold">속도 훈련</h1>
        </div>

        {phase === "setup" && (
          <div className="bg-white rounded-xl shadow p-6">
            <p className="text-gray-600 mb-4">
              훈련 단어: <strong>{keywords.length}개</strong>
              {keywords.length === 0 && (
                <>
                  {" "}
                  —{" "}
                  <Link to="/scan" className="text-blue-600 underline">
                    교재 스캔부터 시작
                  </Link>
                </>
              )}
            </p>

            {keywords.length > 0 && (
              <div className="text-sm text-gray-500 mb-4 flex flex-wrap gap-1">
                {keywords.map((w, i) => (
                  <span key={i} className="px-2 py-0.5 bg-gray-100 rounded">
                    {w}
                  </span>
                ))}
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 mb-4">
              <label className="flex flex-col">
                <span className="text-sm text-gray-600 mb-1">레벨</span>
                <select
                  value={level}
                  onChange={(e) => setLevel(Number(e.target.value) as 1 | 2 | 3 | 4)}
                  className="border rounded px-2 py-1"
                >
                  <option value={1}>Lv1 — 입문 (3.0초)</option>
                  <option value={2}>Lv2 — 기초 (2.5초)</option>
                  <option value={3}>Lv3 — 중급 (2.0초)</option>
                  <option value={4}>Lv4 — 고급 (1.5초)</option>
                </select>
              </label>
              <label className="flex flex-col">
                <span className="text-sm text-gray-600 mb-1">셀 표시 시간 (초)</span>
                <input
                  type="number"
                  step="0.1"
                  min="0.5"
                  max="5"
                  value={cellDurationSec}
                  onChange={(e) => setCellDurationSec(Number(e.target.value))}
                  className="border rounded px-2 py-1"
                />
              </label>
            </div>

            <label className="flex items-center gap-2 mb-4">
              <input
                type="checkbox"
                checked={sendHardware}
                onChange={(e) => setSendHardware(e.target.checked)}
              />
              <span className="text-sm">3셀 하드웨어에 실제 출력</span>
            </label>

            <button
              onClick={onStart}
              disabled={keywords.length === 0}
              className="px-5 py-2 bg-emerald-600 text-white rounded disabled:bg-gray-300"
            >
              훈련 시작
            </button>
            {error && <p className="mt-3 text-red-600 text-sm">{error}</p>}
          </div>
        )}

        {(phase === "running" || phase === "waiting_answer") && currentAttempt && (
          <div className="bg-white rounded-xl shadow p-6 text-center">
            <div className="text-sm text-gray-500 mb-2">
              {wordIdx + 1} / {keywords.length}
            </div>
            <div className="text-5xl font-bold mb-6">{currentAttempt.word}</div>

            <div className="flex justify-center gap-2 mb-6 flex-wrap">
              {currentAttempt.braille_cells.map((cell, i) => (
                <BrailleCell key={i} pattern={cell} size="md" />
              ))}
            </div>

            <div className="text-sm text-gray-600 mb-4">
              {listening
                ? "🎤 듣는 중..."
                : sttText
                  ? `인식: "${sttText}"`
                  : "잠시 후 마이크가 켜집니다"}
            </div>

            <div className="flex justify-center gap-2">
              <button
                onClick={startListening}
                className="px-4 py-2 bg-blue-600 text-white rounded"
              >
                다시 듣기
              </button>
              <button
                onClick={onSkip}
                className="px-4 py-2 bg-gray-400 text-white rounded"
              >
                건너뛰기
              </button>
              <button
                onClick={onFinish}
                className="px-4 py-2 bg-red-500 text-white rounded"
              >
                종료
              </button>
            </div>
            {error && <p className="mt-3 text-red-600 text-sm">{error}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
