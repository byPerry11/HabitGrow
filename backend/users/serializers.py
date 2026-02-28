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
            'fecha_creacion',
            'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'user', 'coins', 'fecha_creacion', 'fecha_actualizacion']
    
    def to_representation(self, instance):
        """
        Personalizar la respuesta para incluir información útil.
        """
        data = super().to_representation(instance)
        return data
