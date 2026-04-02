# Sistema de Gestión de Eventos

Sistema web para la administración de clientes, paquetes y registro de eventos para el negocio "Elotito Regio". Desarrollado con Python (Flask) y MySQL, cuenta con una vitrina pública para clientes y un panel de administración privado.

## Requisitos Previos

Antes de instalar el proyecto, asegúrate de tener instalado en tu computadora:
* **Python 3.x** (para ejecutar el servidor web).
* **XAMPP** (o cualquier otro servidor local que incluya Apache y MySQL).

---

## Guía de Instalación Paso a Paso

### 1. Preparar el Entorno
1. Descomprime el archivo `.zip` del proyecto.
2. Abre la carpeta extraída en tu editor de código (ej. Visual Studio Code).

### 2. Configurar la Base de Datos
1. Abre **XAMPP Control Panel** e inicia los servicios de **Apache** y **MySQL**.
2. Ve a tu navegador y abre phpMyAdmin: `http://localhost/phpmyadmin/`
3. Ve a la pestaña **SQL** en la parte superior.
4. Abre el archivo `sql/create_db.sql` que viene en el proyecto, copia todo su contenido y pégalo en la consola de phpMyAdmin.
5. Haz clic en **Continuar** para crear la base de datos `elotito_regio_db` y todas sus tablas optimizadas.

### 3. Configurar Python y Dependencias
Abre una terminal dentro de la carpeta del proyecto en VS Code y ejecuta los siguientes comandos:

**Crear el entorno virtual:**
```bash
python -m venv .venv

