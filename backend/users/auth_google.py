"""
Vista para autenticación con Google OAuth2.

Flujo:
1. El frontend recibe el id_token de Google (JWT).
2. Lo envía a este endpoint via POST.
3. Verificamos el token con las claves públicas de Google.
4. Buscamos / vinculamos / creamos el usuario según la lógica:
   - Si el google_id ya existe en Profile → login directo.
   - Si el email ya existe en User pero sin google_id → vinculamos.
   - Si nada coincide → creamos nuevo User + Profile.
5. Devolvemos el Token de DRF igual que el login clásico.
"""

import re
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .serializers import UserSerializer

GOOGLE_CLIENT_ID = getattr(settings, 'GOOGLE_CLIENT_ID', '')


class GoogleLoginAPIView(APIView):
    """
    Endpoint: POST /users/api/google-auth/

    Body: { "id_token": "<JWT de Google>" }

    Returns: { "token": "<DRF token>", "user": {...}, "created": bool }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        credential = request.data.get('id_token')

        if not credential:
            return Response(
                {'error': 'Se requiere el campo id_token.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1) Verificar el token contra los servidores de Google
        try:
            idinfo = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                GOOGLE_CLIENT_ID
            )
        except ValueError as e:
            return Response(
                {'error': f'Token de Google inválido: {str(e)}'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Extraer datos del token verificado
        google_user_id = idinfo['sub']
        email = idinfo.get('email', '').lower()
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        google_avatar = idinfo.get('picture', '')
        email_verified = idinfo.get('email_verified', False)

        if not email_verified:
            return Response(
                {'error': 'El email de Google no está verificado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = False

        # 2) Buscar por google_id (usuario ya vinculó antes)
        try:
            profile = User.objects.get(profile__google_id=google_user_id).profile
            user = profile.user

        except User.DoesNotExist:
            # 3) Buscar por email (cuenta existente → vincular)
            try:
                user = User.objects.get(email=email)
                profile = user.profile
                profile.google_id = google_user_id
                if google_avatar and not profile.profile_picture:
                    profile.google_avatar = google_avatar
                profile.save()

            except User.DoesNotExist:
                # 4) Nuevo usuario → crear desde cero
                created = True
                username = self._generate_username(email, first_name)
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=User.objects.make_random_password()
                )
                profile = user.profile
                profile.google_id = google_user_id
                profile.google_avatar = google_avatar
                profile.save()

        # Sincronizar nombre si cambió en Google
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # 5) Token DRF
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'created': created,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def _generate_username(self, email: str, first_name: str) -> str:
        """Genera username único a partir del email."""
        base = re.sub(r'[^a-zA-Z0-9]', '', email.split('@')[0]) or 'usuario'
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        return username
