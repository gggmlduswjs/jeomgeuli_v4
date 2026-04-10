import { useState, useEffect, useRef } from "react";

// Web Speech API는 표준 DOM 타입에 없어서 최소 인터페이스를 정의
type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start: () => void;
  stop: () => void;
  onresult:
    | ((e: { results: { [index: number]: { [index: number]: { transcript: string } } } }) => void)
    | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
};

type WindowWithSR = Window & {
  SpeechRecognition?: new () => SpeechRecognitionLike;
  webkitSpeechRecognition?: new () => SpeechRecognitionLike;
};

export function useSTT() {
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);

  useEffect(() => {
    const w = window as WindowWithSR;
    const Ctor = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!Ctor) {
      console.warn("이 브라우저는 음성 인식을 지원하지 않습니다.");
      return;
    }

    const recog = new Ctor();
    recog.lang = "ko-KR";
    recog.interimResults = false;
    recog.continuous = false;

    recog.onresult = (e) => {
      const result = e.results[0][0].transcript;
      setText(result);
      setListening(false);
    };
    recog.onerror = () => setListening(false);
    recog.onend = () => setListening(false);

    recognitionRef.current = recog;
  }, []);

  const startListening = () => {
    const recog = recognitionRef.current;
    if (recog && !listening) {
      setText("");
      setListening(true);
      try {
        recog.start();
      } catch {
        setListening(false);
      }
    }
  };

  return { text, listening, startListening };
}
