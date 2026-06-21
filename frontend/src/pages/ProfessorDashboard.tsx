import { useState, useEffect, FormEvent, ChangeEvent } from "react"
import Header from "../components/Header"
import { provas as provasApi, resultados as resultadosApi, upload } from "../services/api"
import type { Prova, Resultado } from "../types"

type Aba = "provas" | "upload" | "resultados"
const ALTERNATIVAS = ["A", "B", "C", "D", "E"] as const

export default function ProfessorDashboard() {
    const [listaProvas, setListaProvas] = useState<Prova[]>([])
    const [listaResultados, setListaResultados] = useState<Resultado[]>([])
    const [aba, setAba] = useState<Aba>("provas")
    const [carregando, setCarregando] = useState<boolean>(true)

    // Formulário nova prova
    const [titulo, setTitulo] = useState<string>("")
    const [descricao, setDescricao] = useState<string>("")
    const [totalQuestoes, setTotalQuestoes] = useState<number>(5)
    const [gabarito, setGabarito] = useState<Record<string, string>>({})
    const [mensagem, setMensagem] = useState<string>("")

    // Upload
    const [provaSelecionada, setProvaSelecionada] = useState<string>("")
    const [arquivo, setArquivo] = useState<File | null>(null)
    const [resultadoUpload, setResultadoUpload] = useState<Resultado | null>(null)
    const [erroUpload, setErroUpload] = useState<string>("")

    useEffect(() => {
        Promise.all([provasApi.listar(), resultadosApi.listar()])
            .then(([p, r]) => { setListaProvas(p); setListaResultados(r) })
            .finally(() => setCarregando(false))
    }, [])

    function handleGabaritoChange(numero: number, letra: string): void {
        setGabarito(prev => ({ ...prev, [String(numero)]: letra }))
    }

    async function handleCriarProva(e: FormEvent<HTMLFormElement>): Promise<void> {
        e.preventDefault()
        setMensagem("")
        try {
            const nova = await provasApi.criar({ titulo, descricao, total_questoes: totalQuestoes, gabarito })
            setListaProvas(prev => [...prev, nova])
            setMensagem("✅ Prova criada com sucesso!")
            setTitulo(""); setDescricao(""); setGabarito({}); setTotalQuestoes(5)
        } catch (err) {
            setMensagem(`❌ ${err instanceof Error ? err.message : "Erro"}`)
        }
    }

    async function handleUpload(e: FormEvent<HTMLFormElement>): Promise<void> {
        e.preventDefault()
        setErroUpload(""); setResultadoUpload(null)
        if (!arquivo || !provaSelecionada) return
        try {
            const res = await upload.processarGabarito(Number(provaSelecionada), arquivo)
            setResultadoUpload(res)
            setListaResultados(await resultadosApi.listar())
        } catch (err) {
            setErroUpload(err instanceof Error ? err.message : "Erro no upload")
        }
    }

    if (carregando) return <div className="p-8 text-center">Carregando...</div>

    return (
        <div className="min-h-screen bg-gray-100">
            <Header />
            <main className="max-w-5xl mx-auto p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">Dashboard do Professor</h2>

                {/* Abas */}
                <div className="flex gap-2 mb-6">
                    {(["provas", "upload", "resultados"] as Aba[]).map(a => (
                        <button key={a} onClick={() => setAba(a)}
                            className={`px-4 py-2 rounded-lg font-medium transition ${
                                aba === a ? "bg-blue-700 text-white" : "bg-white text-gray-600 hover:bg-gray-50"
                            }`}>
                            {a === "provas" ? "📝 Provas" : a === "upload" ? "📷 Corrigir" : "📊 Resultados"}
                        </button>
                    ))}
                </div>

                {/* Criar Prova */}
                {aba === "provas" && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-white rounded-2xl shadow p-6">
                            <h3 className="text-lg font-semibold text-gray-700 mb-4">Nova Prova</h3>
                            <form onSubmit={handleCriarProva} className="space-y-4">
                                <input className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Título" value={titulo} onChange={e => setTitulo(e.target.value)} required />
                                <input className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Descrição (opcional)" value={descricao} onChange={e => setDescricao(e.target.value)} />

                                <div>
                                    <label className="text-sm text-gray-600">Número de questões</label>
                                    <input type="number" min={1} max={50}
                                        className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        value={totalQuestoes}
                                        onChange={e => { setTotalQuestoes(Number(e.target.value)); setGabarito({}) }} />
                                </div>

                                <div>
                                    <p className="text-sm text-gray-600 mb-2">Gabarito</p>
                                    <div className="space-y-1 max-h-60 overflow-y-auto pr-1">
                                        {Array.from({ length: totalQuestoes }, (_, i) => i + 1).map(n => (
                                            <div key={n} className="flex items-center gap-2">
                                                <span className="text-sm w-6 text-right text-gray-500">{n}.</span>
                                                {ALTERNATIVAS.map(letra => (
                                                    <button key={letra} type="button"
                                                        onClick={() => handleGabaritoChange(n, letra)}
                                                        className={`w-8 h-8 text-xs rounded-full font-bold border transition ${
                                                            gabarito[String(n)] === letra
                                                                ? "bg-blue-700 text-white border-blue-700"
                                                                : "border-gray-300 text-gray-600 hover:border-blue-400"
                                                        }`}>
                                                        {letra}
                                                    </button>
                                                ))}
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {mensagem && (
                                    <p className={`text-sm ${mensagem.startsWith("✅") ? "text-green-600" : "text-red-600"}`}>
                                        {mensagem}
                                    </p>
                                )}

                                <button type="submit"
                                    className="w-full bg-blue-700 text-white py-2 rounded-lg font-semibold hover:bg-blue-800 transition">
                                    Criar Prova
                                </button>
                            </form>
                        </div>

                        <div className="bg-white rounded-2xl shadow p-6">
                            <h3 className="text-lg font-semibold text-gray-700 mb-4">Provas Cadastradas</h3>
                            {listaProvas.length === 0
                                ? <p className="text-gray-400 text-sm">Nenhuma prova cadastrada.</p>
                                : <ul className="space-y-3">
                                    {listaProvas.map(p => (
                                        <li key={p.id} className="border rounded-lg px-4 py-3">
                                            <p className="font-medium text-gray-800">{p.titulo}</p>
                                            <p className="text-xs text-gray-500 mt-1">{p.total_questoes} questões · ID: {p.id}</p>
                                        </li>
                                    ))}
                                </ul>
                            }
                        </div>
                    </div>
                )}

                {/* Upload */}
                {aba === "upload" && (
                    <div className="bg-white rounded-2xl shadow p-6 max-w-lg">
                        <h3 className="text-lg font-semibold text-gray-700 mb-4">Corrigir Gabarito</h3>
                        <form onSubmit={handleUpload} className="space-y-4">
                            <div>
                                <label className="text-sm text-gray-600">Selecione a prova</label>
                                <select className="w-full border rounded-lg px-3 py-2 text-sm mt-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    value={provaSelecionada} onChange={e => setProvaSelecionada(e.target.value)} required>
                                    <option value="">-- selecione --</option>
                                    {listaProvas.map(p => <option key={p.id} value={p.id}>{p.titulo}</option>)}
                                </select>
                            </div>

                            <div>
                                <label className="text-sm text-gray-600">Foto do gabarito</label>
                                <input type="file" accept=".jpg,.jpeg,.png" className="w-full text-sm mt-1"
                                    onChange={(e: ChangeEvent<HTMLInputElement>) => setArquivo(e.target.files?.[0] ?? null)} required />
                            </div>

                            {erroUpload && (
                                <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2">
                                    ❌ {erroUpload}
                                </div>
                            )}

                            {resultadoUpload && (
                                <div className="bg-green-50 border border-green-200 text-green-700 text-sm rounded-lg px-4 py-3">
                                    <p className="font-semibold">✅ Corrigido com sucesso!</p>
                                    <p>Nota: <strong>{resultadoUpload.nota}</strong></p>
                                    <p>Acertos: {resultadoUpload.total_acertos}</p>
                                </div>
                            )}

                            <button type="submit"
                                className="w-full bg-blue-700 text-white py-2 rounded-lg font-semibold hover:bg-blue-800 transition">
                                Processar Gabarito
                            </button>
                        </form>
                    </div>
                )}

                {/* Resultados */}
                {aba === "resultados" && (
                    <div className="bg-white rounded-2xl shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-700 mb-4">Todos os Resultados</h3>
                        {listaResultados.length === 0
                            ? <p className="text-gray-400 text-sm">Nenhum resultado ainda.</p>
                            : <table className="w-full text-sm">
                                <thead>
                                    <tr className="text-left text-gray-500 border-b">
                                        <th className="pb-2">ID</th>
                                        <th className="pb-2">Aluno</th>
                                        <th className="pb-2">Prova</th>
                                        <th className="pb-2">Acertos</th>
                                        <th className="pb-2">Nota</th>
                                        <th className="pb-2">Editado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {listaResultados.map(r => (
                                        <tr key={r.id} className="border-b last:border-0">
                                            <td className="py-2 text-gray-400">#{r.id}</td>
                                            <td className="py-2">Aluno {r.aluno_id}</td>
                                            <td className="py-2">Prova {r.prova_id}</td>
                                            <td className="py-2">{r.total_acertos}</td>
                                            <td className="py-2 font-bold text-blue-700">{r.nota}</td>
                                            <td className="py-2">
                                                {r.editado_professor
                                                    ? <span className="text-orange-500">Sim</span>
                                                    : <span className="text-gray-400">Não</span>}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        }
                    </div>
                )}
            </main>
        </div>
    )
}