import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import ProtectedRoute from "./components/ProtectedRoute"
import LoginPage from "./pages/LoginPage"
import ProfessorDashboard from "./pages/ProfessorDashboard"
import AlunoDashboard from "./pages/AlunoDashboard"

export default function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/professor" element={
                        <ProtectedRoute perfil="professor">
                            <ProfessorDashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="/aluno" element={
                        <ProtectedRoute perfil="aluno">
                            <AlunoDashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="*" element={<Navigate to="/login" replace />} />
                </Routes>
            </AuthProvider>
        </BrowserRouter>
    )
}