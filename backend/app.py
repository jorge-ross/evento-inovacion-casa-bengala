import os
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        db = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return db
    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
        return None

@app.route('/')
def home():
    return jsonify({"message": "Bienvenido a la API de Flask. La base de datos está configurada."})

@app.route('/datos', methods=['GET'])
def get_data():
    db = get_db_connection()
    if not db:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM tu_tabla")
        datos = cursor.fetchall()
        return jsonify(datos)
    except Exception as e:
        print(f"Error al ejecutar consulta: {e}")
        return jsonify({"error": f"Error al obtener datos: {str(e)}"}), 500
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(debug=True)