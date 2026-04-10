import { Link, useLocation } from "react-router-dom";

export default function NotFound() {
  const location = useLocation();

  return (
    <main
      role="alert"
      aria-live="polite"
      className="min-h-screen px-6 py-12 flex items-center justify-center"
    >
      <div className="max-w-lg w-full bg-white rounded-xl shadow p-8">
        <p className="text-sm text-gray-500 mb-2">404</p>
        <h1 className="text-2xl font-bold mb-3">페이지를 찾을 수 없습니다</h1>
        <p className="text-gray-700 mb-4 leading-relaxed">
          요청하신 경로{" "}
          <code className="bg-gray-100 px-2 py-0.5 rounded text-sm">
            {location.pathname}
          </code>
          는 존재하지 않습니다. 홈으로 돌아가서 주요 기능 중 하나를 선택해주세요.
        </p>
        <Link
          to="/"
          className="inline-block px-5 py-3 bg-blue-700 hover:bg-blue-800 text-white rounded"
        >
          홈으로
        </Link>
      </div>
    </main>
  );
}
