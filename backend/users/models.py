from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Perfil extendido del usuario con sistema de XP y nivel.
    Se crea automáticamente al crear un User mediante signals.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario'
    )
    total_xp = models.IntegerField(
        default=0,
        verbose_name='Experiencia Total',
        help_text='Puntos de experiencia acumulados'
    )
    nivel = models.IntegerField(
        default=1,
        verbose_name='Nivel',
        help_text='Nivel actual del usuario'
    )
    coins = models.IntegerField(
        default=0,
        verbose_name='Monedas',
        help_text='Monedas virtuales para comprar accesorios'
    )
    accesorios_equipados = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Accesorios Equipados',
        help_text='Accesorios equipados en la mascota (JSON)'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        verbose_name='Foto de Perfil'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    last_daily_reward_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Última Recompensa Diaria',
        help_text='Fecha de la última vez que se otorgó la recompensa diaria de monedas'
    )

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['-total_xp']

    def __str__(self):
        return f"Perfil de {self.user.username} - Nivel {self.nivel} ({self.total_xp} XP)"

    def add_xp(self, amount: int) -> None:
        """
        Añade XP al perfil y actualiza el nivel si es necesario.
        
        Lógica de niveles:
        - Nivel 1: 0-99 XP
        - Nivel 2: 100-299 XP
        - Nivel 3: 300-599 XP
        - Nivel N: (N-1) * 100 + (N-1) * (N-2) * 50 XP
        """
        self.total_xp += amount
        
        # Cálculo de nivel basado en XP
        # Fórmula: XP necesario = 100 * nivel + 50 * (nivel - 1)
        xp_for_next_level = 100 * self.nivel + 50 * (self.nivel - 1)
        
        while self.total_xp >= xp_for_next_level and self.nivel < 100:
            self.nivel += 1
            xp_for_next_level = 100 * self.nivel + 50 * (self.nivel - 1)
        
        self.save()
    
    @property
    def xp_para_siguiente_nivel(self) -> int:
        """
        Calcula el XP total necesario para alcanzar el siguiente nivel.
        """
        return 100 * self.nivel + 50 * (self.nivel - 1)
    
    @property
    def progreso_nivel(self) -> float:
        """
        Calcula el progreso hacia el siguiente nivel como porcentaje (0-100).
        """
        if self.nivel == 1:
            xp_nivel_actual = 0
        else:
            xp_nivel_actual = 100 * (self.nivel - 1) + 50 * (self.nivel - 2)
        
        xp_necesario_para_nivel = self.xp_para_siguiente_nivel - xp_nivel_actual
        xp_progreso = self.total_xp - xp_nivel_actual
        
        if xp_necesario_para_nivel == 0:
            return 100.0
        
        progreso = (xp_progreso / xp_necesario_para_nivel) * 100
        return min(100.0, max(0.0, progreso))


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal para crear automáticamente un Profile al crear un User.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal para guardar el Profile al guardar un User.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
