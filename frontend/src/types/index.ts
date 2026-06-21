// ─── Enums ───────────────────────────────────────────────────────────────────

export type Perfil = "aluno" | "professor" | "admin"

// ─── Entidades da API ────────────────────────────────────────────────────────

export interface Usuario {
    id: number
    nome: string
    email: string
    perfil: Perfil
    ativo: boolean
    criado_em: string
}

export interface Prova {
    id: number
    titulo: string
    descricao: string | null
    total_questoes: number
    professor_id: number
    criada_em: string
    ativa: boolean
}

export interface Resultado {
    id: number
    aluno_id: number
    prova_id: number
    nota: number
    total_acertos: number
    corrigido_em: string
    editado_professor: boolean
}

export interface ResultadoDetalhe extends Resultado {
    respostas_aluno: Record<string, string>
    acertos: string[]
    erros: string[]
}

// ─── Requests ────────────────────────────────────────────────────────────────

export interface LoginRequest {
    email: string
    senha: string
}

export interface TokenResponse {
    access_token: string
    token_type: string
    perfil: Perfil
    nome: string
}

export interface ProvaCreate {
    titulo: string
    descricao?: string
    total_questoes: number
    gabarito: Record<string, string>
}

// ─── Estado de formulário ────────────────────────────────────────────────────

export interface GabaritoForm {
    [questao: string]: string
}