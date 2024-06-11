import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
import uuid

app = Flask(__name__)
CORS(app)   # Habilita CORS para todas las rutas

# Configuración de la base de datos con la URL correcta de Railway desde variables de entorno
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/mydatabase')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    conversation_id = db.Column(db.String(36), nullable=False)

@app.before_first_request
def initialize_database():
    """Create database tables and check database connection."""
    try:
        db.create_all()
    except Exception as e:
        app.logger.error(f'Error initializing database: {e}')

# Rutas
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username'), password=data.get('password')).first()
    if user:
        return jsonify({"message": "Login successful", "user": user.username})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"message": "User already exists"}), 409
    new_user = User(username=data.get('username'), password=data.get('password'))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration successful"})

# Otras rutas aquí...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
