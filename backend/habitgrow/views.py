from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from users.models import Profile
from users.serializers import ProfileSerializer, UserSerializer
from pets.models import Mascota
from pets.serializers import MascotaSerializer
from habits.models import Habit, HabitLog
from habits.serializers import HabitWithLogsSerializer, HabitLogSerializer
from django.utils import timezone
from datetime import timedelta


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet personalizado para el Dashboard.
    
    Provee un endpoint único que retorna todos los datos necesarios
    para la vista principal del usuario.
    
    Endpoints:
    - GET /api/v1/dashboard/me/ - Datos completos del dashboard
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retorna todos los datos del dashboard del usuario autenticado.
        
        GET /api/v1/dashboard/me/
        
        Response:
        {
            "user": {...},
            "profile": {...},
            "mascota": {...},
            "habits": [...],
            "recent_logs": [...],
            "stats": {
                "total_habits": 5,
                "habits_activos": 3,
                "habits_cumplidos_hoy": 2,
                "racha_maxima": 10,
                "dias_consecutivos": 5
            }
        }
        """
        user = request.user
        
        # 1. Información del usuario
        user_data = UserSerializer(user).data
        
        # 2. Perfil con XP y nivel
        try:
            profile = user.profile
            profile_data = ProfileSerializer(profile).data
        except Profile.DoesNotExist:
            # Si no existe el perfil, crearlo
            profile = Profile.objects.create(user=user)
            profile_data = ProfileSerializer(profile).data
        
        # 3. Mascota
        try:
            mascota = user.mascota
            mascota_data = MascotaSerializer(mascota).data
        except Mascota.DoesNotExist:
            # Si no tiene mascota, retornar None
            mascota = None
            mascota_data = None
        
        # 4. Hábitos del usuario
        habits = Habit.objects.filter(user=user).order_by('-fecha_creacion')
        habits_data = HabitWithLogsSerializer(habits, many=True).data
        
        # 5. Logs recientes (últimos 7 días)
        fecha_inicio = timezone.now().date() - timedelta(days=7)
        recent_logs = HabitLog.objects.filter(
            habit__user=user,
            fecha_cumplimiento__gte=fecha_inicio
        ).order_by('-fecha_cumplimiento')[:20]
        recent_logs_data = HabitLogSerializer(recent_logs, many=True).data
        
        # 6. Estadísticas
        total_habits = habits.count()
        habits_activos = habits.filter(activo=True).count()
        
        # Hábitos cumplidos hoy
        today = timezone.now().date()
        habits_cumplidos_hoy = HabitLog.objects.filter(
            habit__user=user,
            fecha_cumplimiento=today,
            estado='cumplido'
        ).count()
        
        # Racha máxima de todos los hábitos
        racha_maxima = 0
        dias_consecutivos = 0
        for habit in habits:
            racha = habit.get_racha_actual()
            if racha > racha_maxima:
                racha_maxima = racha
            if racha > 0:
                dias_consecutivos = max(dias_consecutivos, racha)
        
        stats = {
            'total_habits': total_habits,
            'habits_activos': habits_activos,
            'habits_cumplidos_hoy': habits_cumplidos_hoy,
            'racha_maxima': racha_maxima,
            'dias_consecutivos': dias_consecutivos,
            'total_logs': recent_logs.count(),
        }
        
        return Response({
            'user': user_data,
            'profile': profile_data,
            'mascota': mascota_data,
            'habits': habits_data,
            'recent_logs': recent_logs_data,
            'stats': stats
        })
