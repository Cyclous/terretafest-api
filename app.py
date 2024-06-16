import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde un archivo .env

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

db_config = {
    'host': 'localhost',  # Cambiar si es necesario
    'user': 'root',       # Cambiar si es necesario
    'password': 'admin',  # Cambiar si es necesario
    'database': 'terretaFest'
}

# Conexión a la base de datos
db_conn = mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    # Verificación de credenciales en la base de datos
    cursor = db_conn.cursor()
    query = "SELECT username, role_id FROM users WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return jsonify({'username': user[0], 'role_id': user[1]})  # Devolver nombre de usuario y role_id
    else:
        return jsonify({'error': 'Credenciales incorrectas. Inténtalo de nuevo.'})

@app.route('/register', methods=['POST'])
def register():
    data = request.json  # Obtener datos JSON del cuerpo de la solicitud
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirmPassword')

    # Verificar si el usuario ya existe en la base de datos (implementación depende de tu lógica)

    # Guardar el nuevo usuario en la base de datos
    cursor = db_conn.cursor()
    query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, email, password))
    db_conn.commit()
    cursor.close()

    return jsonify({'message': 'Usuari registrat amb èxit'})

@app.route('/productos', methods=['GET'])
def get_productos():
    cursor = db_conn.cursor()
    query = "SELECT * FROM productos"
    cursor.execute(query)
    productos = cursor.fetchall()
    cursor.close()

    productos_list = []
    for producto in productos:
        productos_list.append({
            'id_producto': producto[0],
            'nombre': producto[1],
            'descripcion': producto[2],
            'precio': producto[3],
            'stock': producto[4],
            'tipo': producto[5],
            'talla': producto[6]
        })

    return jsonify(productos_list)

@app.route('/eventos', methods=['GET'])
def get_eventos():
    cursor = db_conn.cursor()
    query = "SELECT * FROM eventos"
    cursor.execute(query)
    eventos = cursor.fetchall()
    cursor.close()

    eventos_list = []
    for evento in eventos:
        eventos_list.append({
            'id': evento[0],
            'nombreDelEvento': evento[1],
            'ubicacion': evento[2],
            'grupoDeMusica': evento[3],
            'numeroDeEntradas': evento[4],
            'precio': evento[5],
            'imagen': evento[6],
            'fecha': evento[7],
            'informacion': evento[8],
            'coordenadas': {
                'latitud': evento[9],
                'longitud': evento[10]
            }
        })

    return jsonify(eventos_list)

@app.route('/eventos/<int:evento_id>', methods=['DELETE'])
def delete_evento(evento_id):
    cursor = db_conn.cursor()

    # Primero comprobamos si el evento existe
    cursor.execute("SELECT * FROM eventos WHERE id = %s", (evento_id,))
    evento = cursor.fetchone()

    if evento is None:
        # Si el evento no existe, retornamos un 404
        cursor.close()
        abort(404, description="Evento no encontrado")

    # Si el evento existe, procedemos a eliminarlo
    cursor.execute("DELETE FROM eventos WHERE id = %s", (evento_id,))
    db_conn.commit()
    cursor.close()

    return '', 204

@app.route('/eventos/<int:evento_id>', methods=['PUT'])
def update_evento(evento_id):
    data = request.json
    nombre_del_evento = data.get('nombreDelEvento')
    ubicacion = data.get('ubicacion')
    grupo_de_musica = data.get('grupoDeMusica')
    n_de_entradas = data.get('numeroDeEntradas')
    precio = data.get('precio')
    fecha = data.get('fecha')

    if not all([nombre_del_evento, ubicacion, grupo_de_musica]):
        abort(400, description="Faltan campos obligatorios")

    cursor = db_conn.cursor()

    cursor.execute("SELECT * FROM eventos WHERE id = %s", (evento_id,))
    evento = cursor.fetchone()

    if evento is None:
        cursor.close()
        abort(404, description="Evento no encontrado")

    query = """
    UPDATE eventos
    SET nombreDelEvento = %s, ubicacion = %s, grupoDeMusica = %s, numeroDeEntradas = %s, precio = %s, fecha = %s
    WHERE id = %s
    """
    cursor.execute(query, (nombre_del_evento, ubicacion, grupo_de_musica, n_de_entradas, precio, fecha, evento_id))
    db_conn.commit()
    cursor.close()

    return jsonify({'message': 'Evento actualizado exitosamente'})

@app.route('/eventos', methods=['POST'])
def add_evento():
    data = request.json  # Obtener datos JSON del cuerpo de la solicitud

    # Extraer los campos del objeto Event
    nombre_del_evento = data.get('nombreDelEvento')
    ubicacion = data.get('ubicacion')
    grupo_de_musica = data.get('grupoDeMusica')
    n_de_entradas = data.get('numeroDeEntradas')
    precio = data.get('precio')
    imagen = 'https://t3.ftcdn.net/jpg/05/03/58/28/360_F_503582859_7SJMOrd2Xf5ujdBjrBCam7ngr9wc84vH.jpg'
    fecha = data.get('fecha')
    informacion = data.get('informacion')
    latitud = data.get('latitud')
    longitud = data.get('longitud')

    # Verificar que los campos obligatorios están presentes
    if not all([nombre_del_evento, ubicacion, grupo_de_musica]):
        abort(400, description="Faltan campos obligatorios")

    
    cursor = db_conn.cursor()
    query = """
    INSERT INTO eventos (nombreDelEvento, ubicacion, grupoDeMusica, numeroDeEntradas, precio, imagen, fecha, informacion, latitud, longitud)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nombre_del_evento, ubicacion, grupo_de_musica, n_de_entradas, precio, imagen, fecha, informacion, latitud, longitud))
    db_conn.commit()
    cursor.close()
    

    return jsonify({'message': 'Evento creado exitosamente'}), 201
    
@app.route('/enviar-correo', methods=['POST'])
def enviar_correo():
    data = request.json  # Obtener datos JSON del cuerpo de la solicitud
    nombre = data.get('nombre')
    correo_usuario = data.get('correo')  # Correo electrónico proporcionado por el usuario
    asunto = data.get('asunto')
    mensaje = data.get('mensaje')

    # Configuración del servidor SMTP (reemplaza con tus propios datos)
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_user = os.getenv('SMTP_USER')  # Tu dirección de correo electrónico
    smtp_password = os.getenv('SMTP_PASSWORD')  # Tu contraseña de correo electrónico

    # Construir el mensaje de correo electrónico
    msg = MIMEMultipart()
    msg['From'] = smtp_user  # El remitente es info.terretafest
    msg['To'] = 'terretafestt@gmail.com'  # El destinatario es tu dirección de correo de administración
    msg['Subject'] = asunto
    # Contenido del correo con estilo
    body = f"""
    <html>
        <head></head>
        <body>
            <p>Salutacions Terretafest,</p>
            <p>Has rebut un nou missatge de {nombre} ({correo_usuario}):</p>
            <p>{mensaje}</p>
            <p>Salutacions,</p>
            <p>Equipo de Terretafest</p>
        </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    # Iniciar sesión en el servidor SMTP
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)

    # Enviar correo electrónico
    server.sendmail(smtp_user, 'terretafestt@gmail.com', msg.as_string())

    # Cerrar sesión en el servidor SMTP
    server.quit()

    return jsonify({'message': 'Correu enviat amb èxit'})

# Ruta para servir archivos estáticos desde el directorio pki-validation
@app.route('/.well-known/pki-validation/<filename>')
def serve_validation_file(filename):
    directory = os.path.join(app.root_path, 'well-known', 'pki-validation')
    return send_from_directory(directory, filename)

@app.route('/health')
def health_check():
    return 'Healthy', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
