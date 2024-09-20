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
        # Usar el nuevo método de la API Chat completions
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Elige el modelo que prefieras, por ejemplo, "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Eres un asistente educativo."},
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({"response": response['choices'][0]['message']['content']})
    except Exception as e:
        # Registrar el error en los logs de Railway
        print(f"Error al conectarse con OpenAI: {str(e)}")
        return jsonify({"response": "Error al conectarse con la API de ChatGPT: " + str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
