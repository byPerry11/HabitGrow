from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import Habit, HabitLog
from .serializers import (
    HabitSerializer,
    HabitCreateSerializer,
    HabitLogSerializer,
    HabitLogCreateSerializer,
    HabitWithLogsSerializer
)
from habitgrow.permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo CRUD para Habit.
    
    Permite crear, leer, actualizar y eliminar hábitos.
    Solo se puede acceder a los hábitos propios.
    
    Endpoints:
    - GET    /api/v1/habits/ - Lista de hábitos del usuario
    - POST   /api/v1/habits/ - Crear hábito
    - GET    /api/v1/habits/{id}/ - Detalle de hábito
    - PATCH  /api/v1/habits/{id}/ - Actualizar hábito
    - DELETE /api/v1/habits/{id}/ - Eliminar hábito
    - GET    /api/v1/habits/activos/ - Solo hábitos activos
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['frecuencia', 'activo']
    ordering_fields = ['fecha_creacion', 'nombre']
    ordering = ['-fecha_creacion']
    
    def get_queryset(self):
        """
        Filtra para que cada usuario solo vea sus propios hábitos.
        """
        return Habit.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Usa diferentes serializers según la acción.
        """
        if self.action == 'create':
            return HabitCreateSerializer
        elif self.action == 'retrieve':
            return HabitWithLogsSerializer
        return HabitSerializer
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Retorna solo los hábitos activos.
        
        GET /api/v1/habits/activos/
        """
        queryset = self.get_queryset().filter(activo=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_activo(self, request, pk=None):
        """
        Activa/desactiva un hábito.
        
        POST /api/v1/habits/{id}/toggle_activo/
        """
        habit = self.get_object()
        habit.activo = not habit.activo
        habit.save()
        
        serializer = self.get_serializer(habit)
        return Response({
            'mensaje': f'Hábito {"activado" if habit.activo else "desactivado"}.',
            'habit': serializer.data
        })


class HabitLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo CRUD para HabitLog.
    
    Permite registrar, ver, actualizar y eliminar registros de hábitos.
    
    Endpoints:
    - GET    /api/v1/habit-logs/ - Lista de logs del usuario
    - POST   /api/v1/habit-logs/ - Crear log (marcar hábito)
    - GET    /api/v1/habit-logs/{id}/ - Detalle de log
    - PATCH  /api/v1/habit-logs/{id}/ - Actualizar log
    - DELETE /api/v1/habit-logs/{id}/ - Eliminar log
    - GET    /api/v1/habit-logs/today/ - Logs de hoy
    - GET    /api/v1/habit-logs/week/ - Logs de esta semana
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'fecha_cumplimiento', 'habit']
    ordering_fields = ['fecha_cumplimiento', 'fecha_registro']
    ordering = ['-fecha_cumplimiento']
    
    def get_queryset(self):
        """
        Filtra para que cada usuario solo vea logs de sus propios hábitos.
        """
        return HabitLog.objects.filter(habit__user=self.request.user)
    
    def get_serializer_class(self):
        """
        Usa diferentes serializers según la acción.
        """
        if self.action == 'create':
            return HabitLogCreateSerializer
        return HabitLogSerializer
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Retorna los logs de hoy.
        
        GET /api/v1/habit-logs/today/
        """
        today = timezone.now().date()
        queryset = self.get_queryset().filter(fecha_cumplimiento=today)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def week(self, request):
        """
        Retorna los logs de esta semana.
        
        GET /api/v1/habit-logs/week/
        """
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        queryset = self.get_queryset().filter(
            fecha_cumplimiento__gte=start_of_week,
            fecha_cumplimiento__lte=end_of_week
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'semana': {
                'inicio': start_of_week,
                'fin': end_of_week
            },
            'total_logs': queryset.count(),
            'logs': serializer.data
        })
