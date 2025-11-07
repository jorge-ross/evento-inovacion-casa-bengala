from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
import time

DB_USER = os.environ.get('DB_USER', 'usuario_ejemplo')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'password_ejemplo')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'mi_base_de_datos')

app = Flask(__name__)
CORS(app)

def get_db_connection():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                database=DB_NAME,
                dictionary=True
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Intento {attempt + 1}/{max_retries} fallido. Error de conexión: {err}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print("Error fatal: No se pudo conectar a la base de datos después de varios intentos.")
                return None

@app.route('/')
def home():
    return jsonify({
        "status": "Running", 
        "service": "Flask API",
        "database_host": DB_HOST
    })

@app.route('/test-db', methods=['GET'])
def test_db_connection():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return jsonify({
                "status": "success", 
                "message": "Conexión a la base de datos exitosa (SELECT 1 OK)."
            })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Conexión OK, pero error al ejecutar consulta: {str(e)}"
            }), 500
        finally:
            conn.close()
    else:
        return jsonify({
            "status": "error", 
            "message": "Fallo al conectar a la base de datos. Revise credenciales y host."
        }), 500

@app.route('/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB no disponible"}), 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, estado FROM items ORDER BY id DESC")
        items = cursor.fetchall()
        cursor.close()
        return jsonify(items)
    except Exception as e:
        print(f"Error al obtener items: {e}")
        return jsonify({"error": "Error al consultar la base de datos."}), 500
    finally:
        conn.close()

@app.route('/items', methods=['POST'])
def add_item():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB no disponible"}), 500
    
    data = request.get_json()
    nombre = data.get('nombre')
    
    if not nombre:
        return jsonify({"error": "El campo 'nombre' es requerido."}), 400

    try:
        cursor = conn.cursor()
        sql = "INSERT INTO items (nombre, estado) VALUES (%s, %s)"
        cursor.execute(sql, (nombre, 'pendiente'))
        conn.commit()
        item_id = cursor.lastrowid
        cursor.close()
        return jsonify({"message": "Item creado", "id": item_id}), 201
    except Exception as e:
        print(f"Error al añadir item: {e}")
        conn.rollback()
        return jsonify({"error": "Error al insertar en la base de datos."}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000), debug=False)