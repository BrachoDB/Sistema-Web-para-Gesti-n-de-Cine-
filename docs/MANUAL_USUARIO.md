# 📖 Manual de Usuario - CineMax

Guía completa para utilizar el sistema de gestión de cine CineMax.

---

## 📑 Contenido

- [Flujo para Clientes](#-flujo-para-clientes)
- [Flujo para Administradores](#-flujo-para-administradores)
- [Interfaz de Pantallas](#-interfaz-de-pantallas)
- [FAQ - Preguntas Frecuentes](#-faq---preguntas-frecuentes)

---

## 👥 Flujo para Clientes

### 1️⃣ Explorar la Cartelera

**Página:** [`index.html`](../frontend/index.html)

Al acceder al sistema, los clientes ven la cartelera con todas las películas disponibles:

```
┌─────────────────────────────────────────────────────────────┐
│  CineMax                                    [Iniciar Sesión]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│           🎬 CARTELERA DISPONIBLE                           │
│     Vive la magia del cine interactivo y premium            │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  [IMAGEN]    │  │  [IMAGEN]    │  │  [IMAGEN]    │       │
│  │              │  │              │  │              │       │
│  │ Dune Parte 2 │  │ Kung Fu      │  │ Godzilla vs  │       │
│  │              │  │ Panda 4      │  │ Kong         │       │
│  │ [25 Mar]     │  │ [26 Mar]     │  │ [27 Mar]     │       │
│  │ [19:30]      │  │ [20:00]      │  │ [18:00]      │       │
│  │ $15.000      │  │ $12.000      │  │ $18.000      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Acciones disponibles:**
- 🔍 Ver todas las películas en cartelera
- 🕐 Ver horarios disponibles por película
- 💰 Ver precios de cada función
- 🖱️ Click en un horario para iniciar compra

---

### 2️⃣ Registro de Usuario (Opcional)

**Página:** [`registro.html`](../frontend/registro.html)

Para registrar una nueva cuenta:

```
┌─────────────────────────────────────────────────────────────┐
│                    📝 CREAR CUENTA                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Nombre completo                                     │    │
│  │ [____________________________________________]      │    │
│  │                                                     │    │
│  │ Correo electrónico                                  │    │
│  │ [____________________________________________]      │    │
│  │                                                     │    │
│  │ Contraseña (mínimo 6 caracteres)                    │    │
│  │ [____________________________________________]      │    │
│  │                                                     │    │
│  │         [    REGISTRARSE    ]                       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│         ¿Ya tienes cuenta? [Iniciar Sesión]                 │
└─────────────────────────────────────────────────────────────┘
```

**Pasos:**
1. Ingresar nombre completo
2. Ingresar correo electrónico válido
3. Crear contraseña (mínimo 6 caracteres)
4. Click en "Registrarse"
5. El sistema iniciará sesión automáticamente

**Nota:** El registro es opcional. Los clientes pueden comprar sin cuenta, pero no tendrán historial de compras.

---

### 3️⃣ Inicio de Sesión

**Página:** [`login.html`](../frontend/login.html)

Para usuarios ya registrados:

```
┌─────────────────────────────────────────────────────────────┐
│                     🔐 INICIAR SESIÓN                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Correo electrónico                                  │    │
│  │ [____________________________________________]      │    │
│  │                                                     │    │
│  │ Contraseña                                          │    │
│  │ [____________________________________________]      │    │
│  │                                                     │    │
│  │         [    INGRESAR    ]                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│         ¿No tienes cuenta? [Registrarse]                    │
└─────────────────────────────────────────────────────────────┘
```

**Pasos:**
1. Ingresar correo registrado
2. Ingresar contraseña
3. Click en "Ingresar"

---

### 4️⃣ Selección de Asientos

**Página:** [`compra.html`](../frontend/compra.html)

Mapa interactivo de la sala:

```
┌─────────────────────────────────────────────────────────────┐
│                    🎭 SELECCIONA TUS ASIENTOS               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                                                     │    │
│  │              ╔═══════════════════════╗              │    │
│  │              ║      🎬 PANTALLA      ║              │    │
│  │              ╚═══════════════════════╝              │    │
│  │                                                     │    │
│  │    A  ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯              │    │
│  │    B  ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯              │    │
│  │    C  ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯              │    │
│  │    ...                                              │    │
│  │    J  ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯ ◯              │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Leyenda:  ◯ Disponible   🔵 Seleccionado   ⚫ Ocupado      │
│                                                             │
│  ───────────────────────────────────────────────────────    │
│                                                             │
│  Total: $45.000                    Asientos: 3              │
│                                                             │
│              [   CONFIRMAR COMPRA   ]                       │
└─────────────────────────────────────────────────────────────┘
```

**Instrucciones:**
1. Seleccionar asientos disponibles (círculos blancos)
2. Los asientos seleccionados se marcan en azul
3. Los asientos ocupados aparecen en gris/negro
4. Ver el total acumulado
5. Click en "Confirmar Compra"

**Después de la compra:**
```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                        🎉                                   │
│              ¡COMPRA EXITOSA!                               │
│                                                             │
│     Muestra el código en taquilla para ingresar.            │
│                                                             │
│         ┌─────────────────────────┐                         │
│         │   🎫 A1B2C3D4            │                         │
│         └─────────────────────────┘                         │
│                                                             │
│              [VOLVER A CARTELERA]                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**¡IMPORTANTE!** Guardar el código del tiquete (ej: A1B2C3D4). Si iniciaste sesión, recibirás un correo electrónico premium con el código QR para un acceso más rápido.

---

### 5️⃣ Validación de Tiquetes

**Página:** [`validacion.html`](../frontend/validacion.html)

Para verificar si un tiquete es válido:

```
┌─────────────────────────────────────────────────────────────┐
│                 ✅ VALIDAR TIQUETE                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                                                     │    │
│  │        Ingresa el código de tu tiquete              │    │
│  │                                                     │    │
│  │        [________________________]                   │    │
│  │                                                     │    │
│  │           [    VALIDAR    ]                         │    │
│  │                                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Posibles resultados:                                       │
│  ✅ Válido   - Tiquete correcto, listo para usar.           │
│  ⚠️ Usado    - El tiquete ya fue utilizado en esta función. │
│  ⌛ Temprano  - Aún falta para la función (15 min antes).   │
│  🚫 Finalizada - La película ya terminó y expiró.           │
│  ❌ Inválido - Código no encontrado en el sistema.          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 👑 Flujo para Administradores

### 🔐 Acceso Administrativo

**Credenciales por defecto:**
- Email: `admin@cine.com`
- Contraseña: `admin123`

**Página:** [`admin.html`](../frontend/admin.html)

---

### 📊 Dashboard Principal

```
┌─────────────────────────────────────────────────────────────┐
│  CineMax - ADMIN                              [Cerrar Sesión│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  💰 VENTAS TOTALES: $1.250.000                              │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  OCUPACIÓN DE FUNCIONES                             │    │
│  │  ────────────────────────────────────────────────   │    │
│  │  Dune Parte 2 - Sala 1 - 25 Mar 19:30      45/150 (30%)      │
│  │  ████████████░░░░░░░░░░░░░░░░░░░░                     │    │
│  │                                                     │    │
│  │  Kung Fu Panda 4 - Sala 2 - 26 Mar 20:00   89/150 (59%)      │
│  │  ████████████████████░░░░░░░░░░                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  [📊 Reportes]  [🎬 Películas]  [📅 Funciones]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Funciones disponibles:**
- Ver ventas totales acumuladas
- Ver ocupación por función en tiempo real
- Acceder a reportes detallados
- Gestionar películas y funciones

---

### 🎬 Gestión de Películas

```
┌─────────────────────────────────────────────────────────────┐
│                 🎬 GESTIÓN DE PELÍCULAS                     │
│                                                             │
│  [ + Nueva Película ]                                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Título:    [________________________]               │    │
│  │ Descripción:[________________________]              │    │
│  │ Duración:  [___] minutos                           │    │
│  │ Género:    [________________________]               │    │
│  │ Clasificación:[_____________________]               │    │
│  │ Imagen URL: [________________________]              │    │
│  │ Trailer URL:[________________________]              │    │
│  │                                                     │    │
│  │ [ Guardar ]  [ Cancelar ]                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  LISTADO:                                                   │
│  ┌────┬──────────────────┬─────────┬────────────┬─────────┐ │
│  │ ID │ Título           │ Género  │ Estado     │ Acciones│ │
│  ├────┼──────────────────┼─────────┼────────────┼─────────┤ │
│  │ 1  │ Dune Parte 2     │ Sci-Fi  │ ✅ Activa  │ ✏️ 🗑️  │ │
│  │ 2  │ Kung Fu Panda 4  │ Animación│ ✅ Activa │ ✏️ 🗑️  │ │
│  └────┴──────────────────┴─────────┴────────────┴─────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Acciones:**
- ✏️ Editar película
- 🗑️ Eliminar película (solo si no tiene funciones activas)
- + Crear nueva película

---

### 📅 Gestión de Funciones

```
┌─────────────────────────────────────────────────────────────┐
│                📅 GESTIÓN DE FUNCIONES                      │
│                                                             │
│  [ + Nueva Función ]                                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Película:  [ Seleccionar... ▼ ]                     │    │
│  │ Fecha:     [________________] 📅                    │    │
│  │ Hora:      [________________] 🕐                    │    │
│  │ Sala:      [ Sala 1 ▼ ]                             │    │
│  │ Precio:    $[______________]                        │    │
│  │                                                     │    │
│  │ [ Guardar ]  [ Cancelar ]                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  LISTADO:                                                   │
│  ┌────┬──────────────────┬──────────┬───────┬────────┬────────┬────┐ │
│  │ ID │ Película         │ Fecha    │ Hora  │ Sala   │ Precio │    │ │
│  ├────┼──────────────────┼──────────┼───────┼────────┼────────┼────┤ │
│  │ 1  │ Dune Parte 2     │25-03-2024│ 19:30 │ Sala 1 │ $15.000│ 🗑️│ │
│  │ 2  │ Kung Fu Panda 4  │26-03-2024│ 20:00 │ Sala 2 │ $12.000│ 🗑️│ │
│  └────┴──────────────────┴──────────┴───────┴────────┴────────┴────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Notas:**
- No se puede eliminar una función que ya tiene tiquetes vendidos
- Las funciones se cancelan (cambian de estado) en lugar de eliminarse

---

### 📈 Reportes Administrativos

#### Ventas por Día
```
┌─────────────────────────────────────────────────────────────┐
│                 📊 VENTAS POR DÍA                           │
│                                                             │
│  ┌─────────────┬─────────────────┬─────────────────────┐    │
│  │ Fecha       │ Tiquetes Vendidos │ Total Ventas      │    │
│  ├─────────────┼─────────────────┼─────────────────────┤    │
│  │ 20-03-2024  │ 15              │ $225.000           │    │
│  │ 19-03-2024  │ 23              │ $345.000           │    │
│  │ 18-03-2024  │ 31              │ $465.000           │    │
│  └─────────────┴─────────────────┴─────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Películas Más Vistas
```
┌─────────────────────────────────────────────────────────────┐
│              🏆 PELÍCULAS MÁS VISTAS                        │
│                                                             │
│  ┌────┬──────────────────┬──────────┬──────────┬──────────┐ │
│  │ #  │ Título           │ Género   │ Tiquetes │ Recaudado│ │
│  ├────┼──────────────────┼──────────┼──────────┼──────────┤ │
│  │ 🥇 │ Dune Parte 2     │ Sci-Fi   │ 145      │$2.175.000│ │
│  │ 🥈 │ Kung Fu Panda 4  │ Animación│ 98       │$1.470.000│ │
│  │ 🥉 │ Godzilla vs Kong │ Acción   │ 76       │$1.368.000│ │
│  └────┴──────────────────┴──────────┴──────────┴──────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Interfaz de Pantallas

### Página Principal (Cartelera)
- **URL:** `index.html`
- **Propósito:** Mostrar películas disponibles
- **Elementos:**
  - Barra de navegación con logo
  - Grid de películas con imagen, título y horarios
  - Botones de autenticación

### Login
- **URL:** `login.html`
- **Propósito:** Autenticación de usuarios
- **Elementos:**
  - Formulario de email y contraseña
  - Enlace a registro

### Registro
- **URL:** `registro.html`
- **Propósito:** Crear nueva cuenta
- **Elementos:**
  - Formulario con nombre, email y contraseña
  - Validaciones en tiempo real

### Compra (Selección de Asientos)
- **URL:** `compra.html?funcion_id=X`
- **Propósito:** Seleccionar asientos y comprar
- **Elementos:**
  - Mapa de sala 10x15
  - Leyenda de estados
  - Resumen de compra
  - Confirmación con código

### Panel Admin
- **URL:** `admin.html`
- **Propósito:** Gestión administrativa
- **Elementos:**
  - Dashboard con métricas
  - Tabs: Dashboard, Películas, Funciones
  - Formularios CRUD
  - Reportes y estadísticas

### Validación
- **URL:** `validacion.html`
- **Propósito:** Verificar tiquetes
- **Elementos:**
  - Campo de código
  - Indicador de resultado

---

## ❓ FAQ - Preguntas Frecuentes

### 💳 Compras y Pagos

**¿Puedo comprar sin registrarme?**
> Sí, el sistema permite compras sin cuenta. Sin embargo, no tendrás acceso al historial de compras.

**¿Qué métodos de pago aceptan?**
> Este es un sistema de demostración. El "pago" se simula al confirmar la compra. En producción se integraría pasarelas de pago.

**¿Puedo cancelar una compra?**
> No, una vez generado el tiquete no se puede cancelar. Contacta a administración si tienes problemas.

**¿Cuántos asientos puedo comprar?**
> Puedes comprar hasta todos los asientos disponibles de una función (máximo 150).

---

### 🎫 Tiquetes

**¿Dónde veo mi tiquete después de comprar?**
> Al confirmar la compra se muestra el código en pantalla. Guárdalo o tómale captura.

**¿Cómo valido mi tiquete en el cine?**
> Muestra el código almacenado en taquilla. El personal lo verificará en el sistema.

**¿Puedo usar el mismo tiquete varias veces?**
> No. Una vez validado, el tiquete cambia a estado "Usado" y no permite reingreso.

**¿El tiquete tiene fecha de vencimiento?**
> El tiquete es válido únicamente para la función específica que compraste.

**¿Qué pasa si pierdo mi código?**
> Si compraste con cuenta de usuario, contacta a administración. Si fue compra anónima, no hay forma de recuperarlo.

---

### 👤 Cuenta de Usuario

**¿Cómo recupero mi contraseña?**
> Actualmente el sistema no tiene recuperación automática. Contacta al administrador.

**¿Puedo cambiar mi correo electrónico?**
> No, el email es el identificador único de cuenta y no se puede modificar.

**¿Qué ventajas tiene registrarme?**
> - Historial de compras
- Compras más rápidas (datos prellenados)
- Soporte para recuperación de tiquetes

---

### 🛠️ Técnico

**¿El sistema funciona en móviles?**
> Sí, la interfaz es responsive y se adapta a dispositivos móviles.

**¿Qué navegadores soportan?**
> Chrome, Firefox, Safari, Edge (últimas versiones).

**¿Necesito instalar algo?**
> No, solo necesitas un navegador web. El backend debe estar corriendo en el servidor.

---

### 👑 Administración

**¿Cómo accedo al panel de admin?**
> Inicia sesión con las credenciales: admin@cine.com / admin123

**¿Puedo crear más cuentas de administrador?**
> Sí, desde la base de datos o modificando el rol de un usuario existente a 'admin'.

**¿Cómo agrego una nueva película?**
> En el panel Admin → Películas → "Nueva Película". Llena todos los campos requeridos.

**¿Puedo editar una función que ya tiene tiquetes vendidos?**
> Sí, pero con precaución. No se puede cancelar una función con ventas existentes.

**¿Los reportes son en tiempo real?**
> Sí, el dashboard y reportes reflejan los datos actuales de la base de datos.

---

## 📞 Soporte

Para problemas técnicos o consultas:
- 📧 Email: soporte@cinemax.com
- 📱 Teléfono: (604) 123-4567

---

**CineMax - Sistema de Gestión de Cine**  
*Tecnológico de Antioquia - 2024*
