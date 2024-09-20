from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

# Configurar la clave de la API de OpenAI desde las variables de entorno
openai.api_key = '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'

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"response": "Escribe algo para que te pueda ayudar."})

    try:
        # Usar el método anterior de la API completions
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Modelo más reciente para chats
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
