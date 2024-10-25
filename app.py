import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = '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'
bing_api_key = '84d3848e78af409095cb546430d9b8af'

conversation_history = []

def search_web(query):
    search_url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": bing_api_key}
    params = {"q": query, "count": 3, "textDecorations": True, "textFormat": "HTML"}
    
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    
    results = []
    if "webPages" in search_results:
        for page in search_results["webPages"]["value"]:
            results.append(page["snippet"])
    return " ".join(results)

@app.route('/', methods=['GET'])
def chat():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    global conversation_history
    MAX_HISTORY = 6
    data = request.get_json()
    prompt = data.get("prompt").lower()

    try:
        web_data = search_web(prompt)
        gpt_prompt = f"Contexto de la búsqueda en la web: {web_data}. Pregunta del usuario: {prompt}"
        recent_history = conversation_history[-MAX_HISTORY:]

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Eres un asistente virtual educativo, especializado en enseñar un curso de introducción a la minería de datos y/o ciencia de datos, con Python. "
                                                "A continuación se detallan las reglas que debes seguir estrictamente en cada respuesta:\n"
                                                "1. Solo puedes responder preguntas relacionadas con minería de datos y/o ciencia de datos (Python).\n"
                                                "2. Si te hacen preguntas sobre temas fuera de minería de datos y/o ciencia de datos (Python), explica que solo puedes responder preguntas dentro de ese contexto, pero intenta relacionar la respuesta si es posible.\n"
                                                "3. Si te piden generar o mejorar código, debes devolverlo estrictamente dentro de las etiquetas <pre><code> y </code></pre> para que se visualice correctamente en HTML.\n"
                                                "4. Si te piden generar o mejorar código, debe ser estrictamente relacionado con un tema del curso.\n"
                                                "5. Si te solicitan una mejora de código, asegúrate de mejorar el código proporcionado en lugar de generar un código completamente diferente.\n"
                                                "6. Debes usar el contexto de la búsqueda en la web proporcionado para mejorar la calidad de tus respuestas.\n"
                                                "7. No proporcionas respuestas si el contexto no está relacionado con minería de datos (ciencia de datos) y/o codigo en Python. En ese caso, menciona la restricción del curso.\n"
                                                "8. Debes dar respuesta a la 'Pregunta del usuario', usando las reglas, el 'Contexto de la búsqueda en la web' y las preguntas y respues historial.\n\n"
                                                "Sigue estas reglas al responder cada pregunta."}] + recent_history + [
                {"role": "user", "content": gpt_prompt}
            ]
        )

        assistant_response = response['choices'][0]['message']['content']

        conversation_history.append({"role": "user", "content": "Pregunta anterior, solo usar a modo de historial: " + prompt})
        conversation_history.append({"role": "assistant", "content": "Respuesta anterior, solo usar a modo de historial: " + assistant_response})


        return jsonify({"response": assistant_response})

    except Exception as e:
        print(f"Error al conectarse con OpenAI o Bing: {str(e)}")
        return jsonify({"response": "Error al conectarse con la API: " + str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)