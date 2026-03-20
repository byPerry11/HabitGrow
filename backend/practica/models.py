from django.db import models

class UnidadInfo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Unidad de Información"
        verbose_name_plural = "Unidades de Información"

    def __str__(self):
        return self.nombre
