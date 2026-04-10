import axiosInstance from "./axiosInstance";
import type { BrailleCell } from "./brailleAPI";

export async function getStatus() {
  const res = await axiosInstance.get<{
    port: string;
    baud: number;
    connected: boolean;
  }>("/hardware/status/");
  return res.data;
}

export async function connect() {
  const res = await axiosInstance.post<{ connected: boolean; port: string }>(
    "/hardware/connect/",
  );
  return res.data;
}

export async function clearCells() {
  const res = await axiosInstance.post<{ ok: boolean }>("/hardware/clear/");
  return res.data;
}

export async function sendCells(cells: BrailleCell[]) {
  const res = await axiosInstance.post("/hardware/send/", { cells });
  return res.data;
}

export async function sendText(text: string, duration?: number) {
  const res = await axiosInstance.post("/hardware/send_text/", {
    text,
    ...(duration !== undefined && { duration }),
  });
  return res.data;
}
