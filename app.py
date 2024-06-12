import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import mysql.connector

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Definición de variables de entorno
db_host = 'localhost'
db_user = 'root'
db_password = 'Utx$abeCCrUDnJC)'
db_database = 'terretaFest'

# Configuración de la base de datos
db_config = {
    'host': db_host,
    'user': db_user,
    'password': db_password,
    'database': db_database
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
            'Nombre_del_Evento': evento[1],
            'Ubicacion': evento[2],
            'Grupo_de_Musica': evento[3],
            'N_de_Entradas': evento[4],
            'Precio': evento[5],
            'Imagen': evento[6],
            'Fecha': evento[7],
            'Informacion': evento[8],
            'Coordenadas': {
                'latitud': evento[9],
                'longitud': evento[10]
            }
        })

    return jsonify(eventos_list)

@app.route('/enviar-correo', methods=['POST'])
def enviar_correo():
    data = request.json  # Obtener datos JSON del cuerpo de la solicitud
    nombre = data.get('nombre')
    correo_usuario = data.get('correo')  # Correo electrónico proporcionado por el usuario
    asunto = data.get('asunto')
    mensaje = data.get('mensaje')

    # Configuración del servidor SMTP (reemplaza con tus propios datos)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'info.terretafest@gmail.com'  # Tu dirección de correo electrónico
    smtp_password = 'sdqi tlqp rrqr wqyu'  # Tu contraseña de correo electrónico

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
