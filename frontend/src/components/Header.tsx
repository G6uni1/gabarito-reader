import { useAuth } from "../context/AuthContext"
import { useNavigate } from "react-router-dom"

export default function Header() {
    const { usuario, logout } = useAuth()
    const navigate = useNavigate()

    function handleLogout(): void {
        logout()
        navigate("/login")
    }

    return (
        <header className="bg-blue-700 text-white px-6 py-4 flex justify-between items-center shadow">
            <h1 className="text-xl font-bold tracking-wide">📋 Gabarito Reader</h1>
            <div className="flex items-center gap-4">
                <span className="text-sm opacity-90">
                    {usuario?.nome} · <span className="capitalize">{usuario?.perfil}</span>
                </span>
                <button
                    onClick={handleLogout}
                    className="bg-white text-blue-700 text-sm font-semibold px-3 py-1 rounded hover:bg-blue-50 transition"
                >
                    Sair
                </button>
            </div>
        </header>
    )
}