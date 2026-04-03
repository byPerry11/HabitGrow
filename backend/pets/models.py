from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Mascota(models.Model):
    """
    Mascota virtual (planta) del usuario.
    Refleja el estado de constancia del usuario mediante su salud.
    """
    
    # Constantes para los diferentes estados de salud de la mascota
    ESTADO_OPTIMO = 'optimo'
    ESTADO_REGULAR = 'regular'
    ESTADO_MAL = 'mal'
    ESTADO_MARCHITO = 'marchito'
    
    # Opciones de estado para el campo choices
    ESTADOS_SALUD = [
        (ESTADO_OPTIMO, 'Óptimo'),
        (ESTADO_REGULAR, 'Regular'),
        (ESTADO_MAL, 'Mal'),
        (ESTADO_MARCHITO, 'Marchito'),
    ]
    
    # Especies disponibles
    ESPECIE_GIZZMO = 'gizzmo'
    ESPECIE_BULBASAUR = 'bulbasaur'
    ESPECIE_CHARMANDER = 'charmander'
    ESPECIE_GASTLY = 'gastly'

    ESPECIES_CHOICES = [
        (ESPECIE_GIZZMO, 'Gizzmo'),
        (ESPECIE_BULBASAUR, 'Bulbasaur'),
        (ESPECIE_CHARMANDER, 'Charmander'),
        (ESPECIE_GASTLY, 'Gastly'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mascota',
        verbose_name='Usuario'
    )
    especie = models.CharField(
        max_length=20,
        choices=ESPECIES_CHOICES,
        default=ESPECIE_GIZZMO,
        verbose_name='Especie'
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
    # Evolución visual (1-5 etapas según nivel)
    nivel_evolucion = models.IntegerField(
        default=1,
        verbose_name='Nivel de Evolución',
        help_text='Etapa visual de crecimiento de la planta'
    )
    # Sistema de XP y Nivel (refactorizado desde Profile)
    total_xp = models.IntegerField(
        default=0,
        verbose_name='Experiencia Total',
        help_text='Puntos de experiencia acumulados de la mascota'
    )
    nivel = models.IntegerField(
        default=1,
        verbose_name='Nivel',
        help_text='Nivel actual de la mascota'
    )
    ultimo_chequeo = models.DateTimeField(
        auto_now=True,
        verbose_name='Último Chequeo',
        help_text='Última vez que se actualizó la salud'
    )
    last_health_notified_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Notificación de Salud',
        help_text='Evita spam de notificaciones cuando la mascota está mal'
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
        
        # LÓGICA DE DETERIORO GRADUAL (Nuevos valores equilibrados)
        deterioro = 0
        mensaje = ""
        
        if dias_sin_actividad == 0:
            mensaje = "¡Tu mascota está feliz! Actividad detectada hoy."
        else:
            # 1. Decaimiento Base (2 HP por cada día de ausencia)
            deterioro += 2 * dias_sin_actividad
            
            # 2. Escalado por Negligencia
            if dias_sin_actividad <= 2:
                deterioro += 5 * dias_sin_actividad
                mensaje = f"Tu mascota te extraña. {dias_sin_actividad} día(s) sin actividad."
            elif dias_sin_actividad <= 5:
                # 2 días a 5 HP + días restantes a 15 HP
                deterioro += (5 * 2) + (15 * (dias_sin_actividad - 2))
                mensaje = f"⚠️ Tu compañero está debilitándose. {dias_sin_actividad} días sin actividad."
            else:
                # 2 días a 5 HP + 3 días a 15 HP + días restantes a 25 HP
                deterioro += (5 * 2) + (15 * 3) + (25 * (dias_sin_actividad - 5))
                mensaje = f"🚨 ESTADO CRÍTICO: Abandono prolongado ({dias_sin_actividad} días)."

        # Aplicar deterioro de Salud
        self.puntos_vida = max(0, self.puntos_vida - deterioro)
        
        # 3. Penalización de XP (Si la salud es Crítica < 20%)
        if self.puntos_vida < 20 and self.total_xp > 0:
            # Pierde 10 XP por día de abandono prolongado en estado crítico
            perdida_xp = 10 * max(1, dias_sin_actividad - 5)
            self.total_xp = max(0, self.total_xp - perdida_xp)
            mensaje += " Tu mascota pierde XP por desnutrición."

        # Actualizar estado de salud basado en puntos_vida
        self._update_estado_salud()
        
        # Actualizar nivel de evolución
        self._update_nivel_evolucion()
        
        self.save()
        
        
        # Enviar alerta si es necesario
        self._check_send_health_alert()
        
        return {
            'dias_sin_actividad': dias_sin_actividad,
            'deterioro_aplicado': deterioro,
            'puntos_vida_actuales': self.puntos_vida,
            'estado_salud': self.get_estado_salud_display(),
            'mensaje': mensaje
        }

    def _check_send_health_alert(self):
        """
        Envía una notificación si la mascota está descuidada (salud < 50%).
        Evita spam usando last_health_notified_at (mínimo 24h entre alertas).
        """
        from django.utils import timezone
        from datetime import timedelta
        try:
            from webpush import send_user_notification
        except ImportError:
            return

        if self.puntos_vida < 50:
            ahora = timezone.now()
            # Si no ha sido notificado hace más de 12 horas (más agresivo que 24h para salud)
            if not self.last_health_notified_at or (ahora - self.last_health_notified_at) > timedelta(hours=12):
                payload = {
                    'title': f'🐾 ¡{self.nombre} te necesita!',
                    'body': f'Tu mascota está en estado "{self.get_estado_salud_display()}". ¡Completa tus hábitos para animarla!',
                    'url': '/dashboard'
                }
                try:
                    send_user_notification(user=self.user, payload=payload, ttl=1000)
                    self.last_health_notified_at = ahora
                    self.save(update_fields=['last_health_notified_at'])
                except Exception as e:
                    print(f"Error enviando notificación de salud: {e}")
    
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
        Actualiza el nivel de evolución visual basado en el nivel de la mascota.
        
        Niveles:
        - 1-4: Bebé (nivel 1)
        - 5-15: Joven (nivel 2)
        - 16-30: Adulto (nivel 3)
        - 31-50: Maduro (nivel 4)
        - 51+: Legendario (nivel 5)
        """
        if self.nivel < 5:
            self.nivel_evolucion = 1
        elif self.nivel <= 15:
            self.nivel_evolucion = 2
        elif self.nivel <= 30:
            self.nivel_evolucion = 3
        elif self.nivel <= 50:
            self.nivel_evolucion = 4
        else:
            self.nivel_evolucion = 5
    
    # --- SISTEMA DE XP --- #
    def add_xp(self, amount: int) -> None:
        """
        Añade XP a la mascota y actualiza el nivel si es necesario.
        Se llama automáticamente al completar hábitos (+10 XP).
        
        Lógica de niveles:
        - Nivel 1: 0-99 XP
        - Nivel 2: 100-299 XP
        - Nivel 3: 300-599 XP
        - Nivel N: 100 * N + 50 * (N - 1) XP
        """
        self.total_xp += amount
        
        # Cálculo de nivel basado en XP
        # Fórmula: XP necesario = 100 * nivel + 50 * (nivel - 1)
        xp_for_next_level = 100 * self.nivel + 50 * (self.nivel - 1)
        
        # Subir de nivel si hay XP suficiente
        while self.total_xp >= xp_for_next_level and self.nivel < 100:
            self.nivel += 1
            xp_for_next_level = 100 * self.nivel + 50 * (self.nivel - 1)
        
        # Actualizar nivel de evolución visual basado en nuevo nivel
        self._update_nivel_evolucion()
        
        self.save()
    
    # --- SISTEMA DE CURACIÓN --- #
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
    
    # --- CÁLCULOS DE XP Y PROGRESO --- #
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
        Usado para la barra de XP en el frontend.
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
