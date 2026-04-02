# 🔌 API REST - CineMax

Documentación completa de los endpoints disponibles en la API de CineMax.

**URL Base:** `http://localhost:5000/api`

---

## 📑 Índice de Endpoints

- [Autenticación](#-autenticación)
- [Películas](#-películas)
- [Funciones](#-funciones)
- [Tiquetes](#-tiquetes)
- [Administración](#-administración)

---

## 🔐 Autenticación

### POST /auth/register
Registra un nuevo usuario cliente.

**URL:** `/api/auth/register`

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@email.com",
  "contrasena": "password123"
}
```

**Validaciones:**
- `nombre`: Requerido
- `email`: Requerido, formato válido, único
- `contrasena`: Mínimo 6 caracteres

**Respuesta Exitosa (201 Created):**
```json
{
  "message": "Usuario registrado exitosamente",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "nombre": "Juan Pérez",
  "rol": "cliente"
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 400 | No se recibieron datos |
| 400 | Todos los campos son requeridos |
| 400 | La contraseña debe tener al menos 6 caracteres |
| 400 | El email ya está registrado |
| 500 | Error al registrar usuario |

---

### POST /auth/login
Inicia sesión y obtiene token JWT.

**URL:** `/api/auth/login`

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "email": "juan@email.com",
  "contrasena": "password123"
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Login exitoso",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "nombre": "Juan Pérez",
  "rol": "cliente"
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 400 | No se recibieron datos |
| 400 | Email y contraseña son requeridos |
| 401 | Credenciales inválidas |
| 500 | Error al iniciar sesión |

---

### GET /auth/me
Obtiene información del usuario autenticado.

**URL:** `/api/auth/me`

**Headers:**
```http
Authorization: Bearer <token>
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@email.com",
  "rol": "cliente",
  "fecha_creacion": "2024-03-20 10:30:00"
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 401 | Token faltante o inválido |
| 404 | Usuario no encontrado |
| 500 | Error al obtener usuario |

---

## 🎬 Películas

### GET /peliculas
Obtiene todas las películas registradas.

**URL:** `/api/peliculas/`

**Headers:** No requiere autenticación

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 1,
    "titulo": "Dune: Parte Dos",
    "descripcion": "Paul Atreides se une a...",
    "duracion": 166,
    "genero": "Ciencia Ficción",
    "clasificacion": "+12",
    "imagen_url": "https://...",
    "trailer_url": "https://...",
    "estado": "activa"
  }
]
```

---

### GET /peliculas/{id}
Obtiene una película específica por ID.

**URL:** `/api/peliculas/1`

**Parámetros:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `id` | int | ID de la película |

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "titulo": "Dune: Parte Dos",
  "descripcion": "Paul Atreides se une a...",
  "duracion": 166,
  "genero": "Ciencia Ficción",
  "clasificacion": "+12",
  "imagen_url": "https://...",
  "trailer_url": "https://...",
  "estado": "activa"
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 404 | Pelicula no encontrada |
| 500 | Error del servidor |

---

### POST /peliculas
Crea una nueva película.

**URL:** `/api/peliculas/`

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "titulo": "Dune: Parte Dos",
  "descripcion": "Paul Atreides se une a...",
  "duracion": 166,
  "genero": "Ciencia Ficción",
  "clasificacion": "+12",
  "imagen_url": "https://...",
  "trailer_url": "https://..."
}
```

**Campos Requeridos:** `titulo`, `duracion`

**Respuesta Exitosa (201 Created):**
```json
{
  "message": "Pelicula creada",
  "id": 1
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 400 | Titulo y duracion requeridos |
| 500 | Error del servidor |

---

### PUT /peliculas/{id}
Actualiza una película existente.

**URL:** `/api/peliculas/1`

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "titulo": "Nuevo Título",
  "descripcion": "Nueva descripción",
  "duracion": 120,
  "genero": "Acción",
  "clasificacion": "+16",
  "imagen_url": "https://...",
  "trailer_url": "https://...",
  "estado": "activa"
}
```

**Nota:** Se debe proporcionar al menos un campo para actualizar.

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Pelicula actualizada correctamente"
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 400 | Debe proporcionar al menos un campo |
| 404 | Pelicula no encontrada |
| 500 | Error del servidor |

---

### DELETE /peliculas/{id}
Elimina una película.

**URL:** `/api/peliculas/1`

**Notas:**
- No se puede eliminar si tiene funciones activas
- Las funciones asociadas se eliminan en cascada

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Pelicula eliminada correctamente"
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 400 | No se puede eliminar porque tiene funciones activas |
| 404 | Pelicula no encontrada |
| 500 | Error del servidor |

---

## 📅 Funciones

### GET /funciones
Obtiene todas las funciones disponibles.

**URL:** `/api/funciones/`

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 1,
    "pelicula_id": 1,
    "fecha": "2024-03-25",
    "hora": "19:30:00",
    "sala": "Sala 1",
    "precio": 15000.00,
    "estado": "disponible",
    "titulo": "Dune: Parte Dos",
    "imagen_url": "https://..."
  }
]
```

---

### GET /funciones/{id}
Obtiene una función específica con información de la película.

**URL:** `/api/funciones/1`

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "pelicula_id": 1,
  "fecha": "2024-03-25",
  "hora": "19:30:00",
  "sala": "Sala 1",
  "precio": 15000.00,
  "estado": "disponible",
  "titulo": "Dune: Parte Dos",
  "imagen_url": "https://...",
  "genero": "Ciencia Ficción",
  "clasificacion": "+12"
}
```

---

### GET /funciones/{id}/asientos
Obtiene el mapa de asientos para una función específica.

**URL:** `/api/funciones/1/asientos`

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 1,
    "numero": 1,
    "fila": "A",
    "columna": 1,
    "estado": "activo",
    "estado_funcion": "disponible"
  },
  {
    "id": 5,
    "numero": 5,
    "fila": "A",
    "columna": 5,
    "estado": "activo",
    "estado_funcion": "ocupado"
  }
]
```

**Nota:** El campo `estado_funcion` indica si el asiento está ocupado para esta función específica.

---

### POST /funciones
Crea una nueva función.

**URL:** `/api/funciones/`

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "pelicula_id": 1,
  "fecha": "2024-03-25",
  "hora": "19:30",
  "sala": "Sala 1",
  "precio": 15000
}
```

**Campos Requeridos:** `pelicula_id`, `fecha`, `hora`, `precio`
**Campos Opcionales:** `sala` (Por defecto: "Sala 1")

**Respuesta Exitosa (201 Created):**
```json
{
  "message": "Funcion creada",
  "id": 1
}
```

---

### PUT /funciones/{id}
Actualiza una función existente.

**URL:** `/api/funciones/1`

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "pelicula_id": 2,
  "fecha": "2024-03-26",
  "hora": "20:00",
  "sala": "Sala 2",
  "precio": 18000,
  "estado": "disponible"
}
```

**Nota:** Se debe proporcionar al menos un campo para actualizar.

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Funcion actualizada correctamente"
}
```

**Validaciones de Horario:**
- El sistema no permite programar funciones en la misma **Sala** y **Fecha** cuyos horarios se traslapen.
- Se incluye un margen automático de 20 minutos entre funciones para limpieza.

---

### DELETE /funciones/{id}
Cancela una función (cambia estado a 'cancelada').

**URL:** `/api/funciones/1`

**Notas:**
- No se elimina físicamente, solo cambia el estado
- No se puede cancelar si ya tiene tiquetes vendidos

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Funcion cancelada correctamente"
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 400 | La funcion ya esta cancelada |
| 400 | No se puede cancelar porque ya hay tiquetes vendidos |
| 404 | Funcion no encontrada |

---

## 🎫 Tiquetes

### POST /tiquetes
Crea un nuevo tiquete de compra.

**URL:** `/api/tiquetes/`

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "funcion_id": 1,
  "asientos": [5, 6, 7],
  "usuario_id": 1
}
```

**Campos:**
| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `funcion_id` | int | Sí | ID de la función |
| `asientos` | array | Sí | Array de IDs de asientos |
| `usuario_id` | int | No | ID del usuario (opcional) |

**Respuesta Exitosa (201 Created):**
```json
{
  "message": "Compra exitosa",
  "tiquete": {
    "id": 1,
    "codigo": "A1B2C3D4",
    "total": 45000.00
  }
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 400 | funcion_id y asientos son requeridos |
| 400 | Uno o mas asientos ya estan ocupados |
| 404 | Funcion no encontrada o no disponible |

---

### POST /tiquetes/validar
Valida un tiquete por su código.

**URL:** `/api/tiquetes/validar`

**Headers:**
```http
Content-Type: application/json
```

**Body:**
```json
{
  "codigo": "A1B2C3D4"
}
```

**Respuesta Exitosa (200 OK):**

Si es válido (primera vez):
```json
{
  "estado": "Válido"
}
```

Si ya fue usado:
```json
{
  "estado": "Usado"
}
```

Si no existe:
```json
{
  "estado": "Inválido"
}
```

**Nota:** Al validar un tiquete válido, su estado cambia automáticamente a 'usado'.

---

## 👑 Administración

**Nota:** Todos los endpoints de administración requieren autenticación con rol `admin`.

### GET /admin/dashboard
Obtiene estadísticas del dashboard administrativo.

**URL:** `/api/admin/dashboard`

**Headers:**
```http
Authorization: Bearer <token>
```

**Respuesta Exitosa (200 OK):**
```json
{
  "total_ventas": 1250000.00,
  "ocupacion": [
    {
      "id": 1,
      "titulo": "Dune: Parte Dos",
      "fecha": "2024-03-25",
      "hora": "19:30:00",
      "sala": "Sala 1",
      "asientos_ocupados": 45,
      "capacidad_total": 150
    }
  ]
}
```

**Errores Posibles:**
| Código | Descripción |
|--------|-------------|
| 403 | Acceso no autorizado (requiere rol admin) |
| 401 | Token faltante o inválido |

---

### GET /admin/ventas-por-dia
Obtiene reporte de ventas agrupadas por día.

**URL:** `/api/admin/ventas-por-dia`

**Headers:**
```http
Authorization: Bearer <token>
```

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "fecha": "2024-03-20",
    "cantidad_tiquetes": 15,
    "total_ventas": 225000.00
  },
  {
    "fecha": "2024-03-19",
    "cantidad_tiquetes": 23,
    "total_ventas": 345000.00
  }
]
```

---

### GET /admin/peliculas-mas-vistas
Obtiene ranking de películas con más tiquetes vendidos.

**URL:** `/api/admin/peliculas-mas-vistas`

**Headers:**
```http
Authorization: Bearer <token>
```

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 1,
    "titulo": "Dune: Parte Dos",
    "genero": "Ciencia Ficción",
    "cantidad_tiquetes": 145,
    "total_recaudado": 2175000.00
  },
  {
    "id": 2,
    "titulo": "Kung Fu Panda 4",
    "genero": "Animación",
    "cantidad_tiquetes": 98,
    "total_recaudado": 1470000.00
  }
]
```

---

## 📊 Resumen de Endpoints

| Método | Endpoint | Autenticación | Descripción |
|--------|----------|---------------|-------------|
| POST | `/auth/register` | No | Registro de usuarios |
| POST | `/auth/login` | No | Inicio de sesión |
| GET | `/auth/me` | Sí | Perfil de usuario |
| GET | `/peliculas` | No | Listar películas |
| GET | `/peliculas/{id}` | No | Detalle de película |
| POST | `/peliculas` | No | Crear película |
| PUT | `/peliculas/{id}` | No | Actualizar película |
| DELETE | `/peliculas/{id}` | No | Eliminar película |
| GET | `/funciones` | No | Listar funciones |
| GET | `/funciones/{id}` | No | Detalle de función |
| GET | `/funciones/{id}/asientos` | No | Mapa de asientos |
| POST | `/funciones` | No | Crear función |
| PUT | `/funciones/{id}` | No | Actualizar función |
| DELETE | `/funciones/{id}` | No | Cancelar función |
| POST | `/tiquetes` | No | Comprar tiquete |
| POST | `/tiquetes/validar` | No | Validar tiquete |
| GET | `/admin/dashboard` | Admin | Dashboard stats |
| GET | `/admin/ventas-por-dia` | Admin | Ventas por fecha |
| GET | `/admin/peliculas-mas-vistas` | Admin | Ranking películas |

---

## 🔒 Códigos de Estado HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Petición exitosa |
| 201 | Created | Recurso creado exitosamente |
| 400 | Bad Request | Datos inválidos o faltantes |
| 401 | Unauthorized | Token JWT faltante o inválido |
| 403 | Forbidden | No tiene permisos necesarios |
| 404 | Not Found | Recurso no encontrado |
| 500 | Internal Server Error | Error del servidor |

---

## 📝 Notas de Implementación

1. **Autenticación JWT:** Todos los endpoints marcados como "Sí" en autenticación requieren el header `Authorization: Bearer <token>`

2. **Formato de fechas:** Las fechas se manejan en formato ISO 8601: `YYYY-MM-DD`

3. **Formato de horas:** Las horas se manejan en formato: `HH:MM:SS` o `HH:MM`

4. **Precios:** Los precios se manejan en formato decimal con 2 decimales

5. **CORS:** La API está configurada para aceptar peticiones desde cualquier origen en desarrollo
