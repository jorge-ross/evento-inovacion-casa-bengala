from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import pymysql
import os 
from urllib.parse import urlparse 
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)

ALLOWED_ORIGINS = [
    'https://evento-inovacion-casa-bengala.vercel.app',
    'https://web-production-59d1b.up.railway.app',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:3000'
]

CORS(app, 
     resources={r"/api/*": {"origins": ALLOWED_ORIGINS}}, 
     methods=['GET', 'POST'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization']
) 

def get_db_config():
    mysql_url = os.getenv('MYSQL_URL')
    
    if mysql_url:
        url = urlparse(mysql_url)
        database_name = url.path.lstrip('/') if url.path else os.getenv('MYSQL_DATABASE', 'event_db')
        
        return {
            'user': url.username, 
            'password': url.password,
            'host': url.hostname, 
            'port': url.port if url.port else 3306,
            'database': database_name,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
    else:
        return {
            'user': os.getenv('MYSQL_USER', 'root'), 
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'host': os.getenv('MYSQL_HOST', '127.0.0.1'), 
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'database': os.getenv('MYSQL_DATABASE', 'event_db'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }


def get_db_connection():
    DB_CONFIG = get_db_config()
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception:
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
        check_query = "SELECT id FROM registrations WHERE email = %s"
        cursor.execute(check_query, (email,))
        if cursor.fetchone():
            return jsonify({'message': 'Error: Este correo ya se encuentra registrado.'}), 409

    except Exception:
        return jsonify({'message': 'Error interno al verificar el registro.'}), 500

    try:
        insert_query = """
            INSERT INTO registrations (name, email, message) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (name, email, message))
        conn.commit()
        
        return jsonify({'message': 'Registro exitoso!'}), 200

    except Exception:
        conn.rollback()
        return jsonify({'message': 'Error interno al guardar el registro.'}), 500
    
    finally:
        if cursor: cursor.close()
        if conn and conn.open: conn.close()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000)) 
    app.run(host='0.0.0.0', port=port, debug=True)