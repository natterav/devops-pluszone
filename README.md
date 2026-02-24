# PlusZone - Tinder meets LinkedIn

**PlusZone** es una plataforma de conexión profesional que combina la experiencia de swipe de Tinder con el enfoque profesional de LinkedIn. Conecta empresas con talento y viceversa de manera intuitiva y moderna.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Uso](#uso)
- [Documentación de Archivos](#documentación-de-archivos)
- [Roles de Usuario](#roles-de-usuario)
- [Categorías](#categorías)

## 🎯 Descripción

PlusZone permite a:
- **Empleados**: Explorar ofertas de trabajo mediante un sistema de swipe, filtrar por categorías y hacer match con empresas.
- **Empresas**: Descubrir candidatos calificados, publicar ofertas de trabajo y conectar con talento profesional.

La aplicación está diseñada con un enfoque en la experiencia de usuario, ofreciendo una interfaz moderna, responsive y fácil de usar.

## ✨ Características

### Para Empleados
- 🔍 Explorar ofertas de trabajo con sistema de swipe
- 🏷️ Filtrar ofertas por categorías (Informática, Industrial, Médicos)
- 💚 Hacer match con empresas
- 📊 Dashboard con estadísticas personales
- 💬 Sistema de mensajería (preparado)
- 👤 Perfil personalizable

### Para Empresas
- Descubrir candidatos calificados
- Crear y publicar ofertas de trabajo
-  Filtrar candidatos por categorías
-  Dashboard con métricas de la empresa
-  Ver matches con candidatos
-  Sistema de mensajería (preparado)

### Generales
-  Diseño moderno y responsive
-  Compatible con dispositivos móviles
-  Interfaz intuitiva y fluida
-  Sistema de autenticación
-  Estadísticas en tiempo real

## 🛠️ Tecnologías

- **HTML5**: Estructura semántica
- **CSS3**: Estilos modernos con variables CSS, flexbox y grid
- **JavaScript (Vanilla)**: Lógica de la aplicación sin frameworks
- **localStorage**: Almacenamiento local de datos
- **Unsplash API**: Imágenes de perfil de ejemplo

## 📁 Estructura del Proyecto

```
Full-Stack-Project--main/
│
├── client/                    # Frontend de la aplicación
│   ├── index.html            # Estructura HTML principal
│   ├── styles.css            # Estilos y diseño responsive
│   ├── app.js                # Lógica principal de la aplicación
│   └── database.js           # Simulación de base de datos con localStorage
│
├── server/                    # Backend (Express + Supabase/PostgreSQL)
│   ├── index.js              # Servidor Express principal
│   ├── db.js                 # Configuración de conexión a Supabase (PostgreSQL)
│   ├── init_db.js            # Script de migración (esquema + seeds)
│   ├── outboxWorker.js       # Worker para reintentos de envío de correo
│   ├── package.json          # Dependencias del servidor
│   ├── README_API.md         # Documentación de la API
│   └── node_modules/         # Dependencias instaladas
│
├── database/                  # Esquemas y datos de referencia
│   ├── pluszone_supabase.sql # Esquema PostgreSQL para Supabase (activo)
│   ├── Pluszone.sql          # Esquema MySQL legacy (referencia)
│   ├── database.json         # Datos de ejemplo en formato JSON
│   └── README_DB.md          # Documentación de la base de datos
│
├── docs/                      # Documentación adicional
│   └── DEPLOYMENT.md         # Guía de despliegue y troubleshooting
│
└── README.md                  # Este archivo (documentación principal)
```

## 🚀 Instalación

### Opción 1: Solo Frontend (modo demo con localStorage)

1. Clona el repositorio:
```bash
git clone <repository-url>
cd Full-Stack-Project--main
```

2. Abre el archivo `client/index.html` en tu navegador web moderno.

**Nota**: Esta opción no requiere servidor web ni instalación de dependencias. La aplicación funciona completamente en el cliente usando localStorage.

### Opción 2: Full Stack (con backend y base de datos)

1. Clona el repositorio:
```bash
git clone <repository-url>
cd Full-Stack-Project--main
```

2. Configura el servidor:
```bash
cd server
cp .env.example .env
# Edita .env con DATABASE_URL (Supabase) y SMTP. Ver docs/DEPLOYMENT.md
npm install
npm run migrate  # Aplica esquema y seeds en Supabase
npm run dev      # Inicia el servidor en modo desarrollo
```

3. Abre tu navegador en `http://localhost:4000`

Para más detalles sobre el despliegue, consulta [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

##  Uso

### Iniciar Sesión

1. Abre `client/index.html` en tu navegador (modo demo) o accede a `http://localhost:4000` (con servidor)
2. Selecciona tu tipo de usuario (Empleado o Empresa)
3. Ingresa tus credenciales o regístrate

### Modo Demo

Para probar la aplicación sin registro, puedes usar el modo demo:
- **Empleado**: Selecciona "Empleado" en el login
- **Empresa**: Selecciona "Empresa" en el login

El sistema creará automáticamente un usuario de prueba.

### Navegación

- **Buscar Candidatos / Ofertas**: Explora perfiles con sistema de swipe
- **Matches**: Ve tus conexiones exitosas
- **Mis Ofertas** (solo empresas): Gestiona tus ofertas de trabajo
- **Mensajes**: Sistema de mensajería (preparado)
- **Dashboard**: Estadísticas y métricas
- **Mi Perfil**: Edita tu información personal

##  Documentación de Archivos

### Frontend (`client/`)

#### `client/index.html`
**Descripción**: Estructura HTML principal de la aplicación.

**Funcionalidades**:
- Pantalla de carga inicial
- Formularios de autenticación (login/registro)
- Layout principal con sidebar y contenido
- Secciones: Discover, Matches, Jobs, Messages, Dashboard, Profile
- Modales para crear ofertas de trabajo
- Overlay para matches
- Estructura responsive con menú móvil

**Elementos principales**:
- `#loadingScreen`: Pantalla de carga
- `#authScreen`: Autenticación
- `#app`: Aplicación principal
- Sidebar de navegación
- Contenedores de contenido dinámico

---

#### `client/styles.css`
**Descripción**: Hojas de estilo completas con diseño moderno y responsive.

**Funcionalidades**:
- Variables CSS para colores y temas
- Diseño responsive con media queries
- Animaciones y transiciones
- Estilos para tarjetas de perfil
- Sistema de swipe visual
- Layout de grid para matches
- Estilos de formularios
- Modales y overlays
- Menú móvil y sidebar

**Secciones principales**:
- Variables y reset CSS
- Pantalla de carga
- Autenticación
- Layout principal (sidebar, header, contenido)
- Tarjetas de perfil y swipe
- Matches y detalles
- Dashboard
- Formularios
- Responsive design

---

#### `client/app.js`
**Descripción**: Lógica principal de la aplicación. Maneja toda la funcionalidad del frontend.

**Funcionalidades principales**:

#### 1. **Gestión de Estado**
- `state`: Objeto global que mantiene el estado de la aplicación
- Perfiles, matches, swipes, usuario actual
- Índice de navegación y categorías seleccionadas

#### 2. **Datos Mock**
- `mockProfiles`: Perfiles de candidatos y ofertas de trabajo
- `mockCompanies`: Información de empresas
- Datos de ejemplo para demo

#### 3. **Autenticación**
- `handleLogin()`: Procesa el inicio de sesión
- `handleRegister()`: Registra nuevos usuarios
- `showAuthScreen()`: Muestra pantalla de autenticación
- `showMainApp()`: Inicializa la aplicación principal
- `handleLogout()`: Cierra sesión

#### 4. **Navegación**
- `showSection()`: Cambia entre secciones
- `setupUserNavigation()`: Configura navegación según tipo de usuario
- Menú móvil responsive

#### 5. **Gestión de Perfiles**
- `loadProfile()`: Carga información del perfil
- `saveProfile()`: Guarda cambios del perfil
- `updateUserInfo()`: Actualiza información del usuario
- `editProfileImage()`: Cambia imagen de perfil

#### 6. **Sistema de Swipe**
- `renderCards()`: Renderiza tarjetas de perfil
- `createCardHTML()`: Genera HTML de tarjetas
- `setupCardListeners()`: Configura eventos de arrastre
- `handleSwipe()`: Procesa acciones de swipe (like/pass)
- `filterByCategory()`: Filtra perfiles por categoría

#### 7. **Matches**
- `renderMatches()`: Muestra lista de matches
- `viewMatchProfile()`: Ver detalles de un match
- `createMatchDetailsHTML()`: Genera panel de detalles
- `showMatchOverlay()`: Muestra overlay de match exitoso

#### 8. **Dashboard**
- `updateDashboard()`: Actualiza dashboard según usuario
- `updateEmployeeDashboard()`: Dashboard para empleados
- `updateCompanyDashboard()`: Dashboard para empresas
- `updateStats()`: Actualiza estadísticas

#### 9. **Ofertas de Trabajo (Empresas)**
- `handleCreateJobOffer()`: Crea nueva oferta
- `renderCompanyJobs()`: Muestra ofertas de la empresa
- `deleteJob()`: Elimina oferta

#### 10. **Filtrado y Búsqueda**
- `filterProfilesByUserType()`: Filtra por tipo de usuario
- `getAvailableCategories()`: Obtiene categorías disponibles
- `renderCategoryFilter()`: Renderiza selector de categorías

#### 11. **Actividad**
- `addActivity()`: Agrega actividad al feed
- `renderActivity()`: Muestra lista de actividades

#### 12. **Utilidades**
- `initLoadingScreen()`: Inicializa pantalla de carga
- `init()`: Inicializa la aplicación

---

#### `client/database.js`
**Descripción**: Simulación de base de datos usando localStorage del navegador.

**Funcionalidades**:
- `init()`: Inicializa la base de datos con datos por defecto
- `getAll()`: Obtiene todos los datos
- `save()`: Guarda datos en localStorage
- `getUsers()`: Obtiene todos los usuarios
- `getUserByEmail()`: Busca usuario por email
- `createUser()`: Crea nuevo usuario
- `updateUser()`: Actualiza usuario existente
- `validateAdmin()`: Valida credenciales de administrador
- `getAdmins()`: Obtiene todos los administradores
- `addSwipe()`: Registra acción de swipe
- `addMatch()`: Crea un match entre usuarios
- `getStats()`: Obtiene estadísticas generales

**Estructura de datos**:
- `users`: Usuarios del sistema
- `profiles`: Perfiles de candidatos/empleos
- `swipes`: Historial de swipes
- `matches`: Matches realizados
- `messages`: Mensajes (preparado)

**Nota**: En producción, esto debería conectarse a un backend real con base de datos SQL/NoSQL.

---

### Backend (`server/`)

#### `server/index.js`
**Descripción**: Servidor Express principal que maneja la API REST y sirve los archivos estáticos del frontend.

**Endpoints principales**:
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/verify` - Verificación de correo electrónico
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/profiles` - Obtener perfiles visibles
- `POST /api/profiles` - Crear perfil

**Características**:
- Servidor Express con Socket.IO para eventos en tiempo real
- Rate limiting (60 req/min por IP)
- Servicio de archivos estáticos desde `client/`
- Migración automática de base de datos al iniciar

---

#### `server/db.js`
**Descripción**: Configuración de conexión a MySQL usando mysql2.

---

#### `server/init_db.js`
**Descripción**: Script de migración que crea la base de datos, tablas y datos iniciales.

**Uso**: Ejecutar con `npm run migrate` desde la carpeta `server/`.

---

#### `server/README_API.md`
**Descripción**: Documentación detallada de la API REST. Consulta este archivo para más información sobre los endpoints disponibles.

---

### Base de Datos (`database/`)

#### `database/Pluszone.sql`
**Descripción**: Esquema SQL principal para MySQL. Contiene la estructura completa de tablas y datos iniciales.

**Tablas principales**:
- `users`: Usuarios del sistema
- `profiles`: Perfiles de candidatos y ofertas
- `swipes`: Historial de interacciones
- `matches`: Conexiones exitosas
- `messages`: Sistema de mensajería
- `companies`: Información de empresas

**Uso**: Este archivo es usado automáticamente por `server/init_db.js` durante la migración.

---

#### `database/database.sql`
**Descripción**: Esquema SQL alternativo para referencia.

---

#### `database/database.json`
**Descripción**: Datos de ejemplo en formato JSON para referencia.

**Contenido**:
- Usuarios de ejemplo
- Perfiles de candidatos
- Ofertas de trabajo
- Estructura de datos de referencia

**Uso**: Útil para entender la estructura de datos y para importar datos de prueba.

---

#### `database/README_DB.md`
**Descripción**: Documentación específica sobre la base de datos y usuarios de prueba.

**Contenido**:
- Información sobre archivos de base de datos
- Usuarios admin de prueba
- Métodos disponibles de Database
- Estructura de datos
- Notas de seguridad

---

### Documentación (`docs/`)

#### `docs/DEPLOYMENT.md`
**Descripción**: Guía completa de despliegue, troubleshooting y solución de problemas comunes.

**Contenido**:
- Instrucciones de instalación paso a paso
- Errores comunes y soluciones
- Guías de despliegue para diferentes plataformas
- Configuración de SMTP y correo electrónico

## 👥 Roles de Usuario

### Empleado
- Ve ofertas de trabajo publicadas por empresas
- Puede hacer swipe (like/pass) en ofertas
- Hace match con empresas
- Tiene dashboard personal con estadísticas
- Puede editar su perfil

### Empresa
- Ve candidatos disponibles
- Puede hacer swipe (like/pass) en candidatos
- Publica ofertas de trabajo
- Hace match con candidatos
- Tiene dashboard con métricas de la empresa
- Puede editar perfil de empresa

### Administrador
- Acceso completo al sistema
- Puede gestionar usuarios
- Ver estadísticas globales

**Credenciales de prueba**:
- Email: `admin@pluszone.com`
- Password: `admin123`

##  Categorías

Las ofertas y candidatos se pueden filtrar por categorías:

- **Informática**: Desarrolladores, DevOps, Diseñadores, Data Scientists, etc.
- **Industrial**: Ingenieros industriales, de producción, mecánicos, etc.
- **Médicos**: Médicos especialistas, enfermeras, profesionales de la salud

##  Características de Diseño

- **Responsive**: Adaptado para móvil, tablet y escritorio
- **Moderno**: Diseño limpio con gradientes y sombras
- **Intuitivo**: Navegación clara y fácil de usar
- **Animaciones**: Transiciones suaves para mejor UX
- **Accesible**: Colores contrastantes y texto legible

##  Próximas Mejoras

- [ ] Integración con backend real
- [ ] Sistema de mensajería completo
- [ ] Notificaciones en tiempo real
- [ ] Búsqueda avanzada con filtros múltiples
- [ ] Sistema de recomendaciones
- [ ] Integración con redes sociales
- [ ] Modo oscuro
- [ ] Internacionalización (i18n)

##  Notas

- La aplicación actualmente funciona completamente en el frontend
- Los datos se almacenan en localStorage del navegador
- Las imágenes de perfil usan Unsplash API (placeholder)
- En producción, se requiere implementar backend y base de datos real
- Las contraseñas están en texto plano (solo para desarrollo)

## Backend, Supabase y verificación por correo
El backend usa **Express + Supabase (PostgreSQL)** en la carpeta `server`:

- **Base de datos**: Supabase. Configura `DATABASE_URL` en `server/.env` (Conexión directa en Supabase → Project Settings → Database).
- **Registro**: `POST /api/auth/register` (correo debe ser `@tecmilenio.mx`). Se envía un **código de 7 dígitos** por correo (Nodemailer).
- **Verificación**: `POST /api/auth/verify` para validar el código de 7 dígitos y activar la cuenta. El usuario **no puede entrar** hasta verificar.
- **Login**: `POST /api/auth/login` (solo usuarios verificados pueden acceder).
- **Perfiles**: `GET /api/profiles` devuelve perfiles de usuarios verificados.

Instrucciones rápidas:
1. Ve a `server`, copia `.env.example` a `.env` y configura **DATABASE_URL** (Supabase) y SMTP.
2. `npm install` y `npm run migrate` (aplica esquema y seeds en Supabase).
3. `npm run dev` y abre `http://localhost:4000`.

**Despliegue en GitHub Pages**: El workflow `.github/workflows/deploy-pages.yml` despliega el frontend (`client/`) en cada push a `main`. En el repo: Settings → Pages → Source: **GitHub Actions**. Luego edita `client/config.js` y asigna la URL de tu backend (`window.API_BASE = 'https://tu-backend.onrender.com';`). Ver `docs/DEPLOYMENT.md`.

Para más detalles, consulta [`server/README_API.md`](server/README_API.md) y [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

Esto permite que cuando un nuevo usuario se registre y verifique su correo, su perfil aparezca automáticamente para el resto de usuarios. Además, el servidor emite eventos en tiempo real (Socket.IO, evento `user_verified`) para notificar a clientes conectados y evitar depender únicamente del polling periodico.

## 👨 Desarrollo

Este proyecto fue desarrollado como una aplicación de demostración con enfoque en el diseño y la experiencia de usuario. La funcionalidad está implementada para demostrar el concepto, pero requiere integración con backend para producción.

---

**PlusZone** - Conectando talento con oportunidades 🚀
