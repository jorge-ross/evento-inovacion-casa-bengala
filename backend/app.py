import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql.cursors
from urllib.parse import urlparse, parse_qs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

DB_PARAMS = None
DB_INITIALIZED = False

def get_db_connection_params():
    global DB_PARAMS
    if DB_PARAMS is not None:
        return DB_PARAMS

    mysql_url = os.environ.get('MYSQL_URL')

    if not mysql_url:
        logging.critical("CRITICO: MYSQL_URL no configurada. Usando 127.0.0.1.")
        DB_PARAMS = {
            'host': '127.0.0.1', 
            'user': 'root', 
            'password': '', 
            'db': 'testdb', 
            'charset': 'utf8mb4'
        }
        return DB_PARAMS

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
            
        logging.info(f"DB PARAMETROS CARGADOS. Host: {params.get('host')}, Puerto: {params.get('port')}, DB: {params.get('db')}")
        DB_PARAMS = params
        return DB_PARAMS

    except Exception as e:
        logging.error(f"ERROR: Fallo al parsear MYSQL_URL: {e}", exc_info=True)
        return {}

def create_db_table():
    global DB_INITIALIZED, DB_PARAMS
    if DB_INITIALIZED:
        return True

    if DB_PARAMS is None:
        get_db_connection_params()

    if not DB_PARAMS or not DB_PARAMS.get('host'):
        logging.critical("CRITICO: No hay parametros de DB validos para inicializar.")
        return False
        
    connection = None
    try:
        logging.info(f"INTENTANDO CONECTAR a HOST: {DB_PARAMS.get('host')}")
        connection = pymysql.connect(**DB_PARAMS)
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
        DB_INITIALIZED = True
        logging.info("EXITO: Tabla 'registrations' verificada/creada.")
        return True
    except pymysql.err.OperationalError as e:
        logging.error(f"FALLO CRITICO DE CONEXION MYSQL (OperationalError): {e}", exc_info=True)
        return False
    except Exception as e:
        logging.error(f"ERROR: Fallo al crear/verificar la tabla: {e}", exc_info=True)
        return False
    finally:
        if connection:
            connection.close()

@app.route('/api/register', methods=['POST'])
def register():
    global DB_INITIALIZED
    
    if DB_PARAMS is None:
        get_db_connection_params()
        
    if not DB_INITIALIZED:
        if not create_db_table():
            return jsonify({
                'success': False, 
                'message': 'Error interno: No se pudo conectar la base de datos para la inicialización. Verifica tu configuración.'
            }), 500
    
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email:
        return jsonify({
            'success': False,
            'message': 'Faltan datos requeridos: nombre completo o correo electrónico.'
        }), 400

    if not DB_PARAMS or not DB_PARAMS.get('host') or not DB_INITIALIZED:
        logging.critical("CRITICO: Parámetros DB no válidos o DB no inicializada.")
        return jsonify({
            'success': False, 
            'message': 'Error interno: Faltan parámetros de configuración de la base de datos.'
        }), 500

    connection = None
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
            if connection:
                connection.close()

    except pymysql.err.OperationalError as e:
        logging.error(f"Error Operacional de MySQL (Conexión/DB): {e}", exc_info=True)
        return jsonify({
            'success': False, 
            'message': 'Error interno: No se pudo conectar o interactuar con la base de datos. Por favor, verifica tu servidor MySQL y configuración."
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