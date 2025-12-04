# Configuración de OAuth para Facebook y Google

## 📘 CONFIGURACIÓN DE FACEBOOK LOGIN

### 1. Crear App de Facebook
1. Ve a [Facebook Developers](https://developers.facebook.com/)
2. Haz clic en "Mis Apps" → "Crear App"
3. Selecciona "Consumidor" como tipo de app
4. Nombre de la app: "Transportes del Bajío" (o el que prefieras)
5. Correo de contacto: tu correo
6. Haz clic en "Crear App"

### 2. Configurar Facebook Login
1. En el dashboard de tu app, busca "Facebook Login" y haz clic en "Configurar"
2. Selecciona "Web" como plataforma
3. URL del sitio: `http://localhost:5000` (para desarrollo)
4. En el menú lateral, ve a **Configuración → Básica**
5. Copia tu **ID de la app** y **Clave secreta de la app**

### 3. Configurar URLs de redirección
1. En el menú lateral, ve a **Facebook Login → Configuración**
2. En "URI de redireccionamiento de OAuth válidos" agrega:
   - `http://localhost:5000/auth/facebook/callback`
   - `http://127.0.0.1:5000/auth/facebook/callback`
3. Guarda los cambios

### 4. Actualizar app.py
Reemplaza en tu archivo `app.py`:
```python
facebook = oauth.register(
    name='facebook',
    client_id='TU_APP_ID',  # ← Pega aquí el ID de tu app
    client_secret='TU_APP_SECRET',  # ← Pega aquí la clave secreta
    access_token_url='https://graph.facebook.com/v10.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v10.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v10.0/',
    client_kwargs={'scope': 'email'},
)
```

---

## 🔴 CONFIGURACIÓN DE GOOGLE LOGIN

### 1. Crear proyecto en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto: "Transportes del Bajío"
3. Selecciona el proyecto recién creado

### 2. Habilitar Google+ API
1. En el menú, ve a **APIs y servicios → Biblioteca**
2. Busca "Google+ API" y habilítala
3. También busca y habilita "Google People API"

### 3. Crear credenciales OAuth
1. Ve a **APIs y servicios → Credenciales**
2. Haz clic en **+ CREAR CREDENCIALES → ID de cliente de OAuth 2.0**
3. Si te pide configurar la pantalla de consentimiento:
   - Tipo de usuario: **Externo**
   - Nombre de la app: "Transportes del Bajío"
   - Correo de asistencia: tu correo
   - Ámbitos: email, profile, openid (ya están por defecto)
   - Usuarios de prueba: agrega tu correo de Gmail
   - Guarda y continúa

4. Crear las credenciales:
   - Tipo de aplicación: **Aplicación web**
   - Nombre: "Transportes Bajío Web"
   - **Orígenes de JavaScript autorizados**:
     - `http://localhost:5000`
     - `http://127.0.0.1:5000`
   - **URIs de redireccionamiento autorizados**:
     - `http://localhost:5000/auth/google/callback`
     - `http://127.0.0.1:5000/auth/google/callback`
   
5. Haz clic en **Crear**
6. Copia tu **ID de cliente** y **Secreto del cliente**

### 4. Actualizar app.py
Reemplaza en tu archivo `app.py`:
```python
google = oauth.register(
    name='google',
    client_id='TU_GOOGLE_CLIENT_ID',  # ← Pega aquí el ID de cliente
    client_secret='TU_GOOGLE_CLIENT_SECRET',  # ← Pega aquí el secreto
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    client_kwargs={'scope': 'openid email profile'},
)
```

---

## 🚀 INSTALACIÓN DE DEPENDENCIAS

Asegúrate de tener instaladas las librerías necesarias:

```powershell
pip install authlib requests
```

---

## ✅ VERIFICACIÓN

1. Reinicia tu aplicación Flask
2. Ve a `http://localhost:5000/login`
3. Haz clic en el botón de Facebook o Google
4. Deberías ser redirigido a la página de autorización
5. Después de aprobar, volverás a tu app con sesión iniciada

---

## 📝 NOTAS IMPORTANTES

### Para Facebook:
- El correo del usuario solo se obtiene si el usuario lo tiene público en Facebook
- La foto de perfil se descarga automáticamente y se guarda en `static/uploads/`

### Para Google:
- Siempre proporciona email, nombre y foto
- Más confiable para obtener datos del usuario

### Para Producción:
Cuando subas tu app a producción, deberás:
1. Agregar tu dominio real a las URLs autorizadas en Facebook y Google
2. En Facebook, cambiar el modo de la app de "Desarrollo" a "Activo"
3. En Google, publicar la app y quitar el modo de prueba

---

## 🔧 TROUBLESHOOTING

### Error: "redirect_uri_mismatch"
- Verifica que las URLs de callback estén exactamente igual en Facebook/Google y en tu app

### Error: "invalid_client"
- Revisa que hayas copiado correctamente el client_id y client_secret

### Facebook no devuelve email
- Ve a Configuración de la App → Permisos de la app
- Asegúrate de solicitar el permiso "email"
