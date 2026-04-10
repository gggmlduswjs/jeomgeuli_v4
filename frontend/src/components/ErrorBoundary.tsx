import { Component, type ErrorInfo, type ReactNode } from "react";

/**
 * 전역 에러 바운더리.
 *
 * React 렌더 / 생명주기 / 이벤트 핸들러 밖 코드에서 발생한 예외를 잡는다.
 * fetch 실패 같은 비동기 에러는 각 페이지의 try/catch + setError 로 처리되므로
 * 이 바운더리의 주 역할은 "예상치 못한 JS 예외로 앱이 빈 화면이 되는 것 방지".
 *
 * 시각장애 사용자를 고려해 role="alert" 로 스크린리더에 즉시 안내.
 */

type Props = {
  children: ReactNode;
};

type State = {
  error: Error | null;
};

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // 개발 환경에서 스택을 콘솔에 남겨 디버깅
    console.error("ErrorBoundary caught:", error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ error: null });
  };

  render() {
    const { error } = this.state;

    if (error) {
      return (
        <main
          role="alert"
          aria-live="assertive"
          className="min-h-screen px-6 py-12 flex items-center justify-center"
        >
          <div className="max-w-lg w-full bg-white rounded-xl shadow p-8 border border-red-200">
            <h1 className="text-2xl font-bold text-red-700 mb-3">
              예상치 못한 오류가 발생했습니다
            </h1>
            <p className="text-gray-700 mb-4 leading-relaxed">
              화면을 그리는 중 문제가 생겼습니다. 홈으로 돌아가 다시 시도해주세요.
              문제가 반복되면 페이지를 새로고침하거나 브라우저 콘솔의 오류
              메시지를 확인해주세요.
            </p>
            <details className="mb-4 text-sm text-gray-600">
              <summary className="cursor-pointer">오류 상세</summary>
              <pre className="mt-2 whitespace-pre-wrap bg-gray-100 p-3 rounded text-xs">
                {error.message}
              </pre>
            </details>
            <div className="flex gap-2">
              <a
                href="/"
                onClick={this.handleReset}
                className="px-5 py-3 bg-blue-700 hover:bg-blue-800 text-white rounded inline-block"
              >
                홈으로
              </a>
              <button
                onClick={() => window.location.reload()}
                className="px-5 py-3 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded"
              >
                새로고침
              </button>
            </div>
          </div>
        </main>
      );
    }

    return this.props.children;
  }
}
