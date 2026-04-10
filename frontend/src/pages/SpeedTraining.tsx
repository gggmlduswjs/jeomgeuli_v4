import { useCallback, useEffect, useRef, useState } from "react";
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
  const [statusMessage, setStatusMessage] = useState<string>("");

  const showStartTimeRef = useRef<number | null>(null);
  const submittedForAnswerRef = useRef<string | null>(null);
  const sessionRef = useRef<Session | null>(null);
  const phaseRef = useRef<Phase>("setup");

  // 최신 session/phase를 keyboard handler에서 참조하기 위한 ref 동기화
  useEffect(() => {
    sessionRef.current = session;
  }, [session]);
  useEffect(() => {
    phaseRef.current = phase;
  }, [phase]);

  const presentWord = useCallback(
    async (sessionId: number, word: string, idx: number, total: number) => {
      try {
        setStatusMessage(`${idx + 1}번째 단어 출력 중`);
        const { attempt } = await showWord(sessionId, word, sendHardware);
        setCurrentAttempt(attempt);
        showStartTimeRef.current = Date.now();
        submittedForAnswerRef.current = null;
        setPhase("waiting_answer");
        speak(`${idx + 1}번째 단어. 답을 말해주세요.`);
        setStatusMessage(`${idx + 1} / ${total}번째 단어 출력 완료. 음성 답변 대기 중.`);
        setTimeout(() => startListening(), 500);
      } catch (e) {
        setError(e instanceof Error ? e.message : "단어 출력 실패");
      }
    },
    [sendHardware, speak, startListening],
  );

  const onFinish = useCallback(async () => {
    const s = sessionRef.current;
    if (!s) return;
    try {
      await finishSession(s.id);
      setPhase("done");
      speak("훈련을 종료합니다.");
      navigate(`/training/report/${s.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "세션 종료 실패");
    }
  }, [navigate, speak]);

  const onStart = useCallback(async () => {
    if (keywords.length === 0) {
      setError("훈련할 단어가 없습니다. 교재 스캔부터 시작하세요.");
      speak("훈련할 단어가 없습니다. 교재 스캔부터 시작하세요.");
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
      speak(`훈련을 시작합니다. 총 ${keywords.length}개 단어.`);
      await presentWord(s.id, keywords[0], 0, keywords.length);
    } catch (e) {
      setError(e instanceof Error ? e.message : "세션 생성 실패");
    }
  }, [keywords, level, cellDurationSec, sourceText, presentWord, speak]);

  const onSkip = useCallback(async () => {
    const s = sessionRef.current;
    if (!s) return;
    speak("건너뜁니다.");
    const nextIdx = wordIdx + 1;
    if (nextIdx >= keywords.length) await onFinish();
    else {
      setWordIdx(nextIdx);
      await presentWord(s.id, keywords[nextIdx], nextIdx, keywords.length);
    }
  }, [wordIdx, keywords, presentWord, speak, onFinish]);

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
        const feedback = correct
          ? "정답입니다."
          : `오답입니다. 정답은 ${currentAttempt.word}.`;
        setStatusMessage(feedback);
        speak(feedback);
        setTimeout(() => {
          const nextIdx = wordIdx + 1;
          if (nextIdx >= keywords.length) {
            void onFinish();
          } else {
            setWordIdx(nextIdx);
            void presentWord(session.id, keywords[nextIdx], nextIdx, keywords.length);
          }
        }, 1500);
      })
      .catch((e) => {
        setError(e instanceof Error ? e.message : "답변 제출 실패");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sttText, phase]);

  // 키보드 단축키: Enter 시작, Space 다시 듣기, S 건너뛰기, Esc 종료
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // 입력 요소에 포커스 중이면 무시
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;

      const p = phaseRef.current;

      if (p === "setup" && e.key === "Enter") {
        e.preventDefault();
        void onStart();
      } else if (p === "waiting_answer") {
        if (e.code === "Space") {
          e.preventDefault();
          startListening();
          speak("다시 들어봅니다.");
        } else if (e.key === "s" || e.key === "S") {
          e.preventDefault();
          void onSkip();
        } else if (e.key === "Escape") {
          e.preventDefault();
          void onFinish();
        }
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onStart, onSkip, onFinish, startListening, speak]);

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-600 hover:text-gray-900 underline">
            홈으로
          </Link>
          <h1 className="text-3xl font-bold">속도 훈련</h1>
        </div>

        {/* 스크린리더 전용 상태 아나운스 */}
        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className="visually-hidden"
        >
          {statusMessage}
        </div>

        {phase === "setup" && (
          <section
            aria-labelledby="setup-heading"
            className="bg-white rounded-xl shadow p-6"
          >
            <h2 id="setup-heading" className="text-xl font-semibold mb-4">
              훈련 준비
            </h2>

            <p className="text-gray-700 mb-4">
              훈련 단어 <strong>{keywords.length}개</strong>
              {keywords.length === 0 && (
                <>
                  {" — "}
                  <Link to="/scan" className="text-blue-700 underline">
                    교재 스캔부터 시작
                  </Link>
                </>
              )}
            </p>

            {keywords.length > 0 && (
              <ul
                aria-label="훈련할 단어 목록"
                className="text-sm text-gray-700 mb-4 flex flex-wrap gap-1 list-none p-0"
              >
                {keywords.map((w, i) => (
                  <li key={i} className="px-2 py-0.5 bg-gray-100 rounded">
                    {w}
                  </li>
                ))}
              </ul>
            )}

            <div className="grid grid-cols-2 gap-4 mb-4">
              <label className="flex flex-col">
                <span className="text-sm text-gray-700 mb-1">레벨</span>
                <select
                  value={level}
                  onChange={(e) => setLevel(Number(e.target.value) as 1 | 2 | 3 | 4)}
                  className="border rounded px-2 py-2"
                >
                  <option value={1}>Lv1 — 입문 (3.0초)</option>
                  <option value={2}>Lv2 — 기초 (2.5초)</option>
                  <option value={3}>Lv3 — 중급 (2.0초)</option>
                  <option value={4}>Lv4 — 고급 (1.5초)</option>
                </select>
              </label>
              <label className="flex flex-col">
                <span className="text-sm text-gray-700 mb-1">셀 표시 시간 (초)</span>
                <input
                  type="number"
                  step="0.1"
                  min="0.5"
                  max="5"
                  value={cellDurationSec}
                  onChange={(e) => setCellDurationSec(Number(e.target.value))}
                  className="border rounded px-2 py-2"
                />
              </label>
            </div>

            <label className="flex items-center gap-2 mb-4">
              <input
                type="checkbox"
                checked={sendHardware}
                onChange={(e) => setSendHardware(e.target.checked)}
              />
              <span>3셀 하드웨어에 실제 출력</span>
            </label>

            <button
              onClick={onStart}
              disabled={keywords.length === 0}
              aria-label="훈련 시작 (엔터 키)"
              className="px-5 py-3 bg-emerald-700 hover:bg-emerald-800 text-white rounded disabled:bg-gray-300"
            >
              훈련 시작 (Enter)
            </button>
            {error && (
              <p role="alert" className="mt-3 text-red-700">
                {error}
              </p>
            )}
          </section>
        )}

        {(phase === "running" || phase === "waiting_answer") && currentAttempt && (
          <section
            aria-labelledby="training-heading"
            className="bg-white rounded-xl shadow p-6 text-center"
          >
            <h2 id="training-heading" className="visually-hidden">
              훈련 진행 중
            </h2>

            <div className="text-sm text-gray-600 mb-2" aria-hidden="true">
              {wordIdx + 1} / {keywords.length}
            </div>
            <div className="text-5xl font-bold mb-6" aria-hidden="true">
              {currentAttempt.word}
            </div>

            <div
              className="flex justify-center gap-2 mb-6 flex-wrap"
              role="img"
              aria-label={`${currentAttempt.word}의 점자 ${currentAttempt.braille_cells.length}셀`}
            >
              {currentAttempt.braille_cells.map((cell, i) => (
                <BrailleCell key={i} pattern={cell} size="md" />
              ))}
            </div>

            <div className="text-gray-700 mb-4" aria-hidden="true">
              {listening
                ? "듣는 중..."
                : sttText
                  ? `인식: "${sttText}"`
                  : "잠시 후 마이크가 켜집니다"}
            </div>

            <div className="flex justify-center gap-2 flex-wrap">
              <button
                onClick={() => {
                  startListening();
                  speak("다시 들어봅니다.");
                }}
                aria-label="다시 듣기 (스페이스 키)"
                className="px-4 py-3 bg-blue-700 hover:bg-blue-800 text-white rounded"
              >
                다시 듣기 (Space)
              </button>
              <button
                onClick={onSkip}
                aria-label="건너뛰기 (S 키)"
                className="px-4 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded"
              >
                건너뛰기 (S)
              </button>
              <button
                onClick={onFinish}
                aria-label="훈련 종료 (ESC 키)"
                className="px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded"
              >
                종료 (Esc)
              </button>
            </div>
            {error && (
              <p role="alert" className="mt-3 text-red-700">
                {error}
              </p>
            )}
          </section>
        )}
      </div>
    </main>
  );
}
