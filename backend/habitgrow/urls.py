from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# Importar ViewSets
from users.views import ProfileViewSet
from pets.views import MascotaViewSet
from habits.views import HabitViewSet, HabitLogViewSet
from habitgrow.views import DashboardViewSet

# Crear router
router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'mascota', MascotaViewSet, basename='mascota')
router.register(r'habits', HabitViewSet, basename='habit')
router.register(r'habit-logs', HabitLogViewSet, basename='habitlog')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include(router.urls)),
    
    # API Authentication (DRF browsable API login)
    path('api-auth/', include('rest_framework.urls')),
    
    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Users app (Formulario de registro tradicional)
    path('users/', include('users.urls')),
]
