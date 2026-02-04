from rest_framework import serializers
from .models import Mascota


class MascotaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Mascota.
    Incluye información calculada sobre el estado.
    """
    estado_salud_display = serializers.CharField(source='get_estado_salud_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    # Campos visuales para el frontend
    emoji = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    porcentaje_salud = serializers.SerializerMethodField()
    
    class Meta:
        model = Mascota
        fields = [
            'id',
            'user',
            'username',
            'nombre',
            'fecha_creacion',
            'puntos_vida',
            'estado_salud',
            'estado_salud_display',
            'nivel_evolucion',
            'ultimo_chequeo',
            'emoji',
            'color',
            'porcentaje_salud'
        ]
        read_only_fields = [
            'id',
            'user',
            'puntos_vida',
            'estado_salud',
            'nivel_evolucion',
            'ultimo_chequeo',
            'fecha_creacion'
        ]
    
    def get_emoji(self, obj):
        """Retorna el emoji correspondiente al estado de salud."""
        emojis = {
            'optimo': '🌱',
            'regular': '🍃',
            'mal': '🥀',
            'marchito': '💀'
        }
        return emojis.get(obj.estado_salud, '🌱')
    
    def get_color(self, obj):
        """Retorna el color hex correspondiente al estado de salud."""
        colors = {
            'optimo': '#4ade80',    # Verde
            'regular': '#fbbf24',   # Amarillo
            'mal': '#f97316',       # Naranja
            'marchito': '#ef4444'   # Rojo
        }
        return colors.get(obj.estado_salud, '#4ade80')
    
    def get_porcentaje_salud(self, obj):
        """Retorna el porcentaje de salud (0-100)."""
        return obj.puntos_vida


class HealthUpdateSerializer(serializers.Serializer):
    """
    Serializer para la respuesta del método update_health().
    """
    dias_sin_actividad = serializers.IntegerField()
    deterioro_aplicado = serializers.IntegerField()
    puntos_vida_actuales = serializers.IntegerField()
    estado_salud = serializers.CharField()
    mensaje = serializers.CharField()
