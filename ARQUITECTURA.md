# Arquitectura y Prácticas — Backend

## Stack

- **Framework:** FastAPI (Python 3.12+)
- **Base de datos:** MongoDB con Motor (async)
- **Autenticación:** JWT (access token en `Bearer`) + blacklist de tokens revocados
- **Hash de contraseñas:** bcrypt
- **Validación:** Pydantic v2
- **Contenedores:** Docker + Docker Compose

---

## Arquitectura: Clean Architecture por capas

```
src/
├── domain/          # Núcleo: entidades, interfaces, excepciones de negocio
├── application/     # Casos de uso, DTOs
├── infrastructure/  # Implementaciones concretas (MongoDB, JWT, bcrypt)
└── presentation/    # FastAPI: rutas, schemas de entrada/salida, dependencias
```

La regla de dependencias va siempre hacia adentro:  
`presentation → application → domain ← infrastructure`

---

## Capa Domain

- **Entidades** (`domain/entities/`): clases `@dataclass` puras sin dependencias externas.
  - `User`: campos del usuario incluyendo `role: Role`, `hashed_password`, fechas opcionales.
  - `Role`: enum con valores `analista`, `gerente`, `admin`.
- **Repositorios** (`domain/repositories/`): interfaces abstractas (`ABC`) que definen el contrato de persistencia. No saben nada de MongoDB.
- **Servicios de dominio** (`domain/services/`): interfaces abstractas para `PasswordService` y `TokenService`.
- **Excepciones** (`domain/exceptions.py`): excepciones de negocio del dominio.

---

## Capa Application

- **Casos de uso** (`application/use_cases/`): cada archivo es un caso de uso aislado.
  - `login.py`, `register.py`, `logout.py`, `refresh_token.py`
  - `get_current_user.py`, `get_user.py`, `update_user.py`, `delete_user.py`
  - `exceptions.py`: excepciones de aplicación (`UserNotFoundError`, `InvalidTokenError`, `TokenRevokedError`, `InactiveUserError`, etc.)
- **DTOs** (`application/dtos/`): objetos de transferencia de datos entre capas.
  - `ResponseDTO[T]`: envelope genérico con `status_code`, `message`, `data`, `error`.

---

## Capa Infrastructure

- **Base de datos** (`infrastructure/database/mongodb.py`): conexión async con Motor; `connect_to_mongo` y `close_mongo_connection` en el lifespan de FastAPI.
- **Repositorios** (`infrastructure/repositories/`): implementaciones concretas de las interfaces del dominio.
  - `MongoUserRepository`: CRUD de usuarios sobre la colección MongoDB.
  - `MongoTokenBlacklistRepository`: tokens revocados (para logout e invalidación).
- **Servicios** (`infrastructure/services/`):
  - `BcryptPasswordService`: hash y verificación de contraseñas.
  - `JWTTokenService`: generación y validación de JWT.
- **Configuración** (`infrastructure/config/settings.py`): Pydantic `BaseSettings`; lee variables de `.env`. Variables clave: `MONGO_URI`, `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`, `API_PREFIX`, `APP_NAME`, `DEBUG`.

---

## Capa Presentation

- **Rutas** (`presentation/api/v1/routes/`):
  - `auth.py`: endpoints públicos de autenticación (login, register, logout, refresh, me, admin-register).
  - `users.py`: CRUD de usuarios (requiere autenticación; algunas rutas solo para admin).
- **Schemas** (`presentation/schemas/`): modelos Pydantic de request/response que expone la API.
- **Dependencias** (`presentation/api/v1/dependencies.py`):
  - Inyección de repositorios y servicios vía `Depends`.
  - `get_current_user`: extrae y valida el Bearer token; retorna la entidad `User`.
  - `require_roles(*roles)`: decorador de autorización por rol; lanza 403 si el rol no está permitido.

---

## Autenticación y Autorización

- El cliente envía `Authorization: Bearer <token>` en cada petición protegida.
- `get_current_user` valida el token con `JWTTokenService` y verifica que no esté en la blacklist.
- `require_roles` se compone sobre `get_current_user` para restringir rutas por rol.
- En logout el token se agrega a la blacklist (`MongoTokenBlacklistRepository`) para invalidarlo antes de su expiración natural.

---

## Manejo de Errores

- Las excepciones de dominio/aplicación se capturan en las rutas y se convierten en `HTTPException`.
- Tres exception handlers globales en `main.py`:
  - `HTTPException` → respuesta con `ResponseDTO`.
  - `RequestValidationError` → 422 con errores serializados.
  - `Exception` genérica → 500.
- Todas las respuestas siguen el envelope `ResponseDTO { status_code, message, data, error }`.

---

## Prácticas

- **Una responsabilidad por archivo**: cada caso de uso es una clase con un método `execute()`.
- **Inversión de dependencias**: las capas externas implementan las interfaces del dominio; el dominio no importa nada de infraestructura.
- **Async de principio a fin**: Motor (MongoDB async), FastAPI async; no hay operaciones bloqueantes.
- **Variables de entorno**: toda configuración sensible en `.env`; nunca hardcodeada. Ver `.env.sample` para referencia.
- **Sin lógica de negocio en las rutas**: las rutas solo orquestan dependencias y llaman al caso de uso correspondiente.
- **Respuesta uniforme**: siempre `ResponseDTO`; el frontend puede depender de la misma forma en todos los endpoints.
