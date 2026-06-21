import { useState, useEffect } from "react"
import Header from "../components/Header"
import { resultados as resultadosApi } from "../services/api"
import { useAuth } from "../context/AuthContext"
import type { Resultado, ResultadoDetalhe } from "../types"

export default function AlunoDashboard() {
    const { usuario } = useAuth()
    const [listaResultados, setListaResultados] = useState<Resultado[]>([])
    const [detalhe, setDetalhe] = useState<ResultadoDetalhe | null>(null)
    const [carregando, setCarregando] = useState<boolean>(true)

    useEffect(() => {
        resultadosApi.listar()
            .then(setListaResultados)
            .finally(() => setCarregando(false))
    }, [])

    async function verDetalhe(id: number): Promise<void> {
        if (detalhe?.id === id) { setDetalhe(null); return }
        const dados = await resultadosApi.detalhar(id)
        setDetalhe(dados)
    }

    if (carregando) return <div className="p-8 text-center">Carregando...</div>

    return (
        <div className="min-h-screen bg-gray-100">
            <Header />
            <main className="max-w-3xl mx-auto p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Olá, {usuario?.nome}!</h2>
                <p className="text-gray-500 mb-6">Aqui estão seus resultados de provas.</p>

                {listaResultados.length === 0
                    ? <div className="bg-white rounded-2xl shadow p-8 text-center text-gray-400">
                        Você ainda não tem resultados cadastrados.
                    </div>
                    : <div className="space-y-4">
                        {listaResultados.map(r => (
                            <div key={r.id} className="bg-white rounded-2xl shadow p-5">
                                <div className="flex justify-between items-center">
                                    <div>
                                        <p className="font-semibold text-gray-800">Prova #{r.prova_id}</p>
                                        <p className="text-sm text-gray-500 mt-1">
                                            {r.total_acertos} acertos · {new Date(r.corrigido_em).toLocaleDateString("pt-BR")}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <span className="text-3xl font-bold text-blue-700">{r.nota}</span>
                                        <p className="text-xs text-gray-400">/ 10</p>
                                    </div>
                                </div>

                                <button onClick={() => verDetalhe(r.id)}
                                    className="mt-3 text-sm text-blue-600 hover:underline">
                                    {detalhe?.id === r.id ? "Ocultar detalhes ↑" : "Ver detalhes →"}
                                </button>

                                {detalhe?.id === r.id && (
                                    <div className="mt-4 border-t pt-4">
                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <p className="font-medium text-green-600 mb-2">
                                                    ✅ Acertos ({detalhe.acertos.length})
                                                </p>
                                                <div className="flex flex-wrap gap-1">
                                                    {detalhe.acertos.map(q => (
                                                        <span key={q} className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">
                                                            Q{q}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                            <div>
                                                <p className="font-medium text-red-500 mb-2">
                                                    ❌ Erros ({detalhe.erros.length})
                                                </p>
                                                <div className="flex flex-wrap gap-1">
                                                    {detalhe.erros.map(q => (
                                                        <span key={q} className="bg-red-100 text-red-600 px-2 py-0.5 rounded text-xs">
                                                            Q{q}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                }
            </main>
        </div>
    )
}