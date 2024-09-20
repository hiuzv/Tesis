from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

# Configurar la clave de la API de OpenAI desde las variables de entorno
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"response": "Escribe algo para que te pueda ayudar."})

    try:
        # Usar el método anterior de la API completions
        response = openai.Completion.create(
            engine="text-davinci-003",  # O el motor que prefieras
            prompt=prompt,
            max_tokens=150
        )
        return jsonify({"response": response.choices[0].text.strip()})
    except Exception as e:
        # Registrar el error en los logs de Railway
        print(f"Error al conectarse con OpenAI: {str(e)}")
        return jsonify({"response": "Error al conectarse con la API de ChatGPT: " + str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
