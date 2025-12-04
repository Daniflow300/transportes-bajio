# Guía de Despliegue - Transportes del Bajío

## Opciones para Subir tu Página Web

### OPCIÓN 1: RENDER (RECOMENDADO - GRATIS)
✅ **Ventajas**: Gratis, fácil, soporta MySQL
❌ **Desventajas**: Se duerme después de 15 min de inactividad (versión gratis)

**Pasos:**
1. Crea cuenta en https://render.com
2. Crea un nuevo "Web Service"
3. Conecta tu repositorio de GitHub (sube tu código a GitHub primero)
4. Configuración:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Agrega una base de datos MySQL en Render
6. Configura las variables de entorno:
   ```
   MYSQL_HOST=<tu-host-render>
   MYSQL_USER=<usuario>
   MYSQL_PASSWORD=<contraseña>
   MYSQL_DB=fletes_mudanzas
   SECRET_KEY=<genera-una-clave-aleatoria>
   ```

### OPCIÓN 2: PYTHONANYWHERE (MÁS SIMPLE)
✅ **Ventajas**: Muy fácil, específico para Python, MySQL incluido
❌ **Desventajas**: Limitaciones en versión gratis (CPU, tráfico)

**Pasos:**
1. Crea cuenta en https://www.pythonanywhere.com
2. Sube tus archivos vía web o Git
3. Crea una MySQL database en el dashboard
4. Configura la aplicación web apuntando a `app.py`
5. Configura variables de entorno en el archivo de configuración

### OPCIÓN 3: RAILWAY (MODERNO)
✅ **Ventajas**: Muy fácil, moderno, buen soporte
❌ **Desventajas**: Plan gratis limitado ($5 crédito inicial)

**Pasos:**
1. Crea cuenta en https://railway.app
2. Conecta tu repositorio GitHub
3. Railway detecta automáticamente Flask
4. Agrega MySQL plugin
5. Configura variables de entorno automáticamente

### OPCIÓN 4: VERCEL (CON LIMITACIONES)
⚠️ No recomendado para tu caso porque MySQL requiere configuración adicional

---

## IMPORTANTE - Antes de Subir

### 1. Cambiar SECRET_KEY
En `app.py`, línea 14:
```python
app.secret_key = os.environ.get('SECRET_KEY', 'clave_temporal_desarrollo')
```

### 2. Configurar Base de Datos
Deberás migrar tu base de datos MySQL local a la nube. Opciones:
- **FreeMySQLHosting**: hosting MySQL gratis
- **PlanetScale**: MySQL gratis con límites generosos
- **Railway/Render**: Incluyen base de datos

### 3. Exportar tu Base de Datos Local
```bash
# Desde PowerShell en la carpeta del proyecto
mysqldump -u root -p159357 fletes_mudanzas > database_backup.sql
```

### 4. Variables de Entorno a Configurar
```
SECRET_KEY=genera-una-clave-aleatoria-segura
MYSQL_HOST=tu-host-produccion
MYSQL_USER=tu-usuario
MYSQL_PASSWORD=tu-contraseña
MYSQL_DB=fletes_mudanzas
MAIL_USERNAME=tu-correo@gmail.com
MAIL_PASSWORD=tu-password-app
SEND_EMAILS=True
```

---

## MI RECOMENDACIÓN PASO A PASO

**Para empezar GRATIS y RÁPIDO:**

1. **Sube tu código a GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/transportes-bajio.git
   git push -u origin main
   ```

2. **Usa RENDER para el hosting**
   - Ve a https://render.com
   - Crea Web Service desde tu repo GitHub
   - Render automáticamente instala dependencias

3. **Usa FREEMYSQLHOSTING para la base de datos**
   - Ve a https://www.freemysqlhosting.net
   - Crea una base de datos gratis
   - Importa tu `database_backup.sql`

4. **Conecta todo en las variables de entorno de Render**

---

## Archivos Creados para el Despliegue

✅ `Procfile` - Indica cómo ejecutar la app
✅ `runtime.txt` - Especifica versión de Python
✅ `.gitignore` - Evita subir archivos innecesarios
✅ `requirements.txt` - Actualizado con gunicorn

**Tu app está lista para subirse a internet.**

---

## ¿Necesitas Ayuda?

Dime qué plataforma prefieres y te ayudo con el proceso específico:
1. Render (mi recomendación)
2. PythonAnywhere (más simple)
3. Railway (moderno)
