import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Scan from "./pages/Scan";
import SpeedTraining from "./pages/SpeedTraining";
import SessionReport from "./pages/SessionReport";
import MathDemo from "./pages/MathDemo";
import BrailleConverter from "./pages/BrailleConverter";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/scan" element={<Scan />} />
        <Route path="/training" element={<SpeedTraining />} />
        <Route path="/training/report/:sessionId" element={<SessionReport />} />
        <Route path="/math" element={<MathDemo />} />
        <Route path="/braille" element={<BrailleConverter />} />
      </Routes>
    </BrowserRouter>
  );
}
