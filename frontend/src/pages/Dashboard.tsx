import { useDashboard } from '@/hooks/useDashboard'
import { MascotaDisplay } from '@/components/mascota/MascotaDisplay'
import { Card } from '@/components/ui/Card'

export function DashboardPage() {
    const { data, isLoading, error } = useDashboard()

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-zen-cream">
                <div className="text-center">
                    <div className="text-6xl mb-4 animate-pulse">🌱</div>
                    <p className="text-zen-earth font-medium">Cargando tu jardín...</p>
                </div>
            </div>
        )
    }

    if (error || !data) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-zen-cream">
                <Card className="p-8 max-w-md text-center">
                    <div className="text-6xl mb-4">🥀</div>
                    <h2 className="text-2xl font-bold text-zen-earth mb-2">
                        No se pudo conectar
                    </h2>
                    <p className="text-gray-600 text-sm mb-4">
                        Asegúrate de estar autenticado en Django admin:
                    </p>
                    <a
                        href="http://localhost:8000/admin"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block px-4 py-2 bg-zen-green text-white rounded-lg hover:bg-green-500 transition-colors duration-400"
                    >
                        Ir a Django Admin
                    </a>
                </Card>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-zen-cream p-6">
            <div className="max-w-6xl mx-auto space-y-6">
                {/* Header */}
                <header className="flex justify-between items-center">
                    <div>
                        <h1 className="text-4xl font-bold text-zen-earth">HabitGrow</h1>
                        <p className="text-sm text-gray-600 mt-1">
                            Hola, <span className="font-semibold">{data.user.username}</span> 👋
                        </p>
                    </div>
                    <div className="flex items-center gap-6 bg-white px-6 py-3 rounded-xl shadow-sm">
                        <div className="text-center">
                            <p className="text-xs text-gray-500 uppercase tracking-wide">Nivel</p>
                            <p className="text-2xl font-bold text-zen-green">{data.profile.nivel}</p>
                        </div>
                        <div className="h-10 w-px bg-gray-200" />
                        <div className="text-center">
                            <p className="text-xs text-gray-500 uppercase tracking-wide">XP</p>
                            <p className="text-2xl font-bold text-zen-green">{data.profile.total_xp}</p>
                        </div>
                    </div>
                </header>

                {/* Barra de progreso de XP */}
                <Card className="p-4">
                    <div className="flex items-center gap-4">
                        <span className="text-sm font-medium text-gray-600">
                            Nivel {data.profile.nivel}
                        </span>
                        <div className="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-zen-green to-green-400 transition-all duration-700 ease-smooth rounded-full"
                                style={{ width: `${data.profile.progreso_nivel}%` }}
                            />
                        </div>
                        <span className="text-sm text-gray-600">
                            {data.profile.total_xp} / {data.profile.xp_para_siguiente_nivel} XP
                        </span>
                    </div>
                </Card>

                {/* Mascota - PROTAGONISTA */}
                <Card className="shadow-lg">
                    <MascotaDisplay mascota={data.mascota} />
                </Card>

                {/* Estadísticas rápidas */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="p-6 hover:shadow-lg transition-shadow duration-400">
                        <div className="flex items-center gap-4">
                            <div className="text-4xl">✅</div>
                            <div>
                                <p className="text-sm text-gray-600">Cumplidos hoy</p>
                                <p className="text-3xl font-bold text-zen-green">
                                    {data.stats.habits_cumplidos_hoy}
                                </p>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6 hover:shadow-lg transition-shadow duration-400">
                        <div className="flex items-center gap-4">
                            <div className="text-4xl">🔥</div>
                            <div>
                                <p className="text-sm text-gray-600">Racha máxima</p>
                                <p className="text-3xl font-bold text-zen-green">
                                    {data.stats.racha_maxima} días
                                </p>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6 hover:shadow-lg transition-shadow duration-400">
                        <div className="flex items-center gap-4">
                            <div className="text-4xl">📋</div>
                            <div>
                                <p className="text-sm text-gray-600">Total hábitos</p>
                                <p className="text-3xl font-bold text-zen-green">
                                    {data.stats.total_habits}
                                </p>
                            </div>
                        </div>
                    </Card>
                </div>

                {/* Lista de hábitos - Placeholder */}
                <Card className="p-6">
                    <h2 className="text-2xl font-bold text-zen-earth mb-4">Mis Hábitos</h2>

                    {data.habits.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4">🌱</div>
                            <p className="text-gray-600 mb-4">
                                Aún no tienes hábitos. ¡Crea tu primer hábito para empezar!
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {data.habits.slice(0, 5).map((habit) => (
                                <div
                                    key={habit.id}
                                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-400"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-3 h-3 rounded-full ${habit.activo ? 'bg-zen-green' : 'bg-gray-400'}`} />
                                        <div>
                                            <p className="font-semibold text-zen-earth">{habit.nombre}</p>
                                            <p className="text-sm text-gray-600">
                                                {habit.descripcion}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-semibold text-zen-green">
                                            {habit.racha_actual} días
                                        </p>
                                        <p className="text-xs text-gray-500">
                                            {habit.total_completados} completados
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </Card>
            </div>
        </div>
    )
}
