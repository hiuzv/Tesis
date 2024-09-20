from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

# Configurar la clave de la API de OpenAI desde las variables de entorno
openai.api_key = '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'

@app.route('/')
def index():
    # Página principal donde el usuario puede hacer clic en el botón de chat
    return render_template('index.html')

@app.route('/chat', methods=['GET'])
def chat():
    # Servir el archivo HTML del chat
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    prompt = data.get("prompt").lower()

    try:
        # Dar una instrucción explícita al modelo para que solo hable de minería de datos
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente virtual educativo, para un curso de introduccion a la mineria de datos, Solo puedes responder preguntas relacionadas con minería de datos. Si te hacen preguntas sobre otro tema, responde que solo puedes hablar sobre temas relacionados al curso."},
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({"response": response['choices'][0]['message']['content']})
    except Exception as e:
        print(f"Error al conectarse con OpenAI: {str(e)}")
        return jsonify({"response": "Error al conectarse con la API de ChatGPT: " + str(e)})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
