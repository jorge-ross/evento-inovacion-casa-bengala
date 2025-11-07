import os
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import errorcode
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

class ConnectionError(Exception):
    pass

def get_db_connection():
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')

    try:
        cnx = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connection_timeout=5
        )
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise ConnectionError("Error de autenticación o permisos en MySQL.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise ConnectionError("Base de datos inexistente.")
        elif err.errno == errorcode.CR_CONN_ERROR:
            raise ConnectionError("Host de BD no alcanzable.")
        else:
            raise ConnectionError(f"Error de conexión desconocido: {err}")
    except Exception as e:
        raise ConnectionError(f"Error general: {e}")


def initialize_db():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        
        SQL_CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS Registros (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            message TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(SQL_CREATE_TABLE)
        cnx.commit()
        cursor.close()
        cnx.close()
    except ConnectionError as e:
        print(f"Fallo en la inicialización: {e}")
    except Exception as e:
        print(f"Error desconocido en la inicialización: {e}")


with app.app_context():
    initialize_db()


@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message', '')

    if not name or not email:
        return jsonify({
            "message": "Faltan campos obligatorios (nombre y email).",
            "success": False
        }), 400

    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
    except ConnectionError as e:
        return jsonify({
            "message": f"Error interno: No se pudo conectar la base de datos. Detalle: {e}",
            "success": False
        }), 500

    try:
        SQL_INSERT = "INSERT INTO Registros (name, email, message) VALUES (%s, %s, %s)"
        data_insert = (name, email, message)

        cursor.execute(SQL_INSERT, data_insert)
        cnx.commit()

        return jsonify({
            "message": "Registro exitoso en el evento.",
            "success": True
        }), 201

    except mysql.connector.IntegrityError:
        return jsonify({
            "message": "El correo electrónico ya está registrado.",
            "success": False
        }), 409

    except mysql.connector.Error as err:
        print(f"Error al registrar: {err}")
        return jsonify({
            "message": f"Error de base de datos al intentar registrar: {err.msg}",
            "success": False
        }), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx and cnx.is_connected():
            cnx.close()


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "¡Servidor de Registro de Evento de Casa Bengala activo!",
        "status": "ok"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)