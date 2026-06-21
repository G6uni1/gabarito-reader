import { Navigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import LoadingSpinner from "./LoadingSpinner"
import type { Perfil } from "../types"
import type { ReactNode } from "react"

interface ProtectedRouteProps {
    children: ReactNode
    perfil?: Perfil
}

export default function ProtectedRoute({ children, perfil }: ProtectedRouteProps) {
    const { usuario, carregando } = useAuth()

    if (carregando) return <LoadingSpinner />
    if (!usuario) return <Navigate to="/login" replace />
    if (perfil && usuario.perfil !== perfil) return <Navigate to="/login" replace />

    return <>{children}</>
}