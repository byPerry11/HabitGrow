from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import UnidadInfo

class UnidadInfoResource(resources.ModelResource):
    class Meta:
        model = UnidadInfo
        # fields = ('id', 'nombre', 'valor')  # Ejemplo de cómo restringir qué campos exportar

class UnidadInfoAdmin(ImportExportModelAdmin):
    resource_class = UnidadInfoResource
    list_display = ('id', 'nombre', 'valor', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')

admin.site.register(UnidadInfo, UnidadInfoAdmin)
