"""
Chequeo rápido: Verifica que el usuario testuser pueda acceder al dashboard
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habitgrow.settings')
django.setup()

from django.contrib.auth.models import User

# Verificar que el usuario existe
try:
    user = User.objects.get(username='testuser')
    print(f"✅ Usuario encontrado: {user.username}")
    print(f"   Email: {user.email}")
    
    # Verificar Profile
    profile = user.profile
    print(f"\n👤 Perfil:")
    print(f"   Nivel: {profile.nivel}")
    print(f"   XP: {profile.total_xp}")
    print(f"   XP para siguiente nivel: {profile.xp_para_siguiente_nivel}")
    print(f"   Progreso: {profile.progreso_nivel:.1f}%")
    
    # Verificar Mascota
    mascota = user.mascota
    print(f"\n🌱 Mascota: {mascota.nombre}")
    print(f"   HP: {mascota.puntos_vida}/100")
    print(f"   Estado: {mascota.get_estado_salud_display()}")
    print(f"   Emoji: {mascota.emoji}")
    print(f"   Color: {mascota.color}")
    print(f"   Porcentaje salud: {mascota.porcentaje_salud}%")
    
    # Contar hábitos
    from habits.models import Habit, HabitLog
    habits = Habit.objects.filter(user=user, activo=True)
    logs = HabitLog.objects.filter(habit__user=user, estado=HabitLog.ESTADO_CUMPLIDO)
    
    print(f"\n📊 Estadísticas:")
    print(f"   Hábitos activos: {habits.count()}")
    print(f"   Completados (total): {logs.count()}")
    
    print("\n✅ ¡Todo listo para probar el frontend!")
    print("\n📝 Instrucciones de prueba:")
    print("1. Abre http://localhost:8000/admin/")
    print(f"2. Inicia sesión con: testuser / testpass123")
    print("3. Luego abre http://localhost:5173/ en otra pestaña")
    print("4. El frontend debe mostrar tu dashboard con todos los datos")
    
except User.DoesNotExist:
    print("❌ Error: Usuario testuser no existe")
    print("   Ejecuta: python test_frontend_data.py")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
