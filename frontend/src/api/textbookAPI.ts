import axiosInstance from "./axiosInstance";

export type Section = {
  type: "body" | "question" | "choice" | "explanation" | "unknown";
  text: string;
};

export type ExtractResponse = {
  raw_lines: string[];
  sections: Section[];
  body_text: string;
};

export async function extractFromImage(
  image: File,
  preprocess = false,
): Promise<ExtractResponse> {
  const form = new FormData();
  form.append("image", image);
  form.append("preprocess", preprocess ? "true" : "false");

  const res = await axiosInstance.post<ExtractResponse>(
    "/textbook/extract/",
    form,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return res.data;
}
