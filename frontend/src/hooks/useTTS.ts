export function useTTS() {
    const speak = (text: string) => {
      if (!window.speechSynthesis) {
        alert("이 브라우저는 음성 출력을 지원하지 않습니다.");
        return;
      }
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = "ko-KR";
      utter.rate = 1;
      utter.pitch = 1;
      window.speechSynthesis.speak(utter);
    };
  
    return { speak };
  }
  