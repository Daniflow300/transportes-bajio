# 🚀 Cómo Actualizar tu Sitio Web en Render

## Proceso Automático (Recomendado)

Cada vez que hagas cambios en tu código local, sigue estos 3 pasos:

### 1️⃣ Prueba tus cambios localmente
```powershell
# Activa el entorno virtual (si no está activo)
& "C:\Users\DaniF\OneDrive\Documentos\PAGINA WEB\transportes_bajio\venv\Scripts\Activate.ps1"

# Ejecuta la aplicación
python app.py

# Abre http://127.0.0.1:5000 en tu navegador y verifica que todo funcione
```

### 2️⃣ Sube los cambios a GitHub
```powershell
# Agrega todos los archivos modificados
git add .

# Crea un commit descriptivo
git commit -m "Descripción clara de lo que cambiaste"

# Sube a GitHub
git push origin main
```

### 3️⃣ Espera el despliegue automático en Render
- Render detecta automáticamente el push
- Descarga el nuevo código
- Instala dependencias
- Reinicia la aplicación
- ✅ ¡Tu sitio está actualizado!

**Tiempo estimado:** 2-5 minutos después del push

---

## Ejemplos de Mensajes de Commit

Buenos ejemplos:
```bash
git commit -m "Agregué sección de testimonios en página principal"
git commit -m "Corregí error en formulario de contacto"
git commit -m "Actualicé precios de paquetes de mudanzas"
git commit -m "Agregué nueva foto en galería de servicios"
```

Malos ejemplos:
```bash
git commit -m "cambios"
git commit -m "fix"
git commit -m "update"
```

---

## Verificar el Estado del Despliegue

1. Ve a https://dashboard.render.com/
2. Inicia sesión
3. Haz clic en tu proyecto `transportes-bajio`
4. Verás el historial de despliegues:
   - 🟢 **Live** = Despliegue exitoso y activo
   - 🔵 **Building** = Construcción en proceso
   - 🔴 **Failed** = Error (revisa los logs)

---

## Comandos Útiles

### Ver qué archivos cambiaron
```powershell
git status
```

### Ver diferencias específicas
```powershell
git diff app.py
```

### Ver historial de commits
```powershell
git log --oneline
```

### Descartar cambios locales (¡cuidado!)
```powershell
git checkout -- archivo.py
```

---

## ⚠️ Casos Especiales

### Si cambiaste `requirements.txt`
Render automáticamente instalará las nuevas dependencias. Solo asegúrate de que también las instalaste localmente:
```powershell
pip install -r requirements.txt
```

### Si agregaste nuevas imágenes
1. Sube las imágenes a la carpeta `static/img/` o `static/uploads/`
2. Haz commit y push normalmente
3. Las imágenes se subirán a Render automáticamente

### Si cambiaste variables de entorno
1. Ve a Render Dashboard → tu proyecto → Environment
2. Agrega o modifica las variables manualmente
3. Haz clic en "Save Changes"
4. Render reiniciará automáticamente

### Si cambiaste la base de datos
⚠️ **Importante:** La base de datos en Render es DIFERENTE a la local.

Para cambios en la estructura:
1. Haz los cambios en FreeSQLDatabase directamente vía phpMyAdmin
2. O exporta tu BD local y reimporta en la nube
3. **NO** uses `app.py` para migraciones en producción

---

## 🔧 Solución de Problemas

### "El sitio no se actualiza"
1. Verifica que hiciste `git push` correctamente
2. Revisa Render Dashboard para ver si hay errores
3. Limpia caché del navegador (Ctrl + Shift + R)

### "Error 500 en el sitio"
1. Revisa logs en Render Dashboard → Logs
2. Verifica variables de entorno
3. Asegúrate de que `requirements.txt` está actualizado

### "No puedo hacer push"
```powershell
# Asegúrate de tener configurado tu token de GitHub
git remote set-url origin https://daniflow300@github.com/daniflow300/transportes-bajio.git
git push origin main
# Te pedirá tu Personal Access Token
```

---

## 📋 Checklist Antes de Subir Cambios

- [ ] Probé los cambios localmente
- [ ] Todo funciona correctamente
- [ ] No hay errores en la consola
- [ ] Hice `git add .`
- [ ] Hice `git commit -m "mensaje descriptivo"`
- [ ] Hice `git push origin main`
- [ ] Esperé 2-5 minutos para el despliegue
- [ ] Probé el sitio en transportesdelbajio.com

---

## 🎯 Tips Profesionales

1. **Haz commits frecuentes** - No acumules muchos cambios
2. **Mensajes claros** - Tu yo del futuro te lo agradecerá
3. **Prueba localmente SIEMPRE** - Evita errores en producción
4. **Revisa los logs** - Render te muestra errores detallados
5. **Haz backups** - Exporta tu BD periódicamente

---

## Enlaces Importantes

- **Tu Sitio:** https://transportesdelbajio.com
- **Render Dashboard:** https://dashboard.render.com/
- **GitHub Repo:** https://github.com/daniflow300/transportes-bajio
- **FreeSQLDatabase:** https://www.freesqldatabase.com/account/

---

**¿Necesitas ayuda?** Consulta los logs en Render o revisa este archivo nuevamente.
