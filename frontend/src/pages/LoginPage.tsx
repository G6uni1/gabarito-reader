import { useState, FormEvent } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

export default function LoginPage() {
    const [email, setEmail] = useState<string>("")
    const [senha, setSenha] = useState<string>("")
    const [erro, setErro] = useState<string>("")
    const [carregando, setCarregando] = useState<boolean>(false)

    const { login } = useAuth()
    const navigate = useNavigate()

    async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
        e.preventDefault()
        setErro("")
        setCarregando(true)

        try {
            const usuario = await login(email, senha)
            if (usuario.perfil === "professor" || usuario.perfil === "admin") {
                navigate("/professor")
            } else {
                navigate("/aluno")
            }
        } catch (err) {
            setErro(err instanceof Error ? err.message : "Erro ao fazer login")
        } finally {
            setCarregando(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center">
            <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-blue-700">📋</h1>
                    <h2 className="text-2xl font-bold text-gray-800 mt-2">Gabarito Reader</h2>
                    <p className="text-gray-500 text-sm mt-1">Entre com sua conta</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="seu@email.com"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
                        <input
                            type="password"
                            value={senha}
                            onChange={e => setSenha(e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    {erro && (
                        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2">
                            {erro}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={carregando}
                        className="w-full bg-blue-700 text-white font-semibold py-2 rounded-lg hover:bg-blue-800 transition disabled:opacity-50"
                    >
                        {carregando ? "Entrando..." : "Entrar"}
                    </button>
                </form>
            </div>
        </div>
    )
}