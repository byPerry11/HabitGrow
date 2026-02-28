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
    filterset_fields = ['activo', 'categoria']
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
    
    def create(self, request, *args, **kwargs):
        """
        Crea un hábito y retorna la representación completa.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Usar el serializer completo para la respuesta
        headers = self.get_success_headers(serializer.data)
        
        # Re-serializamos con el serializer de lectura para incluir campos calculados
        instance = serializer.instance
        read_serializer = HabitSerializer(instance, context={'request': request})
        
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
    
    @action(detail=True, methods=['post'])
    def toggle_completado_hoy(self, request, pk=None):
        """
        Marca/desmarca el hábito como completado hoy.
        
        POST /api/v1/habits/{id}/toggle_completado_hoy/
        """
        habit = self.get_object()
        today = timezone.now().date()
        
        # Buscar si ya existe un log para hoy
        log = habit.logs.filter(fecha_cumplimiento=today).first()
        
        if log:
            # BLOQUEO: Si ya está cumplido, no permitir cambios/reinicio
            if log.estado == HabitLog.ESTADO_CUMPLIDO:
                return Response(
                    {'error': 'Este hábito ya se completó hoy y no se puede reiniciar.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Si existe con pasos, incrementamos
            # Si ya está completado (pasos >= total), reiniciamos/borramos (toggle off logic)
            # Ciclo: 0 -> 1 -> 2 ... -> Total -> 0
            
            log.pasos_completados += 1
            
            if log.pasos_completados > habit.total_pasos:
                # Excedió el total, borramos el log (reset a 0)
                log.delete()
                completado = False
                mensaje = "Progreso reiniciado."
            else:
                # Actualizamos estado
                if log.pasos_completados >= habit.total_pasos:
                    log.estado = HabitLog.ESTADO_CUMPLIDO
                    mensaje = "¡Hábito completado por hoy!"
                    completado = True
                else:
                    log.estado = HabitLog.ESTADO_NO_CUMPLIDO
                    mensaje = f"Paso {log.pasos_completados}/{habit.total_pasos} completado."
                    completado = False
                log.save()
                
        else:
            # Si no existe, lo creamos con 1 paso
            pasos = 1
            estado = HabitLog.ESTADO_CUMPLIDO if pasos >= habit.total_pasos else HabitLog.ESTADO_NO_CUMPLIDO
            
            HabitLog.objects.create(
                habit=habit,
                fecha_cumplimiento=today,
                pasos_completados=pasos,
                estado=estado
            )
            
            if estado == HabitLog.ESTADO_CUMPLIDO:
                mensaje = "¡Hábito completado por hoy!"
                completado = True
            else:
                mensaje = f"Paso {pasos}/{habit.total_pasos} completado."
                completado = False
        
        # Recargar el hábito para obtener datos actualizados (racha, etc)
        # Forzamos la actualización de los campos calculados
        habit.refresh_from_db()
        serializer = self.get_serializer(habit)
        
        return Response({
            'mensaje': mensaje,
            'completado_hoy': completado,
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
    
    @action(detail=False, methods=['get'])
    def heatmap(self, request):
        """
        Retorna la cantidad de hábitos completados por día en el último año.
        Formato para gráfico de calor (similar a GitHub).
        
        GET /api/v1/habit-logs/heatmap/
        """
        from django.db.models import Count
        from django.db.models.functions import TruncDate
        
        # Último año (o rango deseado)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=365)
        
        # Query: Agrupar por fecha y contar logs cumplidos
        # Solo logs cumplidos
        queryset = self.get_queryset().filter(
            fecha_cumplimiento__gte=start_date,
            fecha_cumplimiento__lte=end_date,
            estado=HabitLog.ESTADO_CUMPLIDO
        ).values('fecha_cumplimiento').annotate(
            count=Count('id')
        )
        
        # Transformar a diccionario { "YYYY-MM-DD": count }
        data = {}
        for item in queryset:
            date_str = item['fecha_cumplimiento'].isoformat()
            data[date_str] = item['count']
            
        return Response(data)
