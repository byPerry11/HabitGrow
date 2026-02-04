import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { Habit, HabitLog, CreateHabitLog } from '@/types/api'

// Hook para obtener todos los hábitos
export function useHabits() {
    return useQuery({
        queryKey: ['habits'],
        queryFn: async () => {
            const { data } = await apiClient.get<Habit[]>('/habits/')
            return data
        },
    })
}

// Hook para marcar un hábito como completado (con optimistic updates)
export function useCreateHabitLog() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: async (log: CreateHabitLog) => {
            const { data } = await apiClient.post<HabitLog>('/habit-logs/', log)
            return data
        },
        onSuccess: () => {
            // Invalidar queries para refetch automático
            queryClient.invalidateQueries({ queryKey: ['dashboard'] })
            queryClient.invalidateQueries({ queryKey: ['habits'] })
            queryClient.invalidateQueries({ queryKey: ['mascota'] })
        },
    })
}
