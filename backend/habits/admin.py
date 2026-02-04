from django.contrib import admin
from .models import Habit, HabitLog


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Habit.
    """
    list_display = ('nombre', 'user', 'frecuencia', 'activo', 'total_completados', 'racha_actual', 'fecha_creacion')
    list_filter = ('frecuencia', 'activo', 'fecha_creacion')
    search_fields = ('nombre', 'user__username', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'nombre', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('frecuencia', 'meta_semanal', 'activo')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def total_completados(self, obj):
        """Muestra el total de veces completado."""
        return obj.get_total_completados()
    total_completados.short_description = 'Total Completados'
    
    def racha_actual(self, obj):
        """Muestra la racha actual."""
        racha = obj.get_racha_actual()
        if racha >= 7:
            return f"🔥 {racha} días"
        elif racha >= 3:
            return f"⭐ {racha} días"
        else:
            return f"{racha} días"
    racha_actual.short_description = 'Racha'


@admin.register(HabitLog)
class HabitLogAdmin(admin.ModelAdmin):
    """
    Configuración del admin para HabitLog.
    """
    list_display = ('habit', 'fecha_cumplimiento', 'estado', 'fecha_registro')
    list_filter = ('estado', 'fecha_cumplimiento', 'fecha_registro')
    search_fields = ('habit__nombre', 'habit__user__username', 'notas')
    readonly_fields = ('fecha_registro',)
    date_hierarchy = 'fecha_cumplimiento'
    
    fieldsets = (
        ('Información', {
            'fields': ('habit', 'fecha_cumplimiento', 'estado')
        }),
        ('Detalles', {
            'fields': ('notas',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_registro',),
            'classes': ('collapse',)
        }),
    )
