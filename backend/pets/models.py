from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Mascota(models.Model):
    """
    Mascota virtual (planta) del usuario.
    Refleja el estado de constancia del usuario mediante su salud.
    """
    
    ESTADO_OPTIMO = 'optimo'
    ESTADO_REGULAR = 'regular'
    ESTADO_MAL = 'mal'
    ESTADO_MARCHITO = 'marchito'
    
    ESTADOS_SALUD = [
        (ESTADO_OPTIMO, 'Óptimo'),
        (ESTADO_REGULAR, 'Regular'),
        (ESTADO_MAL, 'Mal'),
        (ESTADO_MARCHITO, 'Marchito'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mascota',
        verbose_name='Usuario'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Sobrenombre de la Mascota',
        help_text='Nombre personalizado que le das a tu planta'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    puntos_vida = models.IntegerField(
        default=100,
        verbose_name='Puntos de Vida',
        help_text='0-100, refleja la salud de la planta'
    )
    estado_salud = models.CharField(
        max_length=20,
        choices=ESTADOS_SALUD,
        default=ESTADO_OPTIMO,
        verbose_name='Estado de Salud'
    )
    nivel_evolucion = models.IntegerField(
        default=1,
        verbose_name='Nivel de Evolución',
        help_text='Etapa visual de crecimiento de la planta'
    )
    ultimo_chequeo = models.DateTimeField(
        auto_now=True,
        verbose_name='Último Chequeo',
        help_text='Última vez que se actualizó la salud'
    )
    
    class Meta:
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'
        ordering = ['-puntos_vida']
    
    def __str__(self):
        return f"{self.nombre} de {self.user.username} - {self.get_estado_salud_display()} ({self.puntos_vida}/100)"
    
    def update_health(self) -> dict:
        """
        Calcula y actualiza el deterioro de la mascota basado en:
        - Tiempo transcurrido desde el último HabitLog exitoso del usuario
        - No castiga fallos aislados, solo abandono prolongado (3+ días sin actividad)
        
        Returns:
            dict: Información sobre el deterioro aplicado
        """
        from habits.models import HabitLog
        
        # Obtener el último HabitLog completado del usuario
        ultimo_log = HabitLog.objects.filter(
            habit__user=self.user,
            estado=HabitLog.ESTADO_CUMPLIDO
        ).order_by('-fecha_cumplimiento').first()
        
        if not ultimo_log:
            # Si no hay logs, verificar días desde creación
            dias_sin_actividad = (timezone.now() - self.fecha_creacion).days
        else:
            # Calcular días desde último hábito cumplido
            dias_sin_actividad = (timezone.now().date() - ultimo_log.fecha_cumplimiento).days
        
        # LÓGICA DE DETERIORO GRADUAL
        deterioro = 0
        mensaje = ""
        
        if dias_sin_actividad == 0:
            # Actividad hoy - sin deterioro
            mensaje = "¡Planta feliz! Actividad reciente."
        elif dias_sin_actividad <= 2:
            # 1-2 días - deterioro mínimo (tolerancia)
            deterioro = 0
            mensaje = f"Planta estable. {dias_sin_actividad} día(s) sin actividad."
        elif dias_sin_actividad <= 5:
            # 3-5 días - deterioro moderado
            deterioro = 10 * (dias_sin_actividad - 2)  # -10, -20, -30
            mensaje = f"⚠️ Planta necesita atención. {dias_sin_actividad} días sin actividad."
        elif dias_sin_actividad <= 10:
            # 6-10 días - deterioro severo
            deterioro = 15 * (dias_sin_actividad - 2)  # -40, -55, -70...
            mensaje = f"🚨 Planta en riesgo. {dias_sin_actividad} días sin actividad."
        else:
            # 10+ días - deterioro crítico
            deterioro = 100  # Marchitamiento completo
            mensaje = f"💀 Abandono prolongado. {dias_sin_actividad} días sin actividad."
        
        # Aplicar deterioro
        self.puntos_vida = max(0, self.puntos_vida - deterioro)
        
        # Actualizar estado de salud basado en puntos_vida
        self._update_estado_salud()
        
        # Actualizar nivel de evolución
        self._update_nivel_evolucion()
        
        self.save()
        
        return {
            'dias_sin_actividad': dias_sin_actividad,
            'deterioro_aplicado': deterioro,
            'puntos_vida_actuales': self.puntos_vida,
            'estado_salud': self.get_estado_salud_display(),
            'mensaje': mensaje
        }
    
    def _update_estado_salud(self) -> None:
        """
        Actualiza el estado de salud según los puntos de vida.
        
        Rangos:
        - 80-100: Óptimo
        - 50-79: Regular
        - 20-49: Mal
        - 0-19: Marchito
        """
        if self.puntos_vida >= 80:
            self.estado_salud = self.ESTADO_OPTIMO
        elif self.puntos_vida >= 50:
            self.estado_salud = self.ESTADO_REGULAR
        elif self.puntos_vida >= 20:
            self.estado_salud = self.ESTADO_MAL
        else:
            self.estado_salud = self.ESTADO_MARCHITO
    
    def _update_nivel_evolucion(self) -> None:
        """
        Actualiza el nivel de evolución visual basado en el nivel del usuario.
        
        Niveles:
        - 1-5: Semilla/Brote (nivel 1)
        - 6-15: Planta Joven (nivel 2)
        - 16-30: Planta Madura (nivel 3)
        - 31-50: Planta Floreciente (nivel 4)
        - 51+: Árbol Majestuoso (nivel 5)
        """
        nivel_usuario = self.user.profile.nivel
        
        if nivel_usuario <= 5:
            self.nivel_evolucion = 1
        elif nivel_usuario <= 15:
            self.nivel_evolucion = 2
        elif nivel_usuario <= 30:
            self.nivel_evolucion = 3
        elif nivel_usuario <= 50:
            self.nivel_evolucion = 4
        else:
            self.nivel_evolucion = 5
    
    def heal(self, amount: int) -> None:
        """
        Cura la mascota (se llama al completar hábitos).
        
        Args:
            amount: Cantidad de puntos de vida a restaurar
        """
        self.puntos_vida = min(100, self.puntos_vida + amount)
        self._update_estado_salud()
        self.save()
    
    @property
    def emoji(self) -> str:
        """
        Devuelve el emoji de la mascota según su nivel de evolución.
        """
        emojis = {
            1: '🌱',  # Semilla/Brote
            2: '🌿',  # Planta Joven
            3: '🪴',  # Planta Madura
            4: '🌻',  # Planta Floreciente
            5: '🌳',  # Árbol Majestuoso
        }
        return emojis.get(self.nivel_evolucion, '🌱')
    
    @property
    def color(self) -> str:
        """
        Devuelve el color de la mascota según su estado de salud.
        Estos colores coinciden con la paleta Zen-Productivo del frontend.
        """
        colores = {
            self.ESTADO_OPTIMO: '#4ade80',      # verde brillante
            self.ESTADO_REGULAR: '#fbbf24',     # amarillo
            self.ESTADO_MAL: '#f97316',         # naranja
            self.ESTADO_MARCHITO: '#ef4444',    # rojo
        }
        return colores.get(self.estado_salud, '#4ade80')
    
    @property
    def porcentaje_salud(self) -> int:
        """
        Devuelve el porcentaje de salud (0-100).
        """
        return max(0, min(100, self.puntos_vida))
