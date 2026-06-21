import {
    createContext,
    useContext,
    useState,
    useEffect,
    ReactNode,
} from "react"
import { auth } from "../services/api"
import type { Usuario } from "../types"

// ─── Tipos do contexto ───────────────────────────────────────────────────────

interface AuthContextType {
    usuario: Usuario | null
    login: (email: string, senha: string) => Promise<Usuario>
    logout: () => void
    carregando: boolean
}

// ─── Criação do contexto ─────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextType | null>(null)

// ─── Provider ────────────────────────────────────────────────────────────────

interface AuthProviderProps {
    children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [usuario, setUsuario] = useState<Usuario | null>(null)
    const [carregando, setCarregando] = useState(true)

    useEffect(() => {
        const token = localStorage.getItem("token")
        if (token) {
            auth.me()
                .then(setUsuario)
                .catch(() => localStorage.removeItem("token"))
                .finally(() => setCarregando(false))
        } else {
            setCarregando(false)
        }
    }, [])

    async function login(email: string, senha: string): Promise<Usuario> {
        const dados = await auth.login(email, senha)
        localStorage.setItem("token", dados.access_token)
        const eu = await auth.me()
        setUsuario(eu)
        return eu
    }

    function logout(): void {
        localStorage.removeItem("token")
        setUsuario(null)
    }

    return (
        <AuthContext.Provider value={{ usuario, login, logout, carregando }}>
            {children}
        </AuthContext.Provider>
    )
}

// ─── Hook ────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextType {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error("useAuth deve ser usado dentro de AuthProvider")
    return ctx
}