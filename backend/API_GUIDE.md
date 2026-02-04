# HabitGrow API - Guía de Endpoints

## 🌐 URL Base

```
http://localhost:8000/api/v1/
```

## 🔐 Autenticación

La API usa **SessionAuthentication** de Django por defecto. Para probarla:

1. Inicia sesión en el admin: `http://localhost:8000/admin`
2. Accede a la Browsable API: `http://localhost:8000/api/v1/`

## 📊 Endpoints Disponibles

### **1. Dashboard** (Vista Completa)

#### GET /api/v1/dashboard/me/
Retorna todos los datos del usuario: perfil, mascota, hábitos, logs y estadísticas.

**Respuesta:**
```json
{
  "user": { "id": 1, "username": "byPerry11", "email": "..." },
  "profile": {
    "id": 1,
    "total_xp": 50,
    "nivel": 1,
    "xp_para_siguiente_nivel": 100,
    "progreso_nivel": 50.0
  },
  "mascota": {
    "nombre": "Mi Planta",
    "puntos_vida": 100,
    "estado_salud": "optimo",
    "emoji": "🌱",
    "color": "#4ade80"
  },
  "habits": [...],
  "recent_logs": [...],
  "stats": {
    "total_habits": 3,
    "habits_cumplidos_hoy": 2,
    "racha_maxima": 5
  }
}
```

---

### **2. Profile** (Perfil del Usuario)

#### GET /api/v1/profile/me/
Obtiene el perfil del usuario autenticado.

**Respuesta:**
```json
{
  "id": 1,
  "username": "byPerry11",
  "total_xp": 50,
  "nivel": 1,
  "accesorios_equipados": {},
  "xp_para_siguiente_nivel": 100,
  "progreso_nivel": 50.0
}
```

---

### **3. Mascota** (Planta Virtual)

#### GET /api/v1/mascota/me/
Obtiene la mascota del usuario autenticado.

**Respuesta:**
```json
{
  "id": 1,
  "nombre": "Mi Plantita",
  "puntos_vida": 85,
  "estado_salud": "optimo",
  "estado_salud_display": "Óptimo",
  "nivel_evolucion": 2,
  "emoji": "🌱",
  "color": "#4ade80",
  "porcentaje_salud": 85
}
```

#### PATCH /api/v1/mascota/{id}/
Actualiza el nombre de la mascota.

**Body:**
```json
{
  "nombre": "Plantita Feliz"
}
```

#### POST /api/v1/mascota/{id}/heal/
Cura la mascota manualmente (útil para pruebas o features premium).

**Body:**
```json
{
  "amount": 20
}
```

**Respuesta:**
```json
{
  "mensaje": "Mascota curada. +20 puntos de vida.",
  "puntos_antes": 70,
  "puntos_despues": 90,
  "mascota": { ... }
}
```

#### POST /api/v1/mascota/{id}/update_health/
Ejecuta la lógica de deterioro basada en la actividad del usuario.

**Respuesta:**
```json
{
  "info": {
    "dias_sin_actividad": 3,
    "deterioro_aplicado": 15,
    "puntos_vida_actuales": 85,
    "estado_salud": "Óptimo",
    "mensaje": "⚠️ Planta necesita atención. 3 días sin actividad."
  },
  "mascota": { ... }
}
```

---

### **4. Habits** (Hábitos)

#### GET /api/v1/habits/
Lista todos los hábitos del usuario.

**Query params:**
- `?activo=true` - Solo hábitos activos
- `?frecuencia=diaria` - Filtrar por frecuencia
- `?ordering=-fecha_creacion` - Ordenar

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Ejercicio diario",
    "descripcion": "30 minutos de ejercicio",
    "frecuencia": "diaria",
    "meta_semanal": 7,
    "activo": true,
    "racha_actual": 5,
    "total_completados": 12
  }
]
```

#### POST /api/v1/habits/
Crea un nuevo hábito.

**Body:**
```json
{
  "nombre": "Leer 30 minutos",
  "descripcion": "Leer libros de desarrollo personal",
  "frecuencia": "diaria",
  "meta_semanal": 5
}
```

#### GET /api/v1/habits/{id}/
Detalle de un hábito (incluye logs recientes).

**Respuesta:**
```json
{
  "id": 1,
  "nombre": "Ejercicio diario",
  ...
  "racha_actual": 5,
  "total_completados": 12,
  "logs_recientes": [...]
}
```

#### PATCH /api/v1/habits/{id}/
Actualiza un hábito.

**Body:**
```json
{
  "nombre": "Ejercicio matutino",
  "activo": false
}
```

#### DELETE /api/v1/habits/{id}/
Elimina un hábito.

#### GET /api/v1/habits/activos/
Retorna solo los hábitos activos.

#### POST /api/v1/habits/{id}/toggle_activo/
Activa/desactiva un hábito.

---

### **5. Habit Logs** (Registros de Hábitos)

#### GET /api/v1/habit-logs/
Lista todos los registros del usuario.

**Query params:**
- `?estado=cumplido` - Solo completados
- `?habit=1` - Logs de un hábito específico
- `?fecha_cumplimiento=2026-01-24` - Logs de una fecha

**Respuesta:**
```json
[
  {
    "id": 1,
    "habit": 1,
    "habit_nombre": "Ejercicio diario",
    "fecha_cumplimiento": "2026-01-24",
    "estado": "cumplido",
    "estado_display": "Cumplido",
    "notas": "30 min de cardio"
  }
]
```

#### POST /api/v1/habit-logs/
Marca un hábito como completado.

**Body:**
```json
{
  "habit": 1,
  "fecha_cumplimiento": "2026-01-24",
  "estado": "cumplido",
  "notas": "Me sentí muy bien!"
}
```

> **Importante:** Al crear un log con `estado: "cumplido"`, automáticamente se disparan los signals que:
> - Añaden +10 XP al perfil
> - Curan +10 puntos de vida a la mascota

#### GET /api/v1/habit-logs/today/
Logs de hoy.

#### GET /api/v1/habit-logs/week/
Logs de esta semana.

**Respuesta:**
```json
{
  "semana": {
    "inicio": "2026-01-20",
    "fin": "2026-01-26"
  },
  "total_logs": 15,
  "logs": [...]
}
```

#### PATCH /api/v1/habit-logs/{id}/
Actualiza un log.

#### DELETE /api/v1/habit-logs/{id}/
Elimina un log.

---

## 🧪 Cómo Probar la API

### **Opción 1: Browsable API de DRF**

1. Inicia sesión en: `http://localhost:8000/admin`
2. Ve a: `http://localhost:8000/api/v1/`
3. Navega por los endpoints con la interfaz web

### **Opción 2: Swagger UI**

Ve a: `http://localhost:8000/api/docs/`

### **Opción 3: cURL**

```bash
# 1. Obtener CSRF token y sessionid
curl -c cookies.txt http://localhost:8000/admin/login/

# 2. Login
curl -b cookies.txt -c cookies.txt -X POST \
  -H "X-CSRFToken: <token>" \
  -d "username=byPerry11&password=<tu_password>" \
  http://localhost:8000/admin/login/

# 3. Obtener dashboard
curl -b cookies.txt http://localhost:8000/api/v1/dashboard/me/

# 4. Marcar hábito como completado
curl -b cookies.txt -X POST \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{"habit": 1, "fecha_cumplimiento": "2026-01-24", "estado": "cumplido"}' \
  http://localhost:8000/api/v1/habit-logs/
```

### **Opción 4: Postman/Insomnia**

Importa la colección desde: `http://localhost:8000/api/schema/`

---

## 🔒 Seguridad

- ✅ Todos los endpoints requieren autenticación
- ✅ Los usuarios solo pueden acceder a sus propios datos
- ✅ Permisos `IsOwner` en Profile, Mascota, Habits
- ✅ Validaciones en serializers (no crear logs futuros, no acceder a hábitos ajenos)

---

## 📈 Flujo Típico de Uso

1. **Login** → `POST /admin/login/`
2. **Dashboard** → `GET /api/v1/dashboard/me/`
3. **Crear hábito** → `POST /api/v1/habits/`
4. **Marcar hábito cumplido** → `POST /api/v1/habit-logs/`
   - Se dispara signal: +10 XP, +10 Vida
5. **Ver progreso** → `GET /api/v1/profile/me/`
6. **Ver mascota** → `GET /api/v1/mascota/me/`

---

## 📝 Próximos Endpoints (Futuro)

- `POST /api/v1/auth/register/` - Registro de usuarios
- `POST /api/v1/auth/login/` - Login con JWT
- `GET /api/v1/achievements/` - Sistema de logros
- `GET /api/v1/accessories/` - Accesorios para la mascota
- `GET /api/v1/leaderboard/` - Ranking de usuarios
