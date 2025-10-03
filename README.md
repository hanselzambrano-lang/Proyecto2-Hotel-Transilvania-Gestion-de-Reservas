# 🏨 Sistema de Gestión de Reservas - Hotel Transilvania

Sistema completo de gestión de reservas hoteleras desarrollado con HTML, CSS, JavaScript y Flask (Python) con base de datos MySQL.

## 🎯 Características

- ✅ **Frontend responsivo** con tema de madera elegante
- ✅ **Sistema de reservas** con verificación de disponibilidad en tiempo real
- ✅ **Base de datos MySQL** con relaciones apropiadas
- ✅ **Backend Flask** con APIs REST
- ✅ **Validaciones** tanto frontend como backend
- ✅ **Interfaz amigable** con notificaciones y efectos visuales

## 🛠️ Tecnologías Utilizadas

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Base de Datos**: MySQL
- **Servidor**: XAMPP (recomendado)

## 📋 Requisitos Previos

1. **XAMPP** instalado y funcionando
2. **Python 3.8+** instalado
3. **MySQL** ejecutándose en XAMPP

## 🚀 Instalación

### 1. Configurar Base de Datos

1. Abrir **phpMyAdmin** (http://localhost/phpmyadmin)
2. Importar el archivo `hotel_reservas.sql`
3. Verificar que se crearon las tablas: `clientes`, `habitaciones`, `reservas`

### 2. Instalar Dependencias Python

```bash
# Navegar al directorio del proyecto
cd "ruta/del/proyecto"

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Estructura de Archivos

Asegúrate de tener esta estructura:

```
Proyecto2-Hotel-Transilvania-Gestion-de-Reservas/
│
├── templates/
│   └── index.html          # Página principal
├── static/
│   ├── style.css           # Estilos CSS
│   ├── script.js          # JavaScript
│   └── IMG/               # Imágenes
├── app.py                 # Aplicación Flask
├── requirements.txt       # Dependencias Python
├── hotel_reservas.sql     # Base de datos
└── README.md             # Este archivo
```

### 4. Mover Archivos a Templates

Si aún no lo has hecho, mueve `index.html` a la carpeta `templates/`:

```bash
mkdir templates
move index.html templates/
```

Y crea la carpeta `static/` y mueve los archivos CSS, JS e imágenes:

```bash
mkdir static
move style.css static/
move script.js static/
move IMG static/
```

### 5. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en: http://localhost:5000

## 📁 Estructura de la Base de Datos

### Tabla: `clientes`
- `id_cliente` (PK)
- `nombre`, `apellido`
- `telefono`, `email`
- `documento_identidad`

### Tabla: `habitaciones`
- `id_habitacion` (PK)
- `numero_habitacion`
- `tipo_habitacion` (Sencilla, Doble, Suite)
- `precio`
- `estado` (Disponible, Ocupada, Mantenimiento)

### Tabla: `reservas`
- `id_reserva` (PK)
- `id_cliente` (FK)
- `id_habitacion` (FK)
- `fecha_ingreso`, `fecha_salida`
- `estado` (Pendiente, Confirmada, Cancelada, Finalizada)

## 🎮 Uso del Sistema

1. **Página Principal**: Formulario de búsqueda de habitaciones
2. **Selección de Fechas**: Verificación automática de disponibilidad
3. **Elección de Habitación**: Cards interactivas con precios
4. **Datos del Cliente**: Modal para capturar información
5. **Confirmación**: Número de reserva generado

## 🔧 APIs Disponibles

- `POST /api/check-availability` - Verificar disponibilidad
- `POST /api/create-reservation` - Crear nueva reserva
- `GET /api/dashboard-stats` - Estadísticas del hotel

## 📱 Funcionalidades JavaScript

- ✅ Validación de fechas en tiempo real
- ✅ Filtrado por número de huéspedes
- ✅ Verificación de disponibilidad dinámica
- ✅ Notificaciones y mensajes de estado
- ✅ Modal para datos del cliente
- ✅ Efectos visuales y animaciones

## 🎨 Características de Diseño

- **Tema de madera** coherente en todo el sitio
- **Responsive design** para móviles y desktop
- **Efectos hover** en cards y botones
- **Gradientes** y sombras elegantes
- **Loading states** y feedback visual

## 🔒 Seguridad

- Validación de datos tanto frontend como backend
- Consultas preparadas para prevenir SQL injection
- Validación de fechas y disponibilidad
- Manejo de errores apropiado

## 📞 Soporte

Para problemas o preguntas sobre el sistema, verifica:

1. **XAMPP** esté ejecutándose
2. **MySQL** esté activo
3. **Base de datos** esté importada correctamente
4. **Dependencias Python** estén instaladas

## 👥 Créditos

Desarrollado como proyecto de gestión hotelera con enfoque en:
- Experiencia de usuario (UX)
- Arquitectura de software
- Integración frontend-backend
- Gestión de bases de datos relacionales