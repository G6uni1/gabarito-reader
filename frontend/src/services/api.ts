import type {
    Usuario,
    Prova,
    Resultado,
    ResultadoDetalhe,
    TokenResponse,
    LoginRequest,
    ProvaCreate,
} from "../types"

const BASE_URL = "http://localhost:8000/api/v1"

// ─── Auxiliar tipado ─────────────────────────────────────────────────────────

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem("token")

    const headers: HeadersInit = {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
    }

    const resposta = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers })

    if (resposta.status === 401) {
        localStorage.removeItem("token")
        window.location.href = "/login"
        throw new Error("Sessão expirada")
    }

    const dados = await resposta.json()

    if (!resposta.ok) {
        throw new Error(dados.detail || "Erro na requisição")
    }

    return dados as T
}

// ─── Auth ────────────────────────────────────────────────────────────────────

export const auth = {
    login: (email: string, senha: string): Promise<TokenResponse> =>
        request<TokenResponse>("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, senha } satisfies LoginRequest),
        }),

    me: (): Promise<Usuario> =>
        request<Usuario>("/auth/me"),
}

// ─── Provas ──────────────────────────────────────────────────────────────────

export const provas = {
    listar: (): Promise<Prova[]> =>
        request<Prova[]>("/provas"),

    criar: (dados: ProvaCreate): Promise<Prova> =>
        request<Prova>("/provas", {
            method: "POST",
            body: JSON.stringify(dados),
        }),

    urlFolha: (provaId: number, alunoId: number): string =>
        `${BASE_URL}/provas/${provaId}/folha/${alunoId}`,
}

// ─── Resultados ──────────────────────────────────────────────────────────────

export const resultados = {
    listar: (): Promise<Resultado[]> =>
        request<Resultado[]>("/resultados"),

    detalhar: (id: number): Promise<ResultadoDetalhe> =>
        request<ResultadoDetalhe>(`/resultados/${id}`),

    editar: (id: number, dados: { nova_nota?: number; novas_respostas?: Record<string, string> }): Promise<Resultado> =>
        request<Resultado>(`/resultados/${id}`, {
            method: "PUT",
            body: JSON.stringify(dados),
        }),
}

// ─── Upload ──────────────────────────────────────────────────────────────────

export const upload = {
    processarGabarito: async (provaId: number, arquivo: File): Promise<Resultado> => {
        const token = localStorage.getItem("token")
        const formData = new FormData()
        formData.append("arquivo", arquivo)

        const resposta = await fetch(`${BASE_URL}/upload/gabarito/${provaId}`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token ?? ""}` },
            body: formData,
        })

        const dados = await resposta.json()
        if (!resposta.ok) throw new Error(dados.detail?.erro || "Erro no upload")
        return dados as Resultado
    },
}