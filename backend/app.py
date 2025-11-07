import os
import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection_params():
    mysql_url = os.environ.get('MYSQL_URL')
    
    if mysql_url:
        try:
            url = urlparse(mysql_url)
            print(f"DEBUG DB CONFIG (sin password): host={url.hostname}, port={url.port}, user={url.username}, database={url.path.strip('/')}")

            return {
                'host': url.hostname,
                'user': url.username,
                'password': url.password,
                'database': url.path.strip('/'),
                'port': url.port if url.port else 3306,
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor
            }
        except Exception as e:
            print(f"Error al parsear MYSQL_URL: {e}")
            return None
    
    return None

def verify_db_connection(params):
    if not params:
        print("Error: Parámetros de conexión a DB no encontrados.")
        return False

    print(f"Intentando conectar a la base de datos: {params.get('database')} en {params.get('host')}:{params.get('port')} con usuario {params.get('user')}")
    
    try:
        connection = pymysql.connect(**params)
        connection.close()
        print("Conexión a MySQL exitosa.")
        return True
    except pymysql.Error as e:
        print(f"Error al conectar a MySQL. Detalles del error: {e}")
        return False
    except Exception as e:
        print(f"Error desconocido durante la verificación de conexión: {e}")
        return False

db_params = get_db_connection_params()
verify_db_connection(db_params)

@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        full_name = data.get('full_name')
        email = data.get('email')
        message = data.get('message')

        if not all([full_name, email]):
            return jsonify({"success": False, "message": "Faltan datos requeridos: nombre completo o correo electrónico."}), 400

        if not db_params:
            print("Error: Parámetros de DB no disponibles en el endpoint /api/register.")
            return jsonify({"success": False, "message": "Error interno: Configuración de la base de datos no encontrada."}), 500

        try:
            connection = pymysql.connect(**db_params)

            try:
                with connection.cursor() as cursor:
                    sql = "INSERT INTO registrations (full_name, email, message) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (full_name, email, message))

                connection.commit()
                print(f"Registro exitoso para: {email}")
                return jsonify({"success": True, "message": "Registro exitoso."}), 200

            finally:
                connection.close()

        except pymysql.Error as e:
            print(f"Error de base de datos al registrar: {e}")
            return jsonify({"success": False, "message": "Error interno: No se pudo completar el registro en la base de datos. Por favor, verifica tu servidor MySQL y configuración."}), 500
        
        except Exception as e:
            print(f"Error inesperado en /api/register: {e}")
            return jsonify({"success": False, "message": "Error interno desconocido."}), 500

    except Exception as e:
        print(f"Error al recibir o procesar JSON: {e}")
        return jsonify({"success": False, "message": "Formato de solicitud inválido."}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)