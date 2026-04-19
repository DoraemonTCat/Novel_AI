import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import Layout from './components/Layout/Layout'
import LoginPage from './components/Auth/LoginPage'
import AuthCallback from './components/Auth/AuthCallback'
import Dashboard from './components/Dashboard/Dashboard'
import CreationWizard from './components/NovelCreation/CreationWizard'
import NovelDetail from './components/NovelDetail/NovelDetail'
import SettingsPage from './components/Settings/SettingsPage'

function ProtectedRoute({ children }) {
  const token = useAuthStore((s) => s.accessToken)
  if (!token) return <Navigate to="/login" replace />
  return children
}

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/auth/callback" element={<AuthCallback />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="create" element={<CreationWizard />} />
        <Route path="novel/:novelId" element={<NovelDetail />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
