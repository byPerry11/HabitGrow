# Documento Técnico — TestMascota

**Versión:** 1.0
**Fecha:** 2026-02-23
**Autores:** Equipo TestMascota

---

## Portada

Proyecto: TestMascota — Plataforma de gamificación de hábitos mediante mascota virtual.

Resumen ejecutivo: TestMascota es una aplicación web que combina seguimiento de hábitos con una mascota virtual gamificada. Los usuarios registran hábitos, obtienen recompensas (XP, HP, coins) y ven cómo su mascota evoluciona visualmente.

---

## Índice

1. Portada
2. Índice
3. Stack Tecnológico
4. Arquitectura General
5. Desglose de Módulos
   - Users (Autenticación y Perfil)
   - Pets (Mascota Virtual)
   - Habits (Seguimiento de Hábitos)
   - Dashboard (Vista consolidada)
6. Flujos de Datos Principales
7. API REST — Endpoints resumidos
8. Interfaz de Usuario (UI)
9. Base de Datos y Esquema
10. Configuración y despliegue
11. Gamificación y reglas de negocio
12. Anexos y referencias

---

## 3. Stack Tecnológico

- Backend
  - Framework: Django 5.x
  - API: Django REST Framework
  - Base de datos: PostgreSQL 16
  - Caché/Queue: Redis
  - Tasks: Celery
  - Documentación API: drf-spectacular (OpenAPI/Swagger)
  - Librerías clave: Pillow, python-decouple, django-cors-headers

- Frontend
  - HTML5 semántico
  - CSS: Tailwind CSS (CDN) + estilos custom
  - JS: Vanilla JavaScript (Fetch API, async/await)
  - Assets: Sprites PNG/JPG bajo `frontend/assets/mascotas/`

- DevOps
  - Contenedores: Docker Compose
  - Servicios: postgres, redis
  - Volúmenes persistentes para postgres y redis

---

## 4. Arquitectura General

- Arquitectura en capas: Frontend (SPA ligero) ↔ API REST (DRF) ↔ Base de datos relacional (Postgres).
- Automatización de lógica mediante Signals de Django (recompensas, creación de perfil).
- ViewSets y Routers de DRF para endpoints RESTful.
- Diseño pensado para minimizar llamadas desde el cliente mediante endpoint `dashboard` agregado.

Diagrama de alto nivel (texto):

Usuario (browser) → dashboard.html / index.html → fetch /api/v1/* → Django REST → PostgreSQL; Redis para caché/tareas.

---

## 5. Desglose de Módulos

### 5.1 Users (Autenticación & Perfil)

Responsabilidad: Gestión de usuarios, perfil extendido, recompensas a nivel de usuario.

Modelos clave:
- `User` (Django native)
- `Profile` (OneToOne → User)
  - `total_xp` (int)
  - `nivel` (int)
  - `coins` (int)
  - `profile_picture` (ImageField)
  - `last_daily_reward_date` (date)
  - `accesorios_equipados` (JSON)

Lógica de negocio:
- Signals: creación automática de `Profile` al crear `User`.
- Métricas de progreso: `progreso_nivel = (xp_actual / xp_requerido) * 100`.
- Fórmula recomendada (implementada): XP requerido para nivel N = 100 * N + 50 * (N - 1).

Endpoints relevantes:
- `GET /api/v1/profile/me/` — Obtener perfil del usuario autenticado.
- `PATCH /api/v1/profile/me/` — Actualizar foto y campos editables.

Permisos: `IsAuthenticated` + `IsOwner` para modificaciones.

### 5.2 Pets (Mascota Virtual)

Responsabilidad: Representar la entidad mascota, gestionar salud, evolución, XP y assets visuales.

Modelo principal: `Mascota`
- `user` (OneToOne)
- `nombre`, `especie`
- `total_xp`, `nivel`
- `puntos_vida` (0-100)
- `estado_salud` (Óptimo/Regular/Mal/Marchito)
- `nivel_evolucion` (visual)

Lógica de salud y evolución:
- Deterioro programado en función de inactividad (número de días sin completar hábitos).
- Curación al completar hábitos (+HP) y endpoint manual de curación.
- Evolución visual por rangos de nivel (stages).

Endpoints:
- `GET /api/v1/mascota/me/`
- `POST /api/v1/mascota/adoptar/` (crear/atribuir mascota)
- `PATCH /api/v1/mascota/{id}/` (editar nombre)
- `POST /api/v1/mascota/{id}/heal/`
- `POST /api/v1/mascota/{id}/update_health/`

Assets:
- Rutas en `frontend/assets/mascotas/{Especie}/{bby|Idle|Happy|Sad}.*`.

### 5.3 Habits (Seguimiento de Hábitos)

Responsabilidad: CRUD de hábitos, logs diarios, cálculo de rachas y recompensas.

Modelos:
- `Habit`
  - `user` (FK)
  - `nombre`, `descripcion`, `categoria`
  - `dias_semana` (string/csv)
  - `total_pasos` (int)
  - `activo` (bool)
- `HabitLog`
  - `habit` (FK)
  - `fecha_cumplimiento` (date)
  - `pasos_completados` (int)
  - `estado` (cumplido/no_cumplido)
  - Constraint: `unique(habit, fecha_cumplimiento)`

Lógica de recompensas:
- Al guardar `HabitLog(estado=cumplido)` → Signals aplican:
  - +10 XP mascota
  - +10 HP mascota
  - Si todos los hábitos del día están cumplidos → +20 coins a `Profile` (controlado por `last_daily_reward_date`).

Endpoints principales:
- `GET /api/v1/habits/` — Lista y filtros
- `POST /api/v1/habits/` — Crear
- `GET /api/v1/habits/{id}/` — Detalle + logs
- `PATCH /api/v1/habits/{id}/` — Editar
- `DELETE /api/v1/habits/{id}/`
- Endpoints auxiliares: `activos`, `toggle_activo`, `toggle_completado_hoy`.

### 5.4 Dashboard (Vista consolidada)

Responsabilidad: Endpoint agregador que devuelve el estado necesario para renderizar la SPA principal en una sola llamada.

Endpoint:
- `GET /api/v1/dashboard/me/` — Retorna `user`, `profile`, `mascota`, `habits` (resumen), `recent_logs`, `stats`.

Propósito: Reducir número de fetches desde el frontend al cargar la vista principal.

---

## 6. Flujos de Datos Principales

Flujo principal (completar hábito):
1. Usuario marca hábito completado (frontend) → POST `habit-logs/`.
2. Backend crea `HabitLog`.
3. Signals: +10 XP, +10 HP a mascota; actualizar nivel si aplica.
4. Si todos hábitos del día completos → +20 coins a `Profile`.
5. Frontend refetch dashboard o recursos afectados para actualizar UI.

Flujo salud mascota (inactividad):
1. Cron job / acción manual invoca `mascota/{id}/update_health/`.
2. Backend calcula días desde último log y aplica deterioro.
3. Actualiza `puntos_vida` y `estado_salud`.

---

## 7. API REST — Endpoints resumidos

(Tabla resumida, incluir en desarrollo completo) — ejemplos:
- `GET /api/v1/profile/me/`
- `PATCH /api/v1/profile/me/`
- `GET /api/v1/mascota/me/`
- `POST /api/v1/mascota/adoptar/`
- `GET /api/v1/habits/`
- `POST /api/v1/habit-logs/`
- `GET /api/v1/dashboard/me/`

(Ver archivo `backend/API_GUIDE.md` para documentación ampliada y el esquema OpenAPI en `/api/schema/`).

---

## 8. Interfaz de Usuario (UI)

Páginas principales:
- `index.html` — Login / Registro
- `dashboard.html` — SPA principal (pet+habits+stats)
- Plantillas Django para registro y otras vistas tradicionales

Componentes principales en `dashboard.html`:
- Sidebar (navegación)
- Header (usuario, coins, nivel)
- Pet container (animación / sprites)
- Habits list (tabla o cards)
- Stats panel (racha, completados)
- Modales: Nuevo hábito, Adoptar mascota, Editar

Design system (resumen):
- Paleta: verdes (emerald), ámbar, neutros.
- Tipografía: Plus Jakarta Sans (Google Fonts)
- Iconografía: Phosphor Icons
- Animaciones: float, wiggle, fade-in

---

## 9. Base de Datos y Esquema

Tablas principales:
- `auth_user`
- `profiles` (profile)
- `pets_mascota`
- `habits_habit`
- `habits_habitlog`

Índices y constraints importantes:
- `unique(habit, fecha_cumplimiento)` en `habitlog`
- Índices sobre `habits(user, activo)` y `habitlog(habit, fecha_cumplimiento)`

Almacenamiento de archivos: `media_files/profile_pics/`.

---

## 10. Configuración y despliegue

- Variables de entorno: DB_HOST, DB_NAME, DB_USER, DB_PASS, REDIS_URL, SECRET_KEY, DEBUG
- Django settings: `TIME_ZONE = 'America/Mexico_City'`, `LANGUAGE_CODE = 'es-mx'`
- Docker Compose: servicios `db` (postgres), `redis`, `web`.
- Static & media: `STATIC_ROOT` y `MEDIA_ROOT` configurados para almacenamiento local en desarrollo.

---

## 11. Gamificación y reglas de negocio

Resumen de reglas aplicadas:
- 1 `HabitLog` cumplido = +10 XP (mascota) +10 HP
- Todos los hábitos del día completados = +20 coins (1 vez por día)
- Fórmula de niveles: XP requerido para pasar a nivel N calculado por 100*N + 50*(N-1)
- Rachas: conteo de días consecutivos con hábito cumplido, utilizado para estadísticas y visualización.

---

## 12. Anexos y referencias

- Referencias a archivos clave en el repositorio:
  - [backend/API_GUIDE.md](backend/API_GUIDE.md)
  - [backend/requirements.txt](backend/requirements.txt)
  - [backend/habitgrow/settings.py](backend/habitgrow/settings.py)
  - [frontend/dashboard.html](frontend/dashboard.html)
  - [frontend/js/dashboard.js](frontend/js/dashboard.js)

- Siguientes recomendaciones / mejoras:
  - Añadir tests automáticos para signals y recompensas.
  - Implementar autenticación token-based (opcional) para APIs públicas.
  - Mover assets pesados a CDN/almacenamiento remoto en producción.

---

Fin del documento — versión inicial.
