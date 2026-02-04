from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer, UserSerializer
from habitgrow.permissions import IsOwner


class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para Profile.
    
    Los usuarios solo pueden ver su propio perfil.
    El XP y nivel se actualizan automáticamente mediante signals.
    
    Endpoints:
    - GET /api/v1/profile/me/ - Perfil del usuario autenticado
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """
        Filtra para que cada usuario solo vea su propio perfil.
        """
        return Profile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Endpoint personalizado para obtener el perfil del usuario autenticado.
        
        GET /api/v1/profile/me/
        """
        try:
            profile = request.user.profile
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(
                {'error': 'Perfil no encontrado. Contacta al administrador.'},
                status=status.HTTP_404_NOT_FOUND
            )
