import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habitgrow.settings')
django.setup()

from django.contrib.auth.models import User
from pets.models import Mascota
import traceback

try:
    user = User.objects.last()
    Mascota.objects.create(user=user, nombre='PlantaTest', especie='gizzmo')
    print("Mascota created successfully!")
except Exception as e:
    traceback.print_exc()
