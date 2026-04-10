import { create } from "zustand";

type TrainingStore = {
  sourceText: string;
  keywords: string[];
  level: 1 | 2 | 3 | 4;
  cellDurationSec: number;

  setSourceText: (text: string) => void;
  setKeywords: (keywords: string[]) => void;
  setLevel: (level: 1 | 2 | 3 | 4) => void;
  setCellDurationSec: (s: number) => void;
  reset: () => void;
};

export const useTrainingStore = create<TrainingStore>((set) => ({
  sourceText: "",
  keywords: [],
  level: 1,
  cellDurationSec: 2.0,

  setSourceText: (text) => set({ sourceText: text }),
  setKeywords: (keywords) => set({ keywords }),
  setLevel: (level) => set({ level }),
  setCellDurationSec: (cellDurationSec) => set({ cellDurationSec }),
  reset: () =>
    set({ sourceText: "", keywords: [], level: 1, cellDurationSec: 2.0 }),
}));
