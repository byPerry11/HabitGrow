from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer, UserSerializer
from .forms import RegistroUsuarioForm
from habitgrow.permissions import IsOwner


class ProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Profile.
    
    Los usuarios pueden ver y actualizar su propio perfil (foto, etc).
    El XP y nivel se gestionan automáticamente.
    
    Endpoints:
    - GET /api/v1/profile/me/ - Perfil del usuario autenticado
    - PATCH /api/v1/profile/{id}/ - Actualizar perfil (ej. foto)
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """
        Filtra para que cada usuario solo vea su propio perfil.
        """
        return Profile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Endpoint personalizado para obtener y actualizar el perfil del usuario autenticado.
        
        GET /api/v1/profile/me/ - Obtener perfil
        PATCH /api/v1/profile/me/ - Actualizar perfil (ej. subir foto)
        """
        try:
            profile = request.user.profile
            
            if request.method == 'PATCH':
                # Actualizar perfil (ej. imagen de perfil)
                serializer = self.get_serializer(profile, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                # Sincronizar username si viene en la petición
                new_username = request.data.get('username')
                if new_username and new_username != request.user.username:
                    try:
                        request.user.username = new_username
                        request.user.save()
                    except Exception as e:
                        # Si hay colisión u otro error, omitir o manejar log
                        pass
                
                # Volver a serializar para incluir el username actualizado
                serializer = self.get_serializer(profile)
                return Response(serializer.data)
            
            # GET: retornar perfil
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Perfil no encontrado. Contacta al administrador.'},
                status=status.HTTP_404_NOT_FOUND
            )


class RegistroUsuarioView(CreateView):
    """
    Vista genérica para el registro de nuevos usuarios.
    
    Utiliza CreateView con el ModelForm RegistroUsuarioForm.
    Al completar el registro exitosamente:
    - Se crea el User
    - Se crea automáticamente el Profile mediante signals
    - Se crea automáticamente la Mascota mediante signals
    
    URL: /users/registro/
    Template: users/registro.html
    """
    form_class = RegistroUsuarioForm
    template_name = 'users/registro.html'
    success_url = reverse_lazy('users:registro')
    
    def form_valid(self, form):
        """
        Se ejecuta cuando el formulario es válido.
        Guarda el usuario y muestra mensaje de éxito.
        """
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(
            self.request,
            f'¡Bienvenido {username}! Tu cuenta ha sido creada exitosamente. '
            f'Tu mascota virtual está lista para comenzar.'
        )
        return response
    
    def form_invalid(self, form):
        """
        Se ejecuta cuando el formulario tiene errores.
        Muestra mensaje de error.
        """
        messages.error(
            self.request,
            'Por favor corrige los errores en el formulario.'
        )
        return super().form_invalid(form)
