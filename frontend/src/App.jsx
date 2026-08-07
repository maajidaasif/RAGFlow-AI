import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import UploadPage from "./pages/UploadPage";
import MyPapers from "./pages/MyPapers";
import History from "./pages/History";
import ResearchGap from "./pages/ResearchGap";
import LiteratureSurvey from "./pages/LiteratureSurvey";
import Report from "./pages/Report";
import Settings from "./pages/Settings";
import Help from "./pages/Help";
import Profile from "./pages/Profile";

import ProtectedRoute from "./components/ProtectedRoute";

function App() {

  const token = localStorage.getItem("token");

  return (

    <BrowserRouter>

      <Routes>

        {/* Login */}

        <Route
          path="/"
          element={
            token
              ? <Navigate to="/dashboard" replace />
              : <Login />
          }
        />

        {/* Register */}

        <Route
          path="/register"
          element={
            token
              ? <Navigate to="/dashboard" replace />
              : <Register />
          }
        />

        {/* Dashboard */}

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Upload Papers */}

        <Route
          path="/upload"
          element={
            <ProtectedRoute>
              <UploadPage />
            </ProtectedRoute>
          }
        />

        {/* My Papers */}

        <Route
          path="/papers"
          element={
            <ProtectedRoute>
              <MyPapers />
            </ProtectedRoute>
          }
        />

        {/* Research Gap */}

        <Route
          path="/research-gap"
          element={
            <ProtectedRoute>
              <ResearchGap />
            </ProtectedRoute>
          }
        />

        {/* Literature Survey */}

        <Route
          path="/literature-survey"
          element={
            <ProtectedRoute>
              <LiteratureSurvey />
            </ProtectedRoute>
          }
        />

        {/* Research Report */}

        <Route
          path="/report"
          element={
            <ProtectedRoute>
              <Report />
            </ProtectedRoute>
          }
        />

        {/* Analysis History */}

        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          }
        />

        {/* Profile */}

        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />

        {/* Settings */}

        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />

        {/* Help */}

        <Route
          path="/help"
          element={
            <ProtectedRoute>
              <Help />
            </ProtectedRoute>
          }
        />

        {/* Unknown Route */}

        <Route
          path="*"
          element={<Navigate to="/" replace />}
        />

      </Routes>

    </BrowserRouter>

  );
}

export default App;