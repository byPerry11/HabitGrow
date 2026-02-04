"""
Script de prueba para verificar el frontend de HabitGrow.
Crea datos de prueba y verifica la integración con la API.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habitgrow.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import Profile
from pets.models import Mascota
from habits.models import Habit, HabitLog
from datetime import datetime, timedelta
from django.utils import timezone

def create_test_data():
    """Crea o actualiza datos de prueba para el frontend."""
    
    print("🌱 Creando datos de prueba para HabitGrow...")
    
    # 1. Crear o obtener usuario de prueba
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@habitgrow.com',
            'is_staff': True,
            'is_superuser': False,
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Usuario creado: {user.username}")
    else:
        print(f"♻️  Usuario existente: {user.username}")
    
    # 2. Verificar Profile
    try:
        profile = user.profile
        print(f"♻️  Profile existente - Nivel: {profile.nivel}, XP: {profile.total_xp}")
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
        print("✅ Profile creado")
    
    # 3. Crear o actualizar Mascota
    mascota, mascota_created = Mascota.objects.get_or_create(
        user=user,
        defaults={
            'nombre': 'Plantita',
            'puntos_vida': 85,
            'estado_salud': Mascota.ESTADO_OPTIMO,
        }
    )
    
    if not mascota_created:
        # Actualizar mascota existente a un estado saludable
        mascota.puntos_vida = 85
        mascota.estado_salud = Mascota.ESTADO_OPTIMO
        mascota._update_nivel_evolucion()
        mascota.save()
        print(f"♻️  Mascota actualizada: {mascota.nombre} - {mascota.puntos_vida}/100 HP")
    else:
        print(f"✅ Mascota creada: {mascota.nombre}")
    
    # 4. Crear hábitos de ejemplo
    habitos_ejemplo = [
        {
            'nombre': '💧 Tomar agua',
            'descripcion': 'Beber 2 litros de agua al día',
            'frecuencia': Habit.FRECUENCIA_DIARIA,
            'meta_semanal': 7,
        },
        {
            'nombre': '🏃 Ejercicio matutino',
            'descripcion': '30 minutos de ejercicio por la mañana',
            'frecuencia': Habit.FRECUENCIA_DIARIA,
            'meta_semanal': 5,
        },
        {
            'nombre': '📚 Leer 30min',
            'descripcion': 'Leer al menos 30 minutos antes de dormir',
            'frecuencia': Habit.FRECUENCIA_DIARIA,
            'meta_semanal': 6,
        },
        {
            'nombre': '🧘 Meditación',
            'descripcion': '10 minutos de meditación guiada',
            'frecuencia': Habit.FRECUENCIA_DIARIA,
            'meta_semanal': 7,
        },
        {
            'nombre': '🎨 Práctica creativa',
            'descripcion': 'Dibujar, escribir o crear algo',
            'frecuencia': Habit.FRECUENCIA_SEMANAL,
            'meta_semanal': 3,
        },
    ]
    
    habits_created = []
    for habit_data in habitos_ejemplo:
        habit, created = Habit.objects.get_or_create(
            user=user,
            nombre=habit_data['nombre'],
            defaults=habit_data
        )
        if created:
            print(f"✅ Hábito creado: {habit.nombre}")
        habits_created.append(habit)
    
    # 5. Crear logs de hábitos (últimos 7 días)
    print("\n📊 Creando logs de hábitos...")
    
    # Eliminar logs antiguos de prueba
    HabitLog.objects.filter(habit__user=user).delete()
    
    log_count = 0
    for i in range(7):
        fecha = timezone.now().date() - timedelta(days=i)
        
        # Los primeros 3 hábitos se completan casi todos los días
        for habit in habits_created[:3]:
            if i < 5 or (i == 5 and habit != habits_created[2]):  # Simular que faltó 1 día
                HabitLog.objects.create(
                    habit=habit,
                    fecha_cumplimiento=fecha,
                    estado=HabitLog.ESTADO_CUMPLIDO,
                    notas=f"Completado el día {fecha}"
                )
                log_count += 1
        
        # El 4to hábito solo 4 días
        if i < 4:
            HabitLog.objects.create(
                habit=habits_created[3],
                fecha_cumplimiento=fecha,
                estado=HabitLog.ESTADO_CUMPLIDO,
            )
            log_count += 1
    
    print(f"✅ {log_count} logs de hábitos creados")
    
    # 6. Actualizar XP del usuario basado en logs
    total_logs = HabitLog.objects.filter(
        habit__user=user,
        estado=HabitLog.ESTADO_CUMPLIDO
    ).count()
    
    profile.total_xp = total_logs * 10  # 10 XP por hábito completado
    profile.save()
    
    # Actualizar nivel de forma manual
    if profile.total_xp >= 500:
        profile.nivel = 6
    elif profile.total_xp >= 300:
        profile.nivel = 5
    elif profile.total_xp >= 150:
        profile.nivel = 4
    elif profile.total_xp >= 75:
        profile.nivel = 3
    elif profile.total_xp >= 30:
        profile.nivel = 2
    else:
        profile.nivel = 1
    
    profile.save()
    
    # Actualizar nivel de evolución de mascota
    mascota._update_nivel_evolucion()
    mascota.save()
    
    print(f"\n✅ Profile actualizado - Nivel: {profile.nivel}, XP: {profile.total_xp}")
    print(f"✅ Mascota - Nivel evolución: {mascota.nivel_evolucion}")
    
    return {
        'user': user,
        'profile': profile,
        'mascota': mascota,
        'habits': habits_created,
        'logs_count': log_count
    }

def print_summary(data):
    """Imprime un resumen de los datos creados."""
    print("\n" + "="*60)
    print("📋 RESUMEN DE DATOS DE PRUEBA")
    print("="*60)
    print(f"\n👤 Usuario: {data['user'].username}")
    print(f"   Email: {data['user'].email}")
    print(f"   Nivel: {data['profile'].nivel}")
    print(f"   Total XP: {data['profile'].total_xp}")
    print(f"   XP para siguiente nivel: {data['profile'].xp_para_siguiente_nivel}")
    print(f"   Progreso: {data['profile'].progreso_nivel}%")
    
    print(f"\n🌱 Mascota: {data['mascota'].nombre}")
    print(f"   HP: {data['mascota'].puntos_vida}/100")
    print(f"   Estado: {data['mascota'].get_estado_salud_display()}")
    print(f"   Nivel evolución: {data['mascota'].nivel_evolucion}")
    print(f"   Emoji: {data['mascota'].emoji}")
    
    print(f"\n📝 Hábitos activos: {len(data['habits'])}")
    for habit in data['habits']:
        logs_count = HabitLog.objects.filter(
            habit=habit,
            estado=HabitLog.ESTADO_CUMPLIDO
        ).count()
        print(f"   • {habit.nombre} - Completado {logs_count} veces")
    
    print(f"\n📊 Total logs registrados: {data['logs_count']}")
    
    print("\n" + "="*60)
    print("✅ DATOS LISTOS PARA PRUEBAS")
    print("="*60)
    print("\n🌐 Accede a:")
    print("   Backend API: http://localhost:8000/api/v1/dashboard/me/")
    print("   Django Admin: http://localhost:8000/admin/")
    print("   Frontend: http://localhost:5173/")
    print(f"\n🔑 Credenciales:")
    print(f"   Usuario: {data['user'].username}")
    print("   Password: testpass123")
    print("\n")

if __name__ == '__main__':
    try:
        data = create_test_data()
        print_summary(data)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
