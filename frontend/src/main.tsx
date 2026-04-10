import React from "react";
import ReactDOM from "react-dom/client";
import AppRouter from "./router"; // ✅ 라우터 import
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AppRouter />   {/* ✅ Router로 전체 감싸기 */}
  </React.StrictMode>
);