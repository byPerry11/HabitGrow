import type { Mascota } from '@/types/api'
import clsx from 'clsx'

interface MascotaDisplayProps {
    mascota: Mascota
}

export function MascotaDisplay({ mascota }: MascotaDisplayProps) {
    return (
        <div className="flex flex-col items-center gap-6 p-8">
            {/* Emoji de la mascota - PROTAGONISTA VISUAL */}
            <div
                className="text-9xl transition-all duration-700 ease-smooth transform hover:scale-110"
                style={{
                    filter: `saturate(${Math.max(mascota.puntos_vida, 20)}%)`,
                    opacity: Math.max(mascota.puntos_vida / 100, 0.3),
                }}
            >
                {mascota.emoji}
            </div>

            {/* Nombre de la mascota */}
            <h2 className="text-3xl font-bold text-zen-earth">{mascota.nombre}</h2>

            {/* Barra de salud */}
            <div className="w-full max-w-sm">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span className="font-medium">{mascota.estado_salud_display}</span>
                    <span className="font-mono font-semibold">{mascota.puntos_vida}/100 HP</span>
                </div>

                {/* Contenedor de la barra */}
                <div className="h-4 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                    <div
                        className={clsx(
                            'h-full transition-all duration-700 ease-smooth rounded-full',
                            'shadow-md',
                            mascota.estado_salud === 'optimo' && 'bg-gradient-to-r from-mascota-optimo to-green-400',
                            mascota.estado_salud === 'regular' && 'bg-gradient-to-r from-mascota-regular to-yellow-400',
                            mascota.estado_salud === 'mal' && 'bg-gradient-to-r from-mascota-mal to-orange-500',
                            mascota.estado_salud === 'marchito' && 'bg-gradient-to-r from-mascota-marchito to-red-600'
                        )}
                        style={{ width: `${mascota.porcentaje_salud}%` }}
                    />
                </div>

                {/* Mensaje de estado */}
                <p className={clsx(
                    'mt-2 text-sm text-center font-medium transition-colors duration-400',
                    mascota.estado_salud === 'optimo' && 'text-mascota-optimo',
                    mascota.estado_salud === 'regular' && 'text-mascota-regular',
                    mascota.estado_salud === 'mal' && 'text-mascota-mal',
                    mascota.estado_salud === 'marchito' && 'text-mascota-marchito'
                )}>
                    {mascota.estado_salud === 'optimo' && '✨ ¡Tu planta está floreciendo!'}
                    {mascota.estado_salud === 'regular' && '💧 Tu planta necesita atención'}
                    {mascota.estado_salud === 'mal' && '⚠️ Tu planta está sufriendo'}
                    {mascota.estado_salud === 'marchito' && '😢 ¡Tu planta está marchita!'}
                </p>
            </div>
        </div>
    )
}
