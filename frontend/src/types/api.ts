// Tipos base
export type EstadoHabit = 'cumplido' | 'no_cumplido' | 'parcial'
export type FrecuenciaHabit = 'diaria' | 'semanal' | 'mensual' | 'personalizada'
export type EstadoSalud = 'optimo' | 'regular' | 'mal' | 'marchito'

// User y Profile
export interface User {
    id: number
    username: string
    email: string
}

export interface Profile {
    id: number
    username: string
    total_xp: number
    nivel: number
    accesorios_equipados: Record<string, unknown>
    xp_para_siguiente_nivel: number
    progreso_nivel: number
}

// Mascota
export interface Mascota {
    id: number
    nombre: string
    puntos_vida: number
    estado_salud: EstadoSalud
    estado_salud_display: string
    nivel_evolucion: number
    emoji: string
    color: string
    porcentaje_salud: number
}

// Habit
export interface Habit {
    id: number
    nombre: string
    descripcion: string
    frecuencia: FrecuenciaHabit
    meta_semanal: number
    activo: boolean
    racha_actual: number
    total_completados: number
    fecha_creacion: string
}

// HabitLog
export interface HabitLog {
    id: number
    habit: number
    habit_nombre: string
    fecha_cumplimiento: string
    estado: EstadoHabit
    estado_display: string
    notas: string
}

// Dashboard
export interface DashboardData {
    user: User
    profile: Profile
    mascota: Mascota
    habits: Habit[]
    recent_logs: HabitLog[]
    stats: {
        total_habits: number
        habits_activos: number
        habits_cumplidos_hoy: number
        racha_maxima: number
        dias_consecutivos: number
    }
}

// Tipos para crear nuevo HabitLog
export type CreateHabitLog = Omit<HabitLog, 'id' | 'habit_nombre' | 'estado_display'>

// Tipos para crear nuevo Habit
export type CreateHabit = Omit<Habit, 'id' | 'racha_actual' | 'total_completados' | 'fecha_creacion'>
