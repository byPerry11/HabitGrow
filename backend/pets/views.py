from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Mascota
from .serializers import MascotaSerializer, HealthUpdateSerializer
from habitgrow.permissions import IsOwner


class MascotaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Mascota.
    
    Permite ver y actualizar el nombre (sobrenombre) de la mascota del usuario.
    Incluye acciones personalizadas para curar la mascota y actualizar su salud.
    
    Endpoints:
    - GET    /api/v1/mascota/ - Lista (solo la del usuario)
    - GET    /api/v1/mascota/me/ - Mascota del usuario autenticado
    - PATCH  /api/v1/mascota/{id}/ - Actualizar sobrenombre
    - POST   /api/v1/mascota/{id}/adoptar/ - Adoptar mascota (asignar nombre inicial)
    - POST   /api/v1/mascota/{id}/heal/ - Curar mascota (manual)
    - POST   /api/v1/mascota/{id}/update_health/ - Actualizar salud
    """
    serializer_class = MascotaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """
        Filtra para que cada usuario solo vea su propia mascota.
        """
        return Mascota.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Endpoint personalizado para obtener la mascota del usuario autenticado.
        
        GET /api/v1/mascota/me/
        """
        try:
            mascota = request.user.mascota
            serializer = self.get_serializer(mascota)
            return Response(serializer.data)
        except Mascota.DoesNotExist:
            return Response(
                {
                    'error': 'No tienes mascota aún.',
                    'mensaje': 'Adopta una mascota asignándole un sobrenombre.',
                    'code': 'needs_adoption'
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def adoptar(self, request):
        """
        Adopta una mascota asignándole un sobrenombre.
        
        POST /api/v1/mascota/adoptar/
        Body: { "nombre": "Plantita Feliz" }
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[ADOPTAR] Usuario {request.user.username} intentando adoptar mascota")
        logger.info(f"[ADOPTAR] Payload recibido: {request.data}")
        
        try:
            # Verificar que no tenga mascota ya
            if hasattr(request.user, 'mascota'):
                logger.warning(f"[ADOPTAR] Usuario {request.user.username} ya tiene mascota: {request.user.mascota.nombre}")
                return Response(
                    {
                        'error': 'Ya tienes una mascota.',
                        'mascota': self.get_serializer(request.user.mascota).data
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            nombre = request.data.get('nombre', '').strip()
            especie = request.data.get('especie', '').strip().lower()
            
            # Validar especie
            especies_validas = [choice[0] for choice in Mascota.ESPECIES_CHOICES]
            if especie and especie not in especies_validas:
                logger.warning(f"[ADOPTAR] Especie inválida: {especie}")
                return Response(
                    {'error': f'La especie "{especie}" no es válida.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not especie:
                especie = Mascota.ESPECIE_GIZZMO # Default
            
            if not nombre:
                logger.warning(f"[ADOPTAR] Nombre vacío proporcionado")
                return Response(
                    {'error': 'Debes proporcionar un nombre para tu mascota.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(nombre) > 100:
                logger.warning(f"[ADOPTAR] Nombre demasiado largo: {len(nombre)} caracteres")
                return Response(
                    {'error': 'El nombre no puede tener más de 100 caracteres.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear la mascota
            logger.info(f"[ADOPTAR] Creando mascota: {nombre} ({especie})")
            mascota = Mascota.objects.create(
                user=request.user,
                nombre=nombre,
                especie=especie
            )
            logger.info(f"[ADOPTAR] Mascota creada exitosamente: ID={mascota.id}")
            
            serializer = self.get_serializer(mascota)
            return Response(
                {
                    'mensaje': f'¡Felicidades! Has adoptado a {nombre} 🌱',
                    'mascota': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"[ADOPTAR] Error inesperado: {type(e).__name__}: {str(e)}")
            logger.exception("[ADOPTAR] Stack trace completo:")
            return Response(
                {
                    'error': 'Error interno del servidor al crear la mascota.',
                    'detalle': str(e) if request.user.is_staff else 'Contacta al administrador.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def heal(self, request, pk=None):
        """
        Cura la mascota manualmente (restaura puntos de vida).
        
        POST /api/v1/mascota/{id}/heal/
        Body: { "amount": 20 }  (opcional, default: 10)
        """
        mascota = self.get_object()
        amount = request.data.get('amount', 10)
        
        try:
            amount = int(amount)
            if amount <= 0 or amount > 100:
                return Response(
                    {'error': 'La cantidad debe estar entre 1 y 100.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'La cantidad debe ser un número entero.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        puntos_antes = mascota.puntos_vida
        mascota.heal(amount)
        puntos_despues = mascota.puntos_vida
        
        serializer = self.get_serializer(mascota)
        return Response({
            'mensaje': f'{mascota.nombre} ha sido curada. +{puntos_despues - puntos_antes} puntos de vida.',
            'puntos_antes': puntos_antes,
            'puntos_despues': puntos_despues,
            'mascota': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def update_health(self, request, pk=None):
        """
        Actualiza la salud de la mascota basándose en la actividad del usuario.
        
        POST /api/v1/mascota/{id}/update_health/
        """
        mascota = self.get_object()
        
        # Ejecutar lógica de deterioro
        info = mascota.update_health()
        
        # Personalizar mensaje con el nombre de la mascota
        mensaje_personalizado = info['mensaje'].replace('Planta', mascota.nombre)
        info['mensaje'] = mensaje_personalizado
        
        # Serializar respuesta
        health_serializer = HealthUpdateSerializer(data=info)
        health_serializer.is_valid(raise_exception=True)
        
        mascota_serializer = self.get_serializer(mascota)
        
        return Response({
            'info': health_serializer.data,
            'mascota': mascota_serializer.data
        })
