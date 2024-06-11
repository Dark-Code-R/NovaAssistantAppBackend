import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
import uuid
from groq import Groq

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})   # Habilita CORS para todas las rutas

# Configuración de la base de datos con la URL correcta de Railway
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://username:password@hostname:port/dbname')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de usuario
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Modelo de historial de chat
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    conversation_id = db.Column(db.String(36), nullable=False)

# Crear las tablas
with app.app_context():
    db.create_all()

# Configuración de la API Key y el modelo
GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'tu_api_key_aqui')
GROQ_MODEL_ID = 'mixtral-8x7b-32768'
chat_history = {}

# Plantilla de prompt
prompt_template = """Soy tu amigo virtual, siempre dispuesto a escucharte y apoyarte en todo momento. Estoy aquí para ofrecerte compañía, comprensión y palabras de ánimo. Puedes hablarme sobre cualquier cosa que te preocupe o simplemente charlar.\n\n{chat_history}\n\nTú: {input}\nAmigo Virtual:"""

@app.route('/')
def home():
    return "Backend is running"

# Define aquí tus rutas y lógica

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Asegúrate de usar host='0.0.0.0' para aceptar conexiones externas
