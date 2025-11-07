from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import pymysql
import os
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

def get_db_config():
    mysql_url = os.getenv('MYSQL_URL')
    
    if mysql_url:
        print("Usando MYSQL_URL de Railway para la configuración.")
        url = urlparse(mysql_url)
        database_name = url.path.strip('/')
        
        return {
            'user': url.username, 
            'password': url.password,
            'host': url.hostname, 
            'port': url.port,
            'database': database_name,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
    else:
        print("Usando variables de entorno separadas o valores locales por defecto.")
        return {
            'user': os.getenv('MYSQL_USER', 'root'), 
            'password': os.getenv('MYSQL_PASSWORD', 'tu_password_local'),
            'host': os.getenv('MYSQL_HOST', '127.0.0.1'), 
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'database': os.getenv('MYSQL_DATABASE', 'event_db'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

def get_db_connection():
    DB_CONFIG = get_db_config()
    # print("Intentando conectar a la base de datos...")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("Conexión a DB exitosa.")
        return conn
    except Exception as err:
        print(f"Error al conectar a MySQL: {err}")
        return None

def is_valid_email(email):
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(regex, email)

@app.route('/', methods=['GET'])
def home():
    # Endpoint para verificar que el servidor está funcionando
    return jsonify({'message': 'Digital Future Summit API Backend está funcionando correctamente.'}), 200


# Endpoint de registro
@app.route('/api/register', methods=['POST'])
def register_user():
    
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message', '')

    print(f"Solicitud de registro recibida: Nombre='{name}', Email='{email}'")

    # Validaciones
    if not name or not email:
        return jsonify({'message': 'Error: Nombre y Email son campos obligatorios.'}), 400
    
    if not is_valid_email(email):
        return jsonify({'message': 'Error: Formato de correo electrónico inválido.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Error interno: No se pudo conectar a la base de datos.'}), 500

    cursor = conn.cursor()

    # Verificar si el email ya existe
    try:
        check_query = "SELECT id FROM registrations WHERE email = %s"
        cursor.execute(check_query, (email,))
        if cursor.fetchone():
            conn.close()
            print(f"Registro fallido: El email {email} ya existe.")
            return jsonify({'message': 'Error: Este correo ya se encuentra registrado.'}), 409

    except Exception as err:
        conn.close()
        print(f"Error de verificación en DB: {err}")
        return jsonify({'message': 'Error al verificar el registro.'}), 500

    # Insertar el nuevo registro
    try:
        insert_query = """
            INSERT INTO registrations (name, email, message) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (name, email, message))
        conn.commit()
        
        print(f"Registro exitoso para el email: {email}")
        return jsonify({'message': 'Registro exitoso!'}), 200

    except Exception as err:
        conn.rollback()
        print(f"Error de inserción en DB: {err}")
        return jsonify({'message': 'Error interno al guardar el registro.'}), 500
    
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000)) 
    print(f"Iniciando servidor Flask en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

