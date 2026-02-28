import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'habitgrow.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from habits.models import Habit
from users.models import Profile
from django.conf import settings

def run_verification():
    # Patch ALLOWED_HOSTS for APIClient
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ['testserver']

    print("--- Starting Dashboard API Verification ---")
    
    User = get_user_model()
    
    # 1. Get or Create User
    username = "testuser_dashboard"
    password = "testpassword123"
    email = "test@dashboard.com"
    user, created = User.objects.get_or_create(username=username, email=email)
    if created:
        user.set_password(password)
        user.save()
        Profile.objects.get_or_create(user=user)
        print(f"Created test user: {username}")
    else:
        print(f"Using existing test user: {username}")

    # 2. API Client
    client = APIClient()
    client.force_authenticate(user=user)

    # 3. Test Profile API (Coins)
    print("\n[TEST] Profile API (Coins Field)")
    response = client.get('/api/v1/profile/me/')
    if response.status_code == 200:
        data = response.json()
        if 'coins' in data:
            print(f"PASS: Coins field present. Value: {data['coins']}")
        else:
            print("FAIL: Coins field missing in response")
            print(f"Response keys: {list(data.keys())}")
    else:
        print(f"FAIL: Profile API returned {response.status_code}")

    # 4. Test Habits API (Create & List)
    print("\n[TEST] Habits API (Create, List, Fields)")
    # Create
    habit_data = {
        "nombre": "Test Habit Desktop",
        "descripcion": "Testing dashboard refactor",
        "frecuencia": "diaria",
        "categoria": "salud"
    }
    response = client.post('/api/v1/habits/', habit_data)
    if response.status_code == 201:
        habit_id = response.json()['id']
        print(f"PASS: Created habit with ID {habit_id}")
    else:
        print(f"FAIL: Could not create habit. Status: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response content: {response.content}")
        habit_id = None

    # List
    response = client.get('/api/v1/habits/')
    if response.status_code == 200:
        data = response.json()
        # Handle pagination
        if 'results' in data:
            results = data['results']
        else:
            results = data
            
        if len(results) > 0:
            first_habit = results[0]
            # Check fields
            if 'completado_hoy' in first_habit:
                print(f"PASS: 'completado_hoy' field present: {first_habit['completado_hoy']}")
            else:
                print("FAIL: 'completado_hoy' field missing")
            
            if 'categoria' in first_habit:
                print(f"PASS: 'categoria' field present: {first_habit['categoria']}")
            else:
                print("FAIL: 'categoria' field missing")
        else:
             print("WARN: No habits found (even after creation?)")
    else:
        print(f"FAIL: List Habits API returned {response.status_code}")

    # 5. Test Toggle Endpoint
    print("\n[TEST] Toggle Habit Endpoint")
    if habit_id:
        url = f'/api/v1/habits/{habit_id}/toggle_completado_hoy/'
        
        # Toggle ON
        response = client.post(url)
        if response.status_code == 200:
            res_json = response.json()
            print(f"PASS: Toggle request successful.")
            print(f" - Message: {res_json.get('mensaje')}")
            print(f" - Completed Today: {res_json.get('completado_hoy')}")
            
            if not res_json.get('completado_hoy'):
                print("FAIL: Expected 'completado_hoy' to be True after first toggle")
        else:
             print(f"FAIL: Toggle endpoint returned {response.status_code}")
             print(response.content)
        
        # Toggle OFF
        response = client.post(url)
        if response.status_code == 200:
             res_json = response.json()
             print(f"PASS: Toggled OFF successfully.")
             print(f" - Completed Today: {res_json.get('completado_hoy')}")
             if res_json.get('completado_hoy'):
                print("FAIL: Expected 'completado_hoy' to be False after second toggle")
        else:
             print(f"FAIL: Toggle OFF returned {response.status_code}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    run_verification()
