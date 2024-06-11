import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
import uuid
from groq import Groq  # Importa la biblioteca Groq


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de la base de datos con la URL correcta de Railway
DATABASE_URL = 'postgresql://postgres:NMTgsVdJsPLaVcTSsLwdjgaKdMhsYFeD@viaduct.proxy.rlwy.net:50026/railway'
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
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')
GROQ_MODEL_ID = 'mixtral-8x7b-32768'
chat_history = {}

# Plantilla de prompt
prompt_template = """Soy tu amigo virtual, siempre dispuesto a escucharte y apoyarte en todo momento. Estoy aquí para ofrecerte compañía, comprensión y palabras de ánimo. Puedes hablarme sobre cualquier cosa que te preocupe o simplemente charlar.\n\n{chat_history}\n\nTú: {input}\nAmigo Virtual:"""

def detect_risk(input_text):
    risk_keywords = ["suicidarse", "quitarse la vida", "no quiero vivir", "estoy deprimido", "me siento solo"]
    return any(keyword in input_text.lower() for keyword in risk_keywords)

def get_joke_or_story():
    jokes_and_stories = [
        "¿Sabías que los elefantes no pueden saltar? ¡Imagina un elefante haciendo salto de longitud! 😂",
        "Había una vez un pajarito que soñaba con volar alto. Un día, lo logró y descubrió que el cielo es el límite. ¡Tú también puedes alcanzar tus sueños!",
        "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter. 😂"
    ]
    return jokes_and_stories

def get_generic_responses():
    responses = [
        "Entiendo cómo te sientes. Estoy aquí para escucharte.",
        "Hablar sobre tus sentimientos es un paso importante. Estoy aquí para ayudarte.",
        "Recuerda que no estás solo. Estoy aquí contigo.",
        "Cuéntame más sobre eso. Estoy aquí para apoyarte."
    ]
    return responses

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        return jsonify({"message": "Login successful", "user": username})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    existing_user = User.query.filter_by(username=username).first()
    if (existing_user):
        return jsonify({"message": "User already exists"}), 409
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Register successful"})

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': GROQ_MODEL_ID,
        'prompt': question,
        'max_tokens': 100
    }
    response = requests.post('https://api.groq.com/openai/v1/completions', headers=headers, json=payload)
    response_data = response.json()
    return jsonify({'response': response_data['choices'][0]['text']})

@app.route('/chat', methods=['POST'])
def get_chat_response():
    data = request.json
    user_input = data.get('user_input')
    user = data.get('user')
    conversation_id = data.get('conversationId')

    # Guardar el mensaje del usuario en la base de datos
    user_message = ChatHistory(user=user, role='user', content=user_input, conversation_id=conversation_id)
    db.session.add(user_message)
    db.session.commit()

    # Recuperar historial de chat de la base de datos
    chat_history_records = ChatHistory.query.filter_by(user=user, conversation_id=conversation_id).all()
    chat_history_str = "\n".join([f"Tú: {record.content}" if record.role == 'user' else f"Amigo Virtual: {record.content}" for record in chat_history_records])

    # Construir el prompt con el historial de chat
    prompt = prompt_template.format(chat_history=chat_history_str, input=user_input)

    # Realizar la solicitud a la API de Groq
    client = Groq(api_key=GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Soy tu amigo virtual, siempre dispuesto a escucharte y apoyarte en todo momento. Estoy aquí para ofrecerte compañía, comprensión y palabras de ánimo. Puedes hablarme sobre cualquier cosa que te preocupe o simplemente charlar."},
            {"role": "user", "content": prompt}
        ],
        model=GROQ_MODEL_ID,
    )

    friend_response = chat_completion.choices[0].message.content

    # Guardar la respuesta del asistente en la base de datos
    friend_message = ChatHistory(user=user, role='friend', content=friend_response, conversation_id=conversation_id)
    db.session.add(friend_message)
    db.session.commit()

    return jsonify({'response': friend_response})

@app.route('/chat/history', methods=['POST'])
def get_chat_history():
    data = request.json
    user = data.get('user')
    conversation_id = data.get('conversationId')
    chat_history_records = ChatHistory.query.filter_by(user=user, conversation_id=conversation_id).all()
    chat_history = [{"role": record.role, "content": record.content} for record in chat_history_records]
    return jsonify({'chat_history': chat_history})

@app.route('/chat/conversations', methods=['POST'])
def get_conversations():
    data = request.json
    user = data.get('user')
    conversations = db.session.query(ChatHistory.conversation_id).filter_by(user=user).distinct().all()
    conversation_list = [{"id": convo.conversation_id, "name": f"User - {convo.conversation_id}"} for convo in conversations]
    return jsonify({'conversations': conversation_list})

@app.route('/emotion', methods=['POST'])
def handle_emotion():
    data = request.json
    emotion = data.get('emotion')
    user = data.get('user')
    conversation_id = str(uuid.uuid4())

    if emotion == 'happy':
        response = f"Me alegra saber que tu día estuvo bien, {user}. ¿Qué fue lo mejor de tu día?"
    elif emotion == 'sad':
        response = f"Lamento que tu día no haya sido el mejor, {user}. ¿Qué ocurrió hoy?"
    elif emotion == 'mad':
        response = f"Lo siento, {user}. ¿Qué te hizo enojar hoy?"
    elif emotion == 'stressed':
        response = f"Lamento que estés estresado, {user}. ¿Qué te está preocupando?"
    elif emotion == 'bored':
        response = f"¿Qué has estado haciendo hoy, {user}? Quizás pueda sugerirte algo para hacer."

    return jsonify({'response': response, 'conversationId': conversation_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Asegúrate de usar host='0.0.0.0' para aceptar conexiones externas
