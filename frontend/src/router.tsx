import { BrowserRouter, Routes, Route } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import Home from "./pages/Home";
import Scan from "./pages/Scan";
import SpeedTraining from "./pages/SpeedTraining";
import SessionReport from "./pages/SessionReport";
import MathDemo from "./pages/MathDemo";
import BrailleConverter from "./pages/BrailleConverter";
import NotFound from "./pages/NotFound";

export default function AppRouter() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/scan" element={<Scan />} />
          <Route path="/training" element={<SpeedTraining />} />
          <Route path="/training/report/:sessionId" element={<SessionReport />} />
          <Route path="/math" element={<MathDemo />} />
          <Route path="/braille" element={<BrailleConverter />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
