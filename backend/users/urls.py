from django.urls import path
from .views import RegistroUsuarioView

app_name = 'users'

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
]
