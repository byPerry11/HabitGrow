# Documento de Procedimientos — TestMascota

**Versión:** 1.0
**Fecha:** 2026-02-23
**Autores:** Equipo TestMascota

---

## 🛠️ Requisitos previos

- Estructura de carpetas ya definida (frontend/, backend/, media_files/, etc.).
- Módulos funcionales en desarrollo: `users`, `pets`, `habits`, `dashboard`.
- Visión de despliegue en producción (Docker Compose para servicios básicos: `postgres`, `redis`, `web`).

---

## 🚀 Pasos a seguir

### 1) Fase de Empatía y Definición (Design Thinking)

- Objetivo de usuario identificado: mejorar adherencia a hábitos mediante retroalimentación gamificada (mascota virtual que evoluciona).
- Cómo la estructura del proyecto responde a la necesidad:
  - Separación frontend/backend permite iterar UI rápidamente sin afectar la API.
  - `dashboard` consolidado reduce fricción (menos cargas) y mejora tiempo hasta el primer valor (TTFV) percibido por el usuario.
  - Modelos `Habit` + `HabitLog` reflejan el comportamiento real del usuario (registro diario, rachas), lo que permite métricas accionables.
- Justificación del diseño de interfaz:
  - Interfaz centrada en tareas: componentes visibles (pet, lista de hábitos, stats) permiten completar acciones en ≤3 clics.
  - Feedback inmediato: animaciones y barras de progreso muestran recompensa (XP/HP/coins), reforzando la conducta.
  - Accesibilidad y simplicidad: botones claros, estados de mascota con colores contrastados para comunicar urgencia.

### 2) Aplicación de Buenas Prácticas Técnicas

- Clean Code
  - Nombres descriptivos: usar `get_racha_actual()` / `update_health()` / `add_xp()` para facilitar lectura del código.
  - Funciones de responsabilidad única: dividir procesos en unidades pequeñas (ej. `calculate_xp_for_habit()`, `apply_daily_reward()`).
  - Tests unitarios por función: cada regla de negocio (XP, curación, racha) debe tener pruebas automatizadas.

- Env Variables (Gestión de datos sensibles)
  - No guardar credenciales en repositorio. Usar `.env` en desarrollo y variables de entorno en producción.
  - Variables mínimas recomendadas:
    - `SECRET_KEY`, `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`, `REDIS_URL`, `DJANGO_DEBUG`.
  - Documentar variables en `README.md` y validar en arranque (fallar temprano si faltan).

- Modularización
  - Separar capas: models → serializers → services → views → tasks.
  - Colocar lógica reusable en `services/` o helpers (ej. `pets/services.py` con funciones `heal_pet()`, `apply_xp()`), evitando business logic en vistas.
  - APIs pequeñas y enfocadas (single responsibility endpoints). Reusar serializers para lectura/creación según necesidad.

### 3) Preparación para Soporte y Nube

- Mantenibilidad y manejo de errores
  - Logs estructurados (JSON) con niveles (INFO/WARN/ERROR). En producción, enviar logs a un agregador (ELK/Datadog).
  - Métricas y alertas: instrumentar contadores (habits completados, errores 5xx, latencia de endpoints) y configurar alertas SLO/SLI.
  - Trazabilidad: incluir request-id en cabezales para correlacionar trazas distribuidas.
  - Plan de soporte: pasos para reproducir → entorno de staging → captura de logs → rollback si es crítico.

- Actualizaciones sin downtime
  - Contenerización: usar imágenes Docker para `web` y servicios auxiliares.
  - Migraciones de DB: aplicar migraciones con `django-migrations` en un step controlado; usar `--check` en CICD y migraciones desglosadas si hay cambios destructivos.
  - Despliegues seguros: usar estrategias Canary / Blue-Green o Rolling updates en orquestador (Kubernetes) o via scripts en host.
  - Feature flags para activar/desactivar funcionalidades experimentales sin desplegar nuevo código.

- Resiliencia y escalabilidad
  - Separación de estados: almacenar sessions/token en Redis o usar tokens stateless para escalar web en múltiples instancias.
  - Caché: usar Redis para datos de alto consumo (ej. resultado de `dashboard/me`) con TTL razonable.
  - Workers: procesar tasks pesadas o retrasadas (notificaciones, recalculos) con Celery y colas separadas.

- Backups y recuperación
  - Backups regulares de Postgres (daily + WAL shipping si procede).
  - Plan de recuperación documentado (RTO/RPO targets).

- Pruebas y CI/CD
  - Pipelines: lint → tests unitarios → build image → despliegue a staging → pruebas E2E → despliegue a producción.
  - Tests E2E para flujos críticos (registro, completar hábito, reward flow, adoptar mascota).

---

## Checklist rápido (para ejecutar antes de desplegar a producción)

- [ ] Variables de entorno documentadas y validadas
- [ ] Tests unitarios y E2E verdes
- [ ] Migraciones revisadas y probadas en staging
- [ ] Backups configurados y verificados
- [ ] Monitoreo y alertas activadas
- [ ] Documento de rollback actualizado

---

Fin del documento — versión inicial.
