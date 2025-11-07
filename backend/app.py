import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection_params():
    mysql_url = os.environ.get('MYSQL_URL')
    
    if mysql_url:
        try:
            url = urlparse(mysql_url)
            db_name = url.path[1:] 
            
            return {
                'host': url.hostname,
                'user': url.username,
                'password': url.password,
                'db': db_name,
                'port': url.port or 3306,
                'charset': 'utf8mb4',
                'cursorclass': pymysql.cursors.DictCursor
            }
        except Exception as e:
            print(f"Error al parsear MYSQL_URL: {e}")
            return None
            
    else:
        return {
            'host': os.environ.get('DB_HOST'),
            'user': os.environ.get('DB_USER'),
            'password': os.environ.get('DB_PASS'),
            'db': os.environ.get('DB_NAME'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message', '')

    if not name or not email:
        return jsonify({"message": "Nombre y correo electrónico son requeridos."}), 400

    conn = None
    try:
        db_params = get_db_connection_params()
        
        if not db_params:
            print("ERROR: No se pudieron obtener los parámetros de conexión de la base de datos.")
            return jsonify({"message": "Error interno: Configuración de DB faltante."}), 500
            
        conn = pymysql.connect(**db_params)
        
        with conn.cursor() as cursor:
            sql_check = "SELECT id FROM registrations WHERE email = %s"
            cursor.execute(sql_check, (email,))
            if cursor.fetchone():
                return jsonify({"message": "Este correo ya se encuentra registrado."}), 409

            sql_insert = "INSERT INTO registrations (name, email, message) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, (name, email, message))
        
        conn.commit()
        return jsonify({"message": "Registro exitoso", "email": email}), 201

    except pymysql.err.OperationalError as e:
        print(f"ERROR: No se pudo conectar a la base de datos. Error: {e}")
        return jsonify({"message": "Error interno: No se pudo conectar a la base de datos."}), 500
    except pymysql.err.IntegrityError as e:
        print(f"ERROR de integridad: {e}")
        return jsonify({"message": "Este correo ya está registrado (Error de integridad)."}), 409
    except Exception as e:
        print(f"ERROR desconocido en el backend: {e}")
        return jsonify({"message": "Error interno del servidor."}), 500
    finally:
        if conn and conn.open:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))