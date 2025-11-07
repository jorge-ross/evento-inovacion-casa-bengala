import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql.cursors
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection_params():
    mysql_url = os.environ.get('MYSQL_URL')

    if not mysql_url:
        logging.error("La variable de entorno MYSQL_URL no está configurada.")
        return {
            'host': '127.0.0.1', 
            'user': 'root', 
            'password': '', 
            'db': 'testdb', 
            'charset': 'utf8mb4'
        }

    try:
        url = urlparse(mysql_url)
        params = {
            'host': url.hostname,
            'user': url.username,
            'password': url.password,
            'db': url.path[1:],
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }
        if url.port:
            params['port'] = url.port
            
        logging.info(f"Parámetros de DB cargados. Host: {params['host']}, DB: {params['db']}")
        return params

    except Exception as e:
        logging.error(f"Error al parsear MYSQL_URL: {e}", exc_info=True)
        return {}

def create_db_table(params):
    try:
        connection = pymysql.connect(**params)
        with connection.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS registrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(sql)
        connection.commit()
        connection.close()
        logging.info("Tabla 'registrations' verificada o creada exitosamente.")
        return True
    except Exception as e:
        logging.error(f"Error al crear/verificar la tabla en la DB: {e}", exc_info=True)
        return False

DB_PARAMS = get_db_connection_params()

if DB_PARAMS.get('host'):
    create_db_table(DB_PARAMS)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email:
        return jsonify({
            'success': False,
            'message': 'Faltan datos requeridos: nombre completo o correo electrónico.'
        }), 400

    if not DB_PARAMS or not DB_PARAMS.get('host'):
        logging.critical("Fallo crítico: No se encontraron parámetros de conexión válidos.")
        return jsonify({
            'success': False, 
            'message': 'Error interno: Faltan parámetros de configuración de la base de datos.'
        }), 500

    try:
        connection = pymysql.connect(**DB_PARAMS)
        
        try:
            with connection.cursor() as cursor:
                sql_check = "SELECT id FROM registrations WHERE email = %s"
                cursor.execute(sql_check, (email,))
                result = cursor.fetchone()
                
                if result:
                    return jsonify({
                        'success': False,
                        'message': 'Este correo electrónico ya está registrado.'
                    }), 409

                sql_insert = "INSERT INTO registrations (name, email, message) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert, (name, email, message))

            connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Registro exitoso! Ahora formas parte del futuro digital. Revisa tu correo para los detalles del evento.'
            }), 201

        finally:
            connection.close()

    except pymysql.err.OperationalError as e:
        logging.error(f"Error Operacional de MySQL (Conexión/DB): {e}", exc_info=True)
        return jsonify({
            'success': False, 
            'message': 'Error interno: No se pudo conectar o interactuar con la base de datos. Por favor, verifica tu servidor MySQL y configuración.'
        }), 500
        
    except Exception as e:
        logging.error(f"Error desconocido durante el registro: {e}", exc_info=True)
        return jsonify({
            'success': False, 
            'message': 'Error interno desconocido durante el procesamiento de su solicitud.'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)