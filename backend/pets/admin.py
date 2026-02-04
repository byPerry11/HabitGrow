from django.contrib import admin
from .models import Mascota


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Mascota.
    """
    list_display = ('nombre', 'user', 'estado_salud', 'puntos_vida', 'nivel_evolucion', 'ultimo_chequeo')
    list_filter = ('estado_salud', 'nivel_evolucion', 'fecha_creacion')
    search_fields = ('nombre', 'user__username')
    readonly_fields = ('fecha_creacion', 'ultimo_chequeo')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'nombre')
        }),
        ('Estado de Salud', {
            'fields': ('puntos_vida', 'estado_salud', 'nivel_evolucion')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'ultimo_chequeo'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['actualizar_salud', 'curar_mascota']
    
    def actualizar_salud(self, request, queryset):
        """
        Acción personalizada para actualizar la salud de las mascotas seleccionadas.
        """
        for mascota in queryset:
            info = mascota.update_health()
            self.message_user(
                request,
                f"{mascota.nombre}: {info['mensaje']} (Deterioro: {info['deterioro_aplicado']})"
            )
    actualizar_salud.short_description = "Actualizar salud de mascotas seleccionadas"
    
    def curar_mascota(self, request, queryset):
        """
        Acción personalizada para curar completamente las mascotas seleccionadas.
        """
        for mascota in queryset:
            mascota.heal(100)
            self.message_user(request, f"{mascota.nombre} ha sido curada completamente.")
    curar_mascota.short_description = "Curar mascotas seleccionadas"
