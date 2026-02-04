from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Habit(models.Model):
    """
    Hábito que el usuario desea rastrear.
    """
    
    FRECUENCIA_DIARIA = 'diaria'
    FRECUENCIA_SEMANAL = 'semanal'
    FRECUENCIA_PERSONALIZADA = 'personalizada'
    
    FRECUENCIAS = [
        (FRECUENCIA_DIARIA, 'Diaria'),
        (FRECUENCIA_SEMANAL, 'Semanal'),
        (FRECUENCIA_PERSONALIZADA, 'Personalizada'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Usuario'
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del Hábito'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción opcional del hábito'
    )
    frecuencia = models.CharField(
        max_length=20,
        choices=FRECUENCIAS,
        default=FRECUENCIA_DIARIA,
        verbose_name='Frecuencia'
    )
    meta_semanal = models.IntegerField(
        default=7,
        verbose_name='Meta Semanal',
        help_text='Veces por semana que se debe completar'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si el hábito está activo o archivado'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Hábito'
        verbose_name_plural = 'Hábitos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['user', 'activo']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.user.username}) - {self.get_frecuencia_display()}"
    
    def get_racha_actual(self) -> int:
        """
        Calcula la racha actual de días consecutivos completados.
        
        Returns:
            int: Número de días consecutivos completados
        """
        from django.utils import timezone
        from datetime import timedelta
        
        logs = self.logs.filter(
            estado=HabitLog.ESTADO_CUMPLIDO
        ).order_by('-fecha_cumplimiento')
        
        if not logs.exists():
            return 0
        
        racha = 0
        fecha_actual = timezone.now().date()
        
        for log in logs:
            if log.fecha_cumplimiento == fecha_actual:
                racha += 1
                fecha_actual -= timedelta(days=1)
            elif log.fecha_cumplimiento < fecha_actual:
                break
        
        return racha
    
    def get_total_completados(self) -> int:
        """
        Retorna el total de veces que se ha completado este hábito.
        """
        return self.logs.filter(estado=HabitLog.ESTADO_CUMPLIDO).count()


class HabitLog(models.Model):
    """
    Registro de cumplimiento/no cumplimiento de un hábito.
    """
    
    ESTADO_CUMPLIDO = 'cumplido'
    ESTADO_NO_CUMPLIDO = 'no_cumplido'
    
    ESTADOS = [
        (ESTADO_CUMPLIDO, 'Cumplido'),
        (ESTADO_NO_CUMPLIDO, 'No Cumplido'),
    ]
    
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='Hábito'
    )
    fecha_cumplimiento = models.DateField(
        verbose_name='Fecha de Cumplimiento'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default=ESTADO_CUMPLIDO,
        verbose_name='Estado'
    )
    notas = models.TextField(
        blank=True,
        verbose_name='Notas',
        help_text='Notas opcionales sobre el cumplimiento'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    class Meta:
        verbose_name = 'Registro de Hábito'
        verbose_name_plural = 'Registros de Hábitos'
        ordering = ['-fecha_cumplimiento']
        unique_together = ['habit', 'fecha_cumplimiento']
        indexes = [
            models.Index(fields=['habit', 'fecha_cumplimiento']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.habit.nombre} - {self.fecha_cumplimiento} ({self.get_estado_display()})"


@receiver(post_save, sender=HabitLog)
def update_mascota_on_habit_completion(sender, instance, created, **kwargs):
    """
    Signal que se dispara al crear/actualizar un HabitLog.
    
    Al completar un hábito (created=True y estado=cumplido):
    1. Añade XP al perfil del usuario (+10 XP)
    2. Cura la mascota (+10 puntos de vida)
    3. Actualiza el último_chequeo de la mascota
    """
    if created and instance.estado == HabitLog.ESTADO_CUMPLIDO:
        user = instance.habit.user
        
        # 1. Añadir XP al perfil
        if hasattr(user, 'profile'):
            user.profile.add_xp(10)
        
        # 2. Curar la mascota
        if hasattr(user, 'mascota'):
            user.mascota.heal(10)
            
            # También actualizar nivel de evolución por si subió de nivel
            user.mascota._update_nivel_evolucion()
            user.mascota.save()
