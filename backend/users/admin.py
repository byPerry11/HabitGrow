from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Profile.
    """
    list_display = ('user', 'nivel', 'total_xp', 'fecha_creacion')
    list_filter = ('nivel', 'fecha_creacion')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Progreso', {
            'fields': ('total_xp', 'nivel')
        }),
        ('Personalización', {
            'fields': ('accesorios_equipados',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
