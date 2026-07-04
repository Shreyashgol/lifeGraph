import { Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "@/components/protected-route";
import ActivityPage from "@/pages/activity";
import DashboardPage from "@/pages/dashboard";
import InsightsPage from "@/pages/insights";
import LoginPage from "@/pages/login";
import MemoryPage from "@/pages/memory";
import OnboardingPage from "@/pages/onboarding";
import SummaryPage from "@/pages/summary";
import TimelinePage from "@/pages/timeline";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/activity" element={<ActivityPage />} />
        <Route path="/timeline" element={<TimelinePage />} />
        <Route path="/memory" element={<MemoryPage />} />
        <Route path="/insights" element={<InsightsPage />} />
        <Route path="/summary" element={<SummaryPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
