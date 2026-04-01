from rest_framework import serializers
from .models import Habit, HabitLog
from django.utils import timezone


class HabitSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Habit.
    Incluye estadísticas calculadas.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    # Estadísticas
    racha_actual = serializers.SerializerMethodField()
    total_completados = serializers.SerializerMethodField()
    completado_hoy = serializers.SerializerMethodField()
    pasos_completados_hoy = serializers.SerializerMethodField()
    
    class Meta:
        model = Habit
        fields = [
            'id',
            'user',
            'username',
            'nombre',
            'descripcion',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
            'racha_actual',
            'total_completados',
            'completado_hoy',
            'categoria',
            'dias_semana',
            'total_pasos',
            'pasos_completados_hoy',
            'notificaciones_activas',
            'hora_notificacion'
        ]
        read_only_fields = ['id', 'user', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_racha_actual(self, obj):
        """Obtiene la racha actual de días consecutivos."""
        return obj.get_racha_actual()
    
    def get_total_completados(self, obj):
        """Obtiene el total de veces completado."""
        return obj.get_total_completados()
    
    def get_completado_hoy(self, obj):
        """Verifica si el hábito se completó hoy."""
        return obj.logs.filter(
            fecha_cumplimiento=timezone.now().date(),
            estado=HabitLog.ESTADO_CUMPLIDO
        ).exists()

    def get_pasos_completados_hoy(self, obj):
        """Obtiene el número de pasos completados hoy."""
        log = obj.logs.filter(fecha_cumplimiento=timezone.now().date()).first()
        return log.pasos_completados if log else 0


class HabitCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para crear hábitos.
    """
    class Meta:
        model = Habit
        fields = ['id', 'nombre', 'descripcion', 'dias_semana', 'total_pasos', 'activo', 'categoria', 'notificaciones_activas', 'hora_notificacion']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """
        Asigna automáticamente el usuario autenticado.
        """
        user = self.context['request'].user
        return Habit.objects.create(user=user, **validated_data)


class HabitLogSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo HabitLog.
    """
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    habit_nombre = serializers.CharField(source='habit.nombre', read_only=True)
    
    class Meta:
        model = HabitLog
        fields = [
            'id',
            'habit',
            'habit_nombre',
            'fecha_cumplimiento',
            'estado',
            'estado_display',
            'pasos_completados',
            'notas',
            'fecha_registro'
        ]
        read_only_fields = ['id', 'fecha_registro']
    
    def validate(self, data):
        """
        Validaciones personalizadas.
        """
        # Verificar que el hábito pertenece al usuario autenticado
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            habit = data.get('habit')
            if habit and habit.user != request.user:
                raise serializers.ValidationError(
                    "No puedes crear logs para hábitos de otros usuarios."
                )
        
        # Verificar que la fecha no sea futura
        fecha_cumplimiento = data.get('fecha_cumplimiento')
        if fecha_cumplimiento and fecha_cumplimiento > timezone.now().date():
            raise serializers.ValidationError(
                "No puedes marcar un hábito como completado en el futuro."
            )
        
        return data


class HabitLogCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para crear logs de hábitos.
    """
    class Meta:
        model = HabitLog
        fields = ['habit', 'fecha_cumplimiento', 'estado', 'pasos_completados', 'notas']
    
    def validate(self, data):
        """
        Validaciones personalizadas.
        """
        # Verificar que el hábito pertenece al usuario autenticado
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            habit = data.get('habit')
            if habit and habit.user != request.user:
                raise serializers.ValidationError(
                    "No puedes crear logs para hábitos de otros usuarios."
                )
        
        # Verificar que la fecha no sea futura
        fecha_cumplimiento = data.get('fecha_cumplimiento')
        if fecha_cumplimiento and fecha_cumplimiento > timezone.now().date():
            raise serializers.ValidationError(
                "No puedes marcar un hábito como completado en el futuro."
            )
        
        return data


class HabitWithLogsSerializer(HabitSerializer):
    """
    Serializer de Habit que incluye los logs recientes.
    """
    logs_recientes = serializers.SerializerMethodField()
    
    class Meta(HabitSerializer.Meta):
        fields = HabitSerializer.Meta.fields + ['logs_recientes']
    
    def get_logs_recientes(self, obj):
        """
        Obtiene los últimos 7 logs del hábito.
        """
        logs = obj.logs.all().order_by('-fecha_cumplimiento')[:7]
        return HabitLogSerializer(logs, many=True).data
