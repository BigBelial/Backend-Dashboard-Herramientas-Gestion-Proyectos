# Backend — Herramientas para la gestión de proyectos de software

Servicio backend en **FastAPI** con autenticación JWT y MongoDB, organizado siguiendo Clean Architecture. Expone endpoints de autenticación, gestión de usuarios y un dashboard analítico.

> Para el detalle de capas, dependencias y convenciones internas ver [ARQUITECTURA.md](ARQUITECTURA.md).

---

## Stack

- **Lenguaje:** Python 3.12+
- **Framework:** FastAPI 0.115 + Uvicorn
- **Base de datos:** MongoDB (driver async `motor`)
- **Auth:** JWT (PyJWT) + bcrypt para hash de contraseñas
- **Validación / settings:** Pydantic v2 + pydantic-settings
- **Contenedores:** Docker + Docker Compose

---

## Requisitos previos

Para levantarlo necesitas **una** de estas dos rutas:

### Opción A — Docker (recomendada)
- [Docker](https://docs.docker.com/get-docker/) 20+ con Compose v2
- Una instancia de **MongoDB accesible** (ver sección [Base de datos](#base-de-datos))

### Opción B — Local (sin Docker)
- Python 3.12+
- `pip` y `venv`
- MongoDB en local (o accesible por red)

---

## Base de datos

El servicio usa **MongoDB**. No requiere migraciones: las colecciones se crean al primer uso.

- Colecciones principales: `users`, `token_blacklist` (y las que consuma `dashboard`).
- Por defecto la base se llama `auth_db` (configurable con `MONGODB_DB_NAME`).
- Conexión por defecto: `mongodb://localhost:27017`.

Formas comunes de tener MongoDB corriendo:

```bash
# 1) Instancia local con Docker
docker run -d --name mongo -p 27017:27017 mongo:7

# 2) MongoDB Atlas u otra instancia gestionada
#    Usar la connection string que da el proveedor en MONGODB_URL
```

> ⚠️ El `docker-compose.yml` actual **solo levanta el backend**, no incluye un contenedor de MongoDB. Debes apuntar `MONGODB_URL` a una instancia existente. Si Mongo corre en el host de Docker, usa `mongodb://host.docker.internal:27017` (ya está habilitado en el compose).

---

## Variables de entorno

Copia el archivo de ejemplo y edita los valores:

```bash
cp .env.sample .env
```

Variables disponibles:

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `APP_NAME` | Nombre de la app que se muestra en OpenAPI | `FastAPI Auth Service` |
| `DEBUG` | Modo debug de FastAPI | `False` |
| `API_PREFIX` | Prefijo para todas las rutas | `/api/v1` |
| `MONGODB_URL` | Connection string de MongoDB | `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Nombre de la base de datos | `auth_db` |
| `JWT_SECRET_KEY` | **Clave secreta** para firmar tokens (cámbiala en producción) | `your-secret-key-here` |
| `JWT_ALGORITHM` | Algoritmo de firma JWT | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Vida del access token (min) | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Vida del refresh token (días) | `7` |

> 🔐 **No commitees `.env`**. Para producción, genera un `JWT_SECRET_KEY` fuerte, por ejemplo: `python -c "import secrets; print(secrets.token_urlsafe(64))"`.

---

## Levantar el servicio

### Con Docker Compose

```bash
# Desde la carpeta Backend/
docker compose up --build
```

- Reconstruye la imagen, monta `./src` con hot-reload (`uvicorn --reload`) y publica el puerto **8000**.
- Carga variables desde `.env`.
- `host.docker.internal` está habilitado para alcanzar servicios del host (útil si Mongo corre fuera del contenedor).

Para detenerlo: `Ctrl+C` y luego `docker compose down`.

### En local (sin Docker)

```bash
# 1) Crear y activar entorno virtual
python3.12 -m venv venv
source venv/bin/activate           # macOS / Linux
# .\venv\Scripts\activate          # Windows PowerShell

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Configurar entorno
cp .env.sample .env
# editar .env con los valores que correspondan

# 4) Arrancar el servidor (PYTHONPATH apunta a src/)
PYTHONPATH=src uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Si todo va bien, la app estará en:

- API base: `http://localhost:8000/api/v1`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Endpoints (resumen)

Todos cuelgan de `API_PREFIX` (por defecto `/api/v1`). Las rutas protegidas requieren cabecera `Authorization: Bearer <token>`.

### Auth — `/auth`
| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/auth/register` | Registro público de usuario |
| `POST` | `/auth/admin/register` | Registro creando usuario con rol arbitrario (solo admin) |
| `POST` | `/auth/login` | Login con credenciales → access + refresh token |
| `POST` | `/auth/logout` | Revoca el token actual (blacklist) |
| `POST` | `/auth/refresh` | Renueva tokens a partir del refresh |
| `GET` | `/auth/me` | Devuelve el usuario autenticado |

### Users — `/users` (autenticado)
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/users/` | Lista de usuarios (admin) |
| `GET` | `/users/{user_id}` | Detalle de un usuario |
| `PATCH` | `/users/{user_id}` | Edición (admin puede editar a cualquiera; un usuario solo a sí mismo) |
| `DELETE` | `/users/{user_id}` | Eliminación |

### Dashboard — `/dashboard` (autenticado)
KPIs y agregaciones para analítica: `/kpis`, `/trends`, `/geo/*`, `/institutions`, `/programs`, `/socioeconomic/*`, `/economic/*`, `/personal/*`, `/filters/*`.

> Roles disponibles: `analista`, `gerente`, `admin`. Algunas rutas exigen rol específico (ver `presentation/api/v1/dependencies.py`).

---

## Formato de respuesta

Todas las respuestas usan el envelope `ResponseDTO`:

```json
{
  "status_code": 200,
  "message": "OK",
  "data": { "...": "..." },
  "error": null
}
```

Errores de validación devuelven `422` con la lista de errores en `error`.

---

## Estructura del proyecto

```
Backend/
├── src/
│   ├── domain/          # Entidades, interfaces, excepciones de negocio
│   ├── application/     # Casos de uso, DTOs
│   ├── infrastructure/  # MongoDB, JWT, bcrypt, settings
│   ├── presentation/    # Rutas FastAPI, schemas, dependencias
│   └── main.py          # Punto de entrada (ASGI app)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.sample
├── ARQUITECTURA.md
└── README.md
```

---

## Verificación rápida

Con el servidor arriba:

```bash
# Health check vía OpenAPI
curl http://localhost:8000/openapi.json | head -c 200

# Registro
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!"}'
```

---

## Troubleshooting

- **`ServerSelectionTimeoutError` / `connection refused`:** MongoDB no está accesible. Verifica `MONGODB_URL` y que el servicio esté arriba. Desde Docker usa `host.docker.internal` para alcanzar Mongo en el host.
- **`ModuleNotFoundError: main`:** falta `PYTHONPATH=src` al lanzar uvicorn fuera de Docker.
- **`401 Unauthorized` en rutas protegidas:** falta o expiró el token. Llama a `/auth/login` o `/auth/refresh`.
- **`403 Forbidden`:** el usuario no tiene el rol requerido (revisa que tu usuario sea `admin` para rutas administrativas).
- **Cambios no se reflejan en Docker:** el compose monta `./src` con `--reload`; si editaste fuera de `src/` reconstruye con `docker compose up --build`.
