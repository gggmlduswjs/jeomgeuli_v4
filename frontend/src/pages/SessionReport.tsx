import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getSession, type Session } from "../api/trainingAPI";

export default function SessionReport() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<Session | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (!sessionId) return;
    getSession(Number(sessionId))
      .then(setSession)
      .catch((e) => setError(e instanceof Error ? e.message : "로드 실패"));
  }, [sessionId]);

  if (error)
    return (
      <div className="p-10 text-red-600">
        {error} — <Link to="/">홈으로</Link>
      </div>
    );

  if (!session) return <div className="p-10 text-gray-500">로딩 중...</div>;

  const incorrect = session.attempts.filter((a) => !a.is_correct);
  const accuracyPct = (session.accuracy * 100).toFixed(0);

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-600 hover:text-gray-900 underline">
            홈으로
          </Link>
          <h1 className="text-3xl font-bold">훈련 리포트</h1>
        </div>

        <div
          role="status"
          aria-live="polite"
          className="sr-only"
        >
          정답률 {accuracyPct}퍼센트, 총 {session.total_words}개 중{" "}
          {session.correct_count}개 정답.
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <Metric label="정답률" value={`${accuracyPct}%`} />
          <Metric
            label="정답 / 총 단어"
            value={`${session.correct_count} / ${session.total_words}`}
          />
          <Metric
            label="평균 반응 시간"
            value={
              session.avg_response_ms != null
                ? `${(session.avg_response_ms / 1000).toFixed(2)}초`
                : "-"
            }
          />
        </div>

        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-3">세션 정보</h2>
          <dl className="text-sm space-y-1 text-gray-700">
            <Row k="레벨" v={`Lv${session.level}`} />
            <Row k="셀 표시 시간" v={`${session.cell_duration_sec}초`} />
            <Row k="시작" v={new Date(session.created_at).toLocaleString("ko-KR")} />
            <Row
              k="종료"
              v={
                session.finished_at
                  ? new Date(session.finished_at).toLocaleString("ko-KR")
                  : "진행 중"
              }
            />
          </dl>
        </div>

        <div className="bg-white rounded-xl shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-3">
            단어별 결과 ({session.attempts.length})
          </h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2">#</th>
                <th className="py-2">출제</th>
                <th className="py-2">답변</th>
                <th className="py-2">결과</th>
                <th className="py-2 text-right">반응 (ms)</th>
              </tr>
            </thead>
            <tbody>
              {session.attempts.map((a) => (
                <tr key={a.id} className="border-b last:border-0">
                  <td className="py-2 text-gray-400">{a.index + 1}</td>
                  <td className="py-2 font-medium">{a.word}</td>
                  <td className="py-2 text-gray-600">{a.user_answer || "-"}</td>
                  <td className="py-2">
                    <span
                      className={a.is_correct ? "text-emerald-600" : "text-red-500"}
                    >
                      {a.is_correct ? "O" : "X"}
                    </span>
                  </td>
                  <td className="py-2 text-right text-gray-500">
                    {a.response_ms ?? "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {incorrect.length > 0 && (
          <div className="bg-amber-50 rounded-xl p-6 mb-6">
            <h2 className="text-lg font-semibold mb-3">복습 필요 ({incorrect.length})</h2>
            <div className="flex flex-wrap gap-2">
              {incorrect.map((a) => (
                <span key={a.id} className="px-3 py-1 bg-white rounded-full text-sm">
                  {a.word}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-3">
          <Link
            to="/training"
            className="px-5 py-3 bg-emerald-700 hover:bg-emerald-800 text-white rounded"
          >
            다시 훈련
          </Link>
          <Link to="/" className="px-5 py-3 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded">
            홈으로
          </Link>
        </div>
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-xl shadow p-5">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-2xl font-bold mt-1">{value}</div>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex">
      <dt className="w-32 text-gray-500">{k}</dt>
      <dd>{v}</dd>
    </div>
  );
}
