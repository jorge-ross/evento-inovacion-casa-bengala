import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import pymysql
import pymysql.cursors 
from urllib.parse import urlparse 
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_config():
    mysql_url = os.getenv('MYSQL_URL')
    
    if mysql_url:
        print("Usando MYSQL_URL de Railway para la configuración.")
        url = urlparse(mysql_url)
        database_name = url.path.lstrip('/') if url.path else os.getenv('MYSQL_DATABASE', 'event_db')
        
        config = {
            'user': url.username, 
            'password': url.password,
            'host': url.hostname, 
            'port': url.port if url.port else 3306,
            'database': database_name,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        
    else:
        print("MYSQL_URL no está configurada. Usando variables de entorno separadas.")
        config = {
            'user': os.getenv('MYSQL_USER', 'root'), 
            'password': os.getenv('MYSQL_PASSWORD', 'your_local_password'),
            'host': os.getenv('MYSQL_HOST', '127.0.0.1'), 
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'database': os.getenv('MYSQL_DATABASE', 'event_db'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    debug_config = config.copy()
    debug_config['password'] = '******'
    print(f"DEBUG DB CONFIG (sin password): {json.dumps(debug_config)}")
    
    return config


def get_db_connection():
    DB_CONFIG = get_db_config()
    print("Intentando conectar a la base de datos...")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("Conexión a DB exitosa.")
        return conn
    except Exception as err:
        error_message = f"Error al conectar a MySQL. Detalles del error: {err}"
        print(error_message)
        return None

def is_valid_email(email):
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(regex, email)

@app.route('/', methods=['GET'])
def home():
    conn = get_db_connection()
    db_status = "Conectado a DB" if conn else "ERROR de Conexión a DB"
    if conn: conn.close()
    return jsonify({'message': f'Digital Future Summit API Backend está funcionando. Estado de DB: {db_status}'}), 200

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message', '')

    print(f"Solicitud de registro recibida: Nombre='{name}', Email='{email}'")

    if not name or not email:
        return jsonify({'message': 'Error: Nombre y Email son campos obligatorios.'}), 400
    
    if not is_valid_email(email):
        return jsonify({'message': 'Error: Formato de correo electrónico inválido.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Error interno: No se pudo conectar a la base de datos. Por favor, verifica tu servidor MySQL y configuración.'}), 500

    cursor = conn.cursor()

    try:
        check_query = "SELECT id FROM registrations WHERE email = %s"
        cursor.execute(check_query, (email,))
        if cursor.fetchone():
            print(f"Registro fallido: El email {email} ya existe.")
            return jsonify({'message': 'Error: Este correo ya se encuentra registrado.'}), 409

    except Exception as err:
        print(f"Error de verificación en DB: {err}")
        return jsonify({'message': 'Error interno al verificar el registro.'}), 500

    try:
        insert_query = """
            INSERT INTO registrations (name, email, message) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (name, email, message))
        conn.commit()
        
        print(f"Registro exitoso para el email: {email}")
        return jsonify({'message': 'Registro completado con éxito!'}), 201

    except Exception as err:
        conn.rollback()
        print(f"Error de inserción en DB: {err}")
        return jsonify({'message': 'Error interno al guardar el registro.'}), 500
    
    finally:
        if cursor: cursor.close()
        if conn and conn.open: conn.close()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000)) 
    print(f"Iniciando servidor Flask en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)