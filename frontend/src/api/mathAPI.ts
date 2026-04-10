import axiosInstance from "./axiosInstance";

export type DetectResult = {
  label: "text" | "formula";
  confidence: number;
};

export async function detectCrop(image: File): Promise<DetectResult> {
  const form = new FormData();
  form.append("image", image);
  const res = await axiosInstance.post<DetectResult>("/math/detect/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function explainFormula(image: File): Promise<string> {
  const form = new FormData();
  form.append("image", image);
  const res = await axiosInstance.post<{ explanation: string }>(
    "/math/explain/",
    form,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return res.data.explanation;
}
