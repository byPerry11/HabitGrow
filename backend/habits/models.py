from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Habit(models.Model):
    """
    Hábito que el usuario desea rastrear.
    """
    
    # Constantes para las opciones de frecuencia del hábito
    FRECUENCIA_DIARIA = 'diaria'
    FRECUENCIA_SEMANAL = 'semanal'
    FRECUENCIA_PERSONALIZADA = 'personalizada'
    
    FRECUENCIAS = [
        (FRECUENCIA_DIARIA, 'Diaria'),
        (FRECUENCIA_SEMANAL, 'Semanal'),
        (FRECUENCIA_PERSONALIZADA, 'Personalizada'),
    ]

    # Constantes para las categorías de hábitos
    CATEGORIA_SALUD = 'salud'
    CATEGORIA_EJERCICIO = 'ejercicio'
    CATEGORIA_ESTUDIO = 'estudio'
    CATEGORIA_TRABAJO = 'trabajo'
    CATEGORIA_TAREA = 'tarea'
    CATEGORIA_ARTE = 'arte'

    CATEGORIAS = [
        (CATEGORIA_SALUD, 'Salud'),
        (CATEGORIA_EJERCICIO, 'Ejercicio'),
        (CATEGORIA_ESTUDIO, 'Estudio'),
        (CATEGORIA_TRABAJO, 'Trabajo'),
        (CATEGORIA_TAREA, 'Tarea'),
        (CATEGORIA_ARTE, 'Arte'),
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
    # Frecuencia ya no se usa como tal, se define por días de la semana
    # Mantener campo por compatibilidad o migrar? 
    # El plan decia reemplazar meta_semanal por dias especificos.
    # Vamos a mantener frecuencia como 'personalizada' por defecto o eliminarla si no es necesaria.
    # Pero el código existente la usa. Vamos a dejarla pero enfocar la lógica en dias_semana.
    
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
        default=CATEGORIA_SALUD,
        verbose_name='Categoría'
    )

    dias_semana = models.CharField(
        max_length=20,
        default='0,1,2,3,4,5,6',
        verbose_name='Días de la Semana',
        help_text='Índices de días separados por coma (0=Lunes, 6=Domingo)'
    )
    
    total_pasos = models.IntegerField(
        default=1,
        verbose_name='Total de Pasos',
        help_text='Número de pasos para completar el hábito (Checkpoints)'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si el hábito está activo o archivado'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Borrado',
        help_text='Indica si el hábito está en la papelera'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Eliminación'
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
            models.Index(fields=['user', 'activo', 'is_deleted']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.user.username})"
    
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
    
    # Constantes para el estado de cumplimiento del hábito
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
    pasos_completados = models.IntegerField(
        default=0,
        verbose_name='Pasos Completados'
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
    
    Al completar un hábito (estado=cumplido):
    1. Añade XP al perfil del usuario (+10 XP)
    2. Cura la mascota (+10 puntos de vida)
    3. Verifica si completó TODOS los hábitos del día:
       - Si sí, y no ha recibido recompensa hoy -> +20 Coins
    """
    if instance.estado != HabitLog.ESTADO_CUMPLIDO:
        return

    # Evitar duplicados en actualizaciones sucesivas si no cambió el estado
    # (Esto es una aproximación, lo ideal es verificar el estado anterior o usar un campo flag)
    # Por ahora confiamos en que la vista solo guarda cambios reales.

    user = instance.habit.user
    today = instance.fecha_cumplimiento # Usar fecha del log, no hoy real, para consistencia
    
    # --- RECOMPENSAS POR HÁBITO COMPLETADO ---
    # 1. Añadir XP a la mascota
    if hasattr(user, 'mascota'):
        user.mascota.add_xp(15)  # +15 XP por cada hábito completado (+50% vs base original)
    
    # 2. Curar la mascota
    if hasattr(user, 'mascota'):
        user.mascota.heal(10)  # +10 HP por cada hábito completado
        # La mascota ya se actualiza y se guarda en heal() y add_xp()

    # 3. Verificar si completó TODOS los hábitos del día
    # Filtrar hábitos activos y programados para este día de la semana
    active_habits = Habit.objects.filter(user=user, activo=True)
    weekday = today.weekday() # 0 = Lunes, 6 = Domingo
    
    habits_today_ids = []
    
    for h in active_habits:
        try:
            # dias_semana es "0,1,2,3,4"
            days = [int(x) for x in h.dias_semana.split(',') if x.strip().isdigit()]
            if weekday in days:
                habits_today_ids.append(h.id)
        except ValueError:
            continue
            
    if not habits_today_ids:
        return

    # Verificar si todos estos hábitos tienen un log cumplido para esta fecha
    # Contamos cuántos de los hábitos de hoy tienen un log cumplido
    completed_count = HabitLog.objects.filter(
        habit_id__in=habits_today_ids,
        fecha_cumplimiento=today,
        estado=HabitLog.ESTADO_CUMPLIDO
    ).count()
    
    if completed_count >= len(habits_today_ids):
        # ¡Todo completado!
        # Verificar si ya se dio la recompensa para ESTA fecha
        # Usamos last_daily_reward_date. Si es diferente a 'today', damos premio.
        if hasattr(user, 'profile'):
            # Convertimos today a date si es datetime (aunque el modelo define datefield)
            if user.profile.last_daily_reward_date != today:
                user.profile.coins += 20
                user.profile.last_daily_reward_date = today
                user.profile.save()
