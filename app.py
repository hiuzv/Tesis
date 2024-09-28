from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

# Configurar la clave de la API de OpenAI desde las variables de entorno
openai.api_key = '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'

@app.route('/', methods=['GET'])
def chat():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    prompt = data.get("prompt").lower()

    try:
        # Dar una instrucción explícita al modelo para que solo hable de minería de datos
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente virtual educativo, experto en enseñar temas sobre un curso de introduccion a la mineria de datos (Ciencia de datos) con python, Solo debes responder preguntas relacionadas con minería de datos (Ciencia de datos) con python. Si te hacen preguntas sobre otro tema, responde que solo debes hablar sobre temas relacionados al curso, si te solicitan código, devuélvelo dentro de las etiquetas <pre><code> para que se visualice correctamente en HTML."},
                {"role": "user", "content": prompt}
            ]
        )
        return jsonify({"response": response['choices'][0]['message']['content']})
    except Exception as e:
        print(f"Error al conectarse con OpenAI: {str(e)}")
        return jsonify({"response": "Error al conectarse con la API de ChatGPT: " + str(e)})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
