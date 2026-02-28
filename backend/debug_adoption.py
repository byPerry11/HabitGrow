import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habitgrow.settings')
django.setup()

from django.contrib.auth.models import User
from pets.models import Mascota

def debug_adoption():
    # Usar el primer usuario para probar
    user = User.objects.first()
    if not user:
        print("No users found")
        return

    print(f"Testing adoption for user: {user.username}")
    
    # Check if has mascota
    if hasattr(user, 'mascota'):
        print(f"User already has mascota: {user.mascota.nombre}")
        # Delete it to test creation if needed, but let's just see if create fails
        # user.mascota.delete()
        # print("Deleted existing mascota to retry creation")
    
    try:
        nombre = "Debug Pet"
        especie = "gizzmo"
        print(f"Attempting to create Mascota: {nombre} ({especie})")
        mascota = Mascota.objects.create(
            user=user,
            nombre=nombre,
            especie=especie
        )
        print(f"Successfully created: {mascota.id}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_adoption()
