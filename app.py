from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Configuración de la base de datos (reemplaza con tus propios datos)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
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
    query = "SELECT username FROM users WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()
    cursor.close()

    if user:
        return jsonify({'username': user[0]})  # Cambiado a devolver el nombre de usuario
    else:
        return jsonify({'error': 'Credenciales incorrectas. Inténtalo de nuevo.', 'email': email, 'password': password})

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

    return jsonify({'message': 'Usuario registrado exitosamente'})

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

# Asegúrate de incluir esta condición para que solo se ejecute en el entorno local
if __name__ == '__main__':
    # Para Heroku, usa el puerto proporcionado por la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    # Quita el parámetro host para que Flask detecte automáticamente el host
    app.run(port=port)
