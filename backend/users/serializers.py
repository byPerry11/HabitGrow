from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo User de Django.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Profile.
    Incluye información del usuario relacionado.
    """
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'username',
            'total_xp',
            'nivel',
            'accesorios_equipados',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'user', 'total_xp', 'nivel', 'fecha_creacion', 'fecha_actualizacion']
    
    def to_representation(self, instance):
        """
        Personalizar la respuesta para incluir información útil.
        """
        data = super().to_representation(instance)
        
        # Añadir XP necesario para próximo nivel
        xp_for_next_level = 100 * instance.nivel + 50 * (instance.nivel - 1)
        data['xp_para_siguiente_nivel'] = xp_for_next_level
        data['progreso_nivel'] = min(100, (instance.total_xp / xp_for_next_level) * 100)
        
        return data
