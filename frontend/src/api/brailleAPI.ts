import axiosInstance from "./axiosInstance";

export type BrailleCell = number[]; // [p1, p2, p3, p4, p5, p6]

export type BrailleMetaEntry = {
  char: string;
  role:
    | "abbreviation"
    | "choseong"
    | "jungseong"
    | "jongseong"
    | "punctuation"
    | "number_sign"
    | "number"
    | "roman_sign"
    | "english";
  jamo: string;
  pattern: BrailleCell;
};

export async function convertText(text: string) {
  const res = await axiosInstance.post<{
    text: string;
    cells: BrailleCell[];
    cell_count: number;
  }>("/braille/convert_text/", { text });
  return res.data;
}

export async function convertWord(text: string) {
  const res = await axiosInstance.post<{
    text: string;
    decomposition: BrailleMetaEntry[];
    cell_count: number;
  }>("/braille/convert_word/", { text });
  return res.data;
}
