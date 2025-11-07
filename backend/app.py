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
    db_host = os.environ.get('MYSQLHOST') or os.environ.get('MYSQL_HOST')
    db_user = os.environ.get('MYSQLUSER') or os.environ.get('MYSQL_USER')
    db_pass = os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_PASSWORD')
    db_name = os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE')
    db_port = os.environ.get('MYSQLPORT') or os.environ.get('MYSQL_PORT')

    if db_host and db_user and db_name:
        config = {
            'user': db_user, 
            'password': db_pass,
            'host': db_host if db_host != 'localhost' else 'mysql.railway.internal', 
            'port': int(db_port or 3306),
            'database': db_name,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        print(f"DEBUG DB Config (Railway Individual): Host={config['host']}, DB={config['database']}")
        return config

    mysql_url = os.environ.get('MYSQL_URL')
    if mysql_url:
        url = urlparse(mysql_url)
        db_host = url.hostname if url.hostname else 'mysql.railway.internal'

        config = {
            'user': url.username, 
            'password': url.password,
            'host': db_host, 
            'port': url.port if url.port else 3306,
            'database': url.path.lstrip('/'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        print(f"DEBUG DB Config (Railway URL): Host={config['host']}, DB={url.path.lstrip('/')}")
        return config

    else:
        config = {
            'user': os.getenv('MYSQL_USER', 'root'), 
            'password': os.getenv('MYSQL_PASSWORD', 'your_local_password'),
            'host': os.getenv('MYSQL_HOST', '127.0.0.1'), 
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'database': os.getenv('MYSQL_DATABASE', 'event_db'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        print(f"DEBUG DB Config (Local Fallback): Host={config['host']}, DB={config['database']}")
        return config

def get_db_connection():
    DB_CONFIG = get_db_config()
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("Conexión a DB exitosa.")
        return conn
    except Exception as err:
        print(f"!!! CRITICAL DB CONNECTION ERROR: {err}")
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

    if not name or not email:
        return jsonify({'message': 'Error: Nombre y Email son campos obligatorios.'}), 400
    
    if not is_valid_email(email):
        return jsonify({'message': 'Error: Formato de correo electrónico inválido.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'message': 'Error interno: No se pudo conectar a la base de datos. Por favor, verifica tu servidor MySQL y configuración.'}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        check_query = "SELECT id FROM registrations WHERE email = %s"
        cursor.execute(check_query, (email,))
        if cursor.fetchone():
            return jsonify({'message': 'Error: Este correo ya se encuentra registrado.'}), 409

    except Exception as err:
        print(f"Error durante verificación/creación de tabla: {err}")
        return jsonify({'message': 'Error interno al verificar/crear el registro.'}), 500

    try:
        insert_query = """
            INSERT INTO registrations (name, email, message) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (name, email, message))
        conn.commit()
        
        return jsonify({'message': 'Registro completado con éxito!'}), 201

    except Exception as err:
        conn.rollback()
        return jsonify({'message': 'Error interno al guardar el registro.'}), 500
    
    finally:
        if cursor: cursor.close()
        if conn and conn.open: conn.close()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port, debug=False)