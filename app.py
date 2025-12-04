from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from PIL import Image
import re



app = Flask(__name__)
app.secret_key = 'clave_secreta_super_segura'

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from authlib.integrations.flask_client import OAuth
import requests
from urllib.parse import urlparse
from uuid import uuid4

# CONFIGURACIÓN DE CORREO
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'TU_CORREO@gmail.com'
app.config['MAIL_PASSWORD'] = 'TU_PASSWORD_APP'
app.config['MAIL_DEFAULT_SENDER'] = 'TU_CORREO@gmail.com'

mail = Mail(app)

# Controla si se envían correos (útil en desarrollo). Cambiar a True para activar envío.
app.config['SEND_EMAILS'] = False

# SERIALIZADOR DE TOKENS
serializer = URLSafeTimedSerializer(app.secret_key)

# Inicializar Authlib OAuth (para proveedores como Facebook)
oauth = OAuth(app)

# Registrar proveedor Facebook
# INSTRUCCIONES: Ve a https://developers.facebook.com/
# 1. Crea una app, ve a Configuración > Básica
# 2. Copia el App ID y App Secret
# 3. Ve a Productos > Facebook Login > Configuración
# 4. Añade la URL: http://127.0.0.1:5000/auth/facebook/callback
facebook = oauth.register(
    name='facebook',
    client_id='881278685074120',
    client_secret='c0c082c6648a55b7aaaa1a57b6e55c76',
    access_token_url='https://graph.facebook.com/v18.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v18.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v18.0/',
    client_kwargs={'scope': 'email public_profile'}
)

# Registrar proveedor Google
# INSTRUCCIONES: Ve a https://console.cloud.google.com/
# 1. Crea un proyecto, ve a APIs y servicios > Credenciales
# 2. Crea credenciales OAuth 2.0
# 3. Añade la URL de redireccionamiento: http://127.0.0.1:5000/auth/google/callback
# 4. Copia Client ID y Client Secret
google = oauth.register(
    name='google',
    client_id='3371246556-332eao4dasc64knr9eabov16o2k0rh5r.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)


def download_and_save_image(url):
    try:
        resp = requests.get(url, stream=True, timeout=10)
        if resp.status_code != 200:
            return None

        # Try to get extension from URL path, fallback to jpg
        parsed = urlparse(url)
        root, ext = os.path.splitext(parsed.path)
        if ext and len(ext) <= 5:
            extension = ext
        else:
            # Try from content-type
            ctype = resp.headers.get('content-type', '')
            if 'png' in ctype:
                extension = '.png'
            else:
                extension = '.jpg'

        filename = f"{uuid4().hex}{extension}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        with open(save_path, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
        return filename
    except Exception:
        return None


# Configuración MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '159357'
app.config['MYSQL_DB'] = 'fletes_mudanzas'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def ensure_inventario_has_image_column():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=%s AND TABLE_NAME='inventario' AND COLUMN_NAME='imagen'", (app.config['MYSQL_DB'],))
    exists = cur.fetchone()
    if not exists:
        try:
            cur.execute("ALTER TABLE inventario ADD COLUMN imagen VARCHAR(255) NULL")
            mysql.connection.commit()
        except Exception:
            # If alter fails (permissions or different schema), ignore and continue
            pass
    cur.close()

# Ensure schema has imagen column if possible
try:
    ensure_inventario_has_image_column()
except Exception:
    pass

def ensure_inventario_imagenes_table():
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventario_imagenes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                inventario_id INT NOT NULL,
                filename VARCHAR(255) NOT NULL,
                orden INT DEFAULT 0,
                FOREIGN KEY (inventario_id) REFERENCES inventario(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        mysql.connection.commit()
    except Exception:
        pass
    cur.close()

try:
    ensure_inventario_imagenes_table()
except Exception:
    pass

def compress_and_save_image(file_storage, filename, max_size=1600, quality=78):
    """Compress and save image using Pillow. Returns final filename."""
    try:
        img = Image.open(file_storage)
    except Exception:
        return None

    # Convert to RGB if needed (for JPEG)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Resize if larger than max_size in either dimension
    w, h = img.size
    if max(w, h) > max_size:
        scale = max_size / float(max(w, h))
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # Choose format by extension
    ext = os.path.splitext(filename)[1].lower()
    try:
        if ext in ['.jpg', '.jpeg']:
            img.save(save_path, 'JPEG', quality=quality, optimize=True)
        else:
            # For PNG/GIF keep defaults but attempt to optimize
            img.save(save_path)
    except Exception:
        try:
            img.save(save_path)
        except Exception:
            return None

    return filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validar_telefono(telefono):
    patron = r'^\+?\d{7,15}$'
    return bool(re.match(patron, telefono))

def validar_password(password):
    """Valida que la contraseña tenga mínimo 8 caracteres, 1 mayúscula, 1 minúscula y 1 número"""
    if len(password) < 8:
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        domicilio = request.form['domicilio']
        telefono = request.form['telefono']
        email = request.form['email']
        password_raw = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validar teléfono antes de crear usuario
        if not validar_telefono(telefono):
            flash('El número de teléfono no es válido. Solo números, mínimo 7 dígitos y máximo 15.', 'danger')
            return redirect(url_for('register'))
        
        # Validar contraseña
        if not validar_password(password_raw):
            flash('La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula y un número.', 'danger')
            return redirect(url_for('register'))
        
        # Validar que las contraseñas coincidan
        if password_raw != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('register'))
        
        password = generate_password_hash(password_raw)

        # Crear token seguro
        token = serializer.dumps(email)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuarios (nombre, domicilio, telefono, email, password, activo, token_activacion)
            VALUES (%s, %s, %s, %s, %s, 0, %s)
        """, (nombre, domicilio, telefono, email, password, token))
        mysql.connection.commit()
        cur.close()

        # Enviar correo (solo si está habilitado en configuración)
        link_activacion = url_for('activar_cuenta', token=token, _external=True)

        msg = Message('Activa tu cuenta', recipients=[email])
        msg.body = f"Hola {nombre}, activa tu cuenta haciendo clic aquí:\n{link_activacion}"

        if app.config.get('SEND_EMAILS'):
            mail.send(msg)


        flash('Registro exitoso. Revisa tu correo para activar tu cuenta.', 'info')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/activar/<token>')
def activar_cuenta(token):
    try:
        email = serializer.loads(token, max_age=3600)  # 1 hora
    except:
        flash('El enlace de activación ha expirado o es inválido.', 'danger')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("UPDATE usuarios SET activo=1 WHERE email=%s", [email])
    mysql.connection.commit()
    cur.close()

    flash('Cuenta activada correctamente. Ya puedes iniciar sesión.', 'success')
    return redirect(url_for('login'))




@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE email = %s', [email])
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user['password'], password):
            session['nombre'] = user['nombre']
            session['email'] = user['email']
            return redirect(url_for('index'))
        else:
            flash('Credenciales inválidas.', 'danger')
    return render_template('login.html')


@app.route('/login/facebook')
def login_facebook():
    redirect_uri = url_for('facebook_callback', _external=True)
    return facebook.authorize_redirect(redirect_uri)


@app.route('/auth/facebook/callback')
def facebook_callback():
    try:
        token = facebook.authorize_access_token()
        resp = facebook.get('me?fields=id,name,email,picture{url}')
        user_info = resp.json()

        nombre = user_info.get('name', 'Usuario Facebook')
        email = user_info.get('email')
        foto_url = None
        
        # Obtener URL de la foto
        try:
            foto_url = user_info.get('picture', {}).get('data', {}).get('url')
        except Exception:
            pass

        if not email:
            flash("Facebook no proporcionó tu correo electrónico. Verifica los permisos de la aplicación.", "danger")
            return redirect(url_for('login'))

        # Descargar y guardar foto si existe
        foto_final = None
        if foto_url:
            foto_final = download_and_save_image(foto_url)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email=%s", [email])
        user = cur.fetchone()

        if not user:
            # Crear nuevo usuario
            cur.execute("""
                INSERT INTO usuarios (nombre, email, foto, activo, domicilio, telefono, password)
                VALUES (%s, %s, %s, 1, 'No especificado', '0000000000', '')
            """, (nombre, email, foto_final or 'default.png'))
            mysql.connection.commit()
        elif foto_final:
            # Actualizar foto si se descargó una nueva
            cur.execute("UPDATE usuarios SET foto=%s WHERE email=%s", (foto_final, email))
            mysql.connection.commit()

        # Iniciar sesión
        session['email'] = email
        session['nombre'] = nombre
        if foto_final:
            session['foto'] = foto_final
        elif user and user.get('foto'):
            session['foto'] = user['foto']

        cur.close()
        flash(f"¡Bienvenido {nombre}! Sesión iniciada con Facebook.", "success")
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f"Error al iniciar sesión con Facebook: {str(e)}", "danger")
        return redirect(url_for('login'))


@app.route('/login/google')
def login_google():
    redirect_uri = url_for('google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/auth/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
        # Obtener información del usuario desde Google
        resp = google.get('userinfo')
        user_info = resp.json()

        nombre = user_info.get('name') or user_info.get('given_name', 'Usuario Google')
        email = user_info.get('email')
        foto_url = user_info.get('picture')

        if not email:
            flash('Google no proporcionó tu correo electrónico. Verifica los permisos.', 'danger')
            return redirect(url_for('login'))

        # Descargar y guardar foto si existe
        foto_final = None
        if foto_url:
            foto_final = download_and_save_image(foto_url)

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE email=%s', [email])
        user = cur.fetchone()

        if not user:
            # Crear nuevo usuario
            cur.execute("""
                INSERT INTO usuarios (nombre, email, foto, activo, domicilio, telefono, password)
                VALUES (%s, %s, %s, 1, 'No especificado', '0000000000', '')
            """, (nombre, email, foto_final or 'default.png'))
            mysql.connection.commit()
        elif foto_final:
            # Actualizar foto si se descargó una nueva
            cur.execute('UPDATE usuarios SET foto=%s WHERE email=%s', (foto_final, email))
            mysql.connection.commit()

        # Iniciar sesión
        session['email'] = email
        session['nombre'] = nombre
        if foto_final:
            session['foto'] = foto_final
        elif user and user.get('foto'):
            session['foto'] = user['foto']

        cur.close()
        flash(f'¡Bienvenido {nombre}! Sesión iniciada con Google.', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Error al iniciar sesión con Google: {str(e)}', 'danger')
        return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM inventario WHERE email = %s', [session['email']])
    items = cur.fetchall()
    # For each item, fetch first image (if any)
    for item in items:
        try:
            cur.execute('SELECT filename FROM inventario_imagenes WHERE inventario_id=%s ORDER BY orden LIMIT 1', [item['id']])
            img = cur.fetchone()
            item['imagen'] = img['filename'] if img else None
        except Exception:
            item['imagen'] = item.get('imagen')  # fallback to columna imagen

    cur.close()
    return render_template('dashboard.html', nombre=session['nombre'], items=items)
    # Si quieres integrar login con Facebook usa Authlib/Flask-Dance.
    # El bloque de ejemplo de Facebook OAuth fue removido para evitar errores
    # por la ausencia de la variable `oauth`. Puedo reañadirlo si lo deseas.

@app.route('/mi_informacion', methods=['GET', 'POST'])
def mi_informacion():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nuevo_nombre = request.form['nombre']
        nuevo_domicilio = request.form['domicilio']
        nuevo_telefono = request.form['telefono']
        nuevo_email = request.form['email']

        if not validar_telefono(nuevo_telefono):
            flash('El número de teléfono no es válido.', 'danger')
            return redirect(url_for('mi_informacion'))


        # Si se subió foto
        file = request.files.get('foto')
        foto_final = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(foto_path)
            foto_final = filename

        cur = mysql.connection.cursor()

        if foto_final:
            cur.execute("""
                UPDATE usuarios 
                SET nombre=%s, domicilio=%s, telefono=%s, email=%s, foto=%s
                WHERE email=%s
            """, (nuevo_nombre, nuevo_domicilio, nuevo_telefono, nuevo_email, foto_final, session['email']))
            session['foto'] = foto_final
        else:
            cur.execute("""
                UPDATE usuarios 
                SET nombre=%s, domicilio=%s, telefono=%s, email=%s
                WHERE email=%s
            """, (nuevo_nombre, nuevo_domicilio, nuevo_telefono, nuevo_email, session['email']))

        mysql.connection.commit()
        cur.close()

        session['nombre'] = nuevo_nombre
        session['email'] = nuevo_email

        flash('Información actualizada correctamente.', 'success')
        return redirect(url_for('mi_informacion'))
    
    # GET: Mostrar información actual del usuario
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuarios WHERE email = %s', [session['email']])
    usuario = cur.fetchone()
    cur.close()
    
    return render_template('mi_informacion.html', usuario=usuario)


@app.route('/reenviar_activacion', methods=['POST'])
def reenviar_activacion():
    if 'email' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuarios WHERE email = %s', [session['email']])
    user = cur.fetchone()

    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('mi_informacion'))

    if user.get('activo') == 1:
        flash('La cuenta ya está activada.', 'info')
        cur.close()
        return redirect(url_for('mi_informacion'))

    # Crear nuevo token y actualizar
    token = serializer.dumps(user['email'])
    cur.execute('UPDATE usuarios SET token_activacion = %s WHERE email = %s', (token, user['email']))
    mysql.connection.commit()

    link_activacion = url_for('activar_cuenta', token=token, _external=True)
    msg = Message('Activa tu cuenta', recipients=[user['email']])
    msg.body = f"Hola {user.get('nombre', '')}, activa tu cuenta haciendo clic aquí:\n{link_activacion}"

    if app.config.get('SEND_EMAILS'):
        mail.send(msg)

    cur.close()
    flash('Correo de activación reenviado (si está habilitado el envío).', 'info')
    return redirect(url_for('mi_informacion'))



@app.route('/cambiar_password', methods=['GET', 'POST'])
def cambiar_password():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        password_actual = request.form['password_actual']
        password_nueva = request.form['password_nueva']
        password_confirmar = request.form['password_confirmar']

        # Validar que ambas coincidan
        if password_nueva != password_confirmar:
            flash('La nueva contraseña no coincide con la confirmación.', 'danger')
            return redirect(url_for('cambiar_password'))

        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM usuarios WHERE email = %s", [session['email']])
        user = cur.fetchone()

        # Validar contraseña actual
        if not check_password_hash(user['password'], password_actual):
            flash('La contraseña actual es incorrecta.', 'danger')
            return redirect(url_for('cambiar_password'))

        # Guardar contraseña nueva
        nueva_hash = generate_password_hash(password_nueva)
        cur.execute("UPDATE usuarios SET password = %s WHERE email = %s", (nueva_hash, session['email']))
        mysql.connection.commit()
        cur.close()

        flash('Contraseña cambiada con éxito.', 'success')
        return redirect(url_for('mi_informacion'))

    return render_template('cambiar_password.html')


@app.route('/agregar_item', methods=['POST'])
def agregar_item():
    if 'email' not in session:
        return redirect(url_for('login'))

    nombre_item = request.form['nombre_item']
    cantidad = request.form['cantidad']
    # Handle uploaded images (multiple)
    files = request.files.getlist('imagenes') or request.files.getlist('imagen')
    imagen_filenames = []

    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO inventario (email, nombre_item, cantidad) VALUES (%s,%s,%s)',
                (session['email'], nombre_item, cantidad))
    mysql.connection.commit()
    # get last insert id
    cur.execute('SELECT LAST_INSERT_ID() as id')
    row = cur.fetchone()
    new_id = row['id'] if row else None

    # save uploaded files
    order = 0
    for f in files:
        if f and f.filename and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            filename = f"{uuid4().hex}_{filename}"
            saved = compress_and_save_image(f, filename)
            if saved and new_id:
                try:
                    cur.execute('INSERT INTO inventario_imagenes (inventario_id, filename, orden) VALUES (%s,%s,%s)', (new_id, saved, order))
                    order += 1
                except Exception:
                    pass
    mysql.connection.commit()
    cur.close()
    
    flash('Item agregado exitosamente.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/editar_item/<int:id>', methods=['GET', 'POST'])
def editar_item(id):
    if 'email' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nuevo_nombre = request.form['nombre_item']
        nueva_cantidad = request.form['cantidad']
        # Handle uploaded images for edit (multiple)
        files = request.files.getlist('imagenes') or request.files.getlist('imagen')
        imagen_filenames = []
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                filename = f"{uuid4().hex}_{filename}"
                saved = compress_and_save_image(f, filename)
                if saved:
                    imagen_filenames.append(saved)
        cur.execute("""
            UPDATE inventario 
            SET nombre_item = %s, cantidad = %s
            WHERE id = %s AND email = %s
        """, (nuevo_nombre, nueva_cantidad, id, session['email']))
        # insert new images if any
        order = 0
        try:
            cur.execute('SELECT IFNULL(MAX(orden), -1) as maxorden FROM inventario_imagenes WHERE inventario_id=%s', (id,))
            r = cur.fetchone()
            order = (r['maxorden'] + 1) if r and r.get('maxorden') is not None else 0
        except Exception:
            order = 0
        for saved in imagen_filenames:
            try:
                cur.execute('INSERT INTO inventario_imagenes (inventario_id, filename, orden) VALUES (%s,%s,%s)', (id, saved, order))
                order += 1
            except Exception:
                pass
        # Handle deletions requested by user
        delete_ids = request.form.getlist('delete_imagenes')
        for did in delete_ids:
            try:
                cur.execute('SELECT filename FROM inventario_imagenes WHERE id=%s AND inventario_id=%s', (did, id))
                row = cur.fetchone()
                if row:
                    fname = row.get('filename')
                    # delete file from disk
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                    except Exception:
                        pass
                    cur.execute('DELETE FROM inventario_imagenes WHERE id=%s AND inventario_id=%s', (did, id))
            except Exception:
                pass
        mysql.connection.commit()
        cur.close()
        flash('Item actualizado correctamente.', 'success')
        return redirect(url_for('dashboard'))

    # Si el método es GET, cargamos el item a editar
    cur.execute('SELECT * FROM inventario WHERE id = %s AND email = %s', (id, session['email']))
    item = cur.fetchone()
    # fetch images for this item
    try:
        cur.execute('SELECT * FROM inventario_imagenes WHERE inventario_id=%s ORDER BY orden', (id,))
        images = cur.fetchall()
        item['imagenes'] = images
    except Exception:
        item['imagenes'] = []
    cur.close()
    return render_template('editar_item.html', item=item)


@app.route('/eliminar_item/<int:id>', methods=['POST'])
def eliminar_item(id):
    if 'email' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM inventario WHERE id = %s AND email = %s', (id, session['email']))
    mysql.connection.commit()
    cur.close()
    
    flash('Item eliminado correctamente.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('index'))


@app.route('/galeria')
def galeria():
    if 'email' not in session:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    # select images for this user's inventory
    cur.execute("""
        SELECT ii.id as img_id, ii.filename, inv.nombre_item, inv.id as inventario_id
        FROM inventario_imagenes ii
        JOIN inventario inv ON inv.id = ii.inventario_id
        WHERE inv.email = %s
        ORDER BY ii.orden ASC
    """, (session['email'],))
    images = cur.fetchall()
    cur.close()
    return render_template('galeria.html', images=images)


@app.route('/acerca')
def acerca():
    return render_template('acerca.html')


@app.route('/ayuda')
def ayuda():
    return render_template('ayuda.html')


@app.route('/fletes')
def fletes():
    return render_template('fletes.html')


@app.route('/mudanzas')
def mudanzas():
    return render_template('mudanzas.html')


@app.route('/unidades')
def unidades():
    return render_template('unidades.html')


@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Endpoint para subir imágenes vía AJAX. Parámetros: file (archivo), inventario_id (opcional)."""
    if 'email' not in session:
        return jsonify({'ok': False, 'error': 'no_session'}), 401

    file = request.files.get('file') or (request.files.getlist('files')[0] if request.files.getlist('files') else None)
    inventario_id = request.form.get('inventario_id') or request.args.get('inventario_id')

    if not file or not file.filename:
        return jsonify({'ok': False, 'error': 'no_file_provided'}), 400

    if not allowed_file(file.filename):
        return jsonify({'ok': False, 'error': 'invalid_extension'}), 400

    orig = secure_filename(file.filename)
    filename = f"{uuid4().hex}_{orig}"
    saved = compress_and_save_image(file, filename)
    if not saved:
        return jsonify({'ok': False, 'error': 'save_failed'}), 500

    # If inventario_id provided, register in DB immediately
    if inventario_id:
        try:
            cur = mysql.connection.cursor()
            # compute next orden
            cur.execute('SELECT IFNULL(MAX(orden), -1) as maxorden FROM inventario_imagenes WHERE inventario_id=%s', (inventario_id,))
            r = cur.fetchone()
            order = (r['maxorden'] + 1) if r and r.get('maxorden') is not None else 0
            cur.execute('INSERT INTO inventario_imagenes (inventario_id, filename, orden) VALUES (%s,%s,%s)', (inventario_id, saved, order))
            mysql.connection.commit()
            cur.close()
        except Exception:
            # swallow DB errors but keep file
            pass

    return jsonify({'ok': True, 'filename': saved, 'url': url_for('static', filename='uploads/' + saved)})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)


