import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { DashboardData } from '@/types/api'

export function useDashboard() {
    return useQuery({
        queryKey: ['dashboard'],
        queryFn: async () => {
            const { data } = await apiClient.get<DashboardData>('/dashboard/me/')
            return data
        },
        refetchInterval: 60000, // Actualizar cada minuto
        staleTime: 30000, // Considerar fresco por 30s
    })
}
