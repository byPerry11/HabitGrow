from django.urls import path
from .views import RegistroUsuarioView
from .api_views import RegisterAPIView, LoginAPIView

app_name = 'users'

urlpatterns = [
    # Template View
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    
    # API endpoints
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
]
