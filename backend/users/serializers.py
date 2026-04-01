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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Profile.
    Incluye información del usuario relacionado.
    """
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'username',
            'email',
            'coins',
            'accesorios_equipados',
            'profile_picture',
            'google_avatar',
            'is_onboarded',
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'user', 'coins', 'fecha_creacion', 'fecha_actualizacion']
    
    def to_representation(self, instance):
        """
        Personalizar la respuesta para incluir información útil y fallback de avatar.
        """
        data = super().to_representation(instance)
        
        # Fallback para profile_picture: Si no tiene, usar google_avatar
        if not data.get('profile_picture') and instance.google_avatar:
            data['profile_picture'] = instance.google_avatar
            
        return data
