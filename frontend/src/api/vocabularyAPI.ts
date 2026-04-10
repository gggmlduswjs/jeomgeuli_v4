import axiosInstance from "./axiosInstance";

export type Keyword = { word: string; score: number };

export async function extractKeywords(
  text: string,
  topK = 12,
  strategy: "sbert" | "tfidf" = "sbert",
): Promise<Keyword[]> {
  const res = await axiosInstance.post<{
    strategy: string;
    keywords: Keyword[];
  }>("/vocabulary/extract/", { text, top_k: topK, strategy });
  return res.data.keywords;
}
