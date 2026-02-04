from rest_framework import serializers
from .models import Habit, HabitLog
from django.utils import timezone


class HabitSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Habit.
    Incluye estadísticas calculadas.
    """
    frecuencia_display = serializers.CharField(source='get_frecuencia_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    # Estadísticas
    racha_actual = serializers.SerializerMethodField()
    total_completados = serializers.SerializerMethodField()
    
    class Meta:
        model = Habit
        fields = [
            'id',
            'user',
            'username',
            'nombre',
            'descripcion',
            'frecuencia',
            'frecuencia_display',
            'meta_semanal',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
            'racha_actual',
            'total_completados'
        ]
        read_only_fields = ['id', 'user', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_racha_actual(self, obj):
        """Obtiene la racha actual de días consecutivos."""
        return obj.get_racha_actual()
    
    def get_total_completados(self, obj):
        """Obtiene el total de veces completado."""
        return obj.get_total_completados()


class HabitCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para crear hábitos.
    """
    class Meta:
        model = Habit
        fields = ['nombre', 'descripcion', 'frecuencia', 'meta_semanal', 'activo']
    
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
        fields = ['habit', 'fecha_cumplimiento', 'estado', 'notas']
    
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
