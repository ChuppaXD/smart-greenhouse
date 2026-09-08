import { BrowserRouter, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import DashboardPage from "./pages/DashboardPage";

function HomePage() {
  return (
    <div className="space-y-4">
      <h2 className="text-3xl font-bold text-slate-900">
        Smart Greenhouse
      </h2>

      <p className="text-slate-600">
        Welcome to the Smart Greenhouse application.
      </p>

      <p className="text-slate-600">
        Use the navigation above to open the dashboard.
      </p>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}