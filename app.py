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
    params = {"q": query, "count": 5, "textDecorations": True, "textFormat": "HTML"}
    
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
    data = request.get_json()
    prompt = data.get("prompt").lower()

    try:
        web_data = search_web(prompt)

        conversation_history.append({"role": "user", "content": prompt})
        
        gpt_prompt = f"Contexto de la búsqueda en la web: {web_data}. Pregunta del usuario: {prompt}"

        conversation_history.append({"role": "system", "content": gpt_prompt})

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente virtual educativo, experto en enseñar temas sobre un curso de introduccion a la mineria de datos (Ciencia de datos) con python, Solo debes responder preguntas relacionadas con minería de datos (Ciencia de datos) con python. Si te hacen preguntas sobre otro tema, responde que solo debes hablar sobre temas relacionados al curso, pueden pedirte mejoras de codigo o seguir una conversación anterior, si te solicitan código, devuélvelo dentro de las etiquetas <pre><code> para que se visualice correctamente en HTML, tambien Utiliza el contexto de la web proporcionado para mejorar tus respuestas."},
                {"role": "user", "content": gpt_prompt},
                conversation_history
            ]
        )

        assistant_response = response['choices'][0]['message']['content']
        conversation_history.append({"role": "assistant", "content": assistant_response})

        return jsonify({"response": assistant_response})
        
    except Exception as e:
        print(f"Error al conectarse con OpenAI o Bing: {str(e)}")
        return jsonify({"response": "Error al conectarse con la API: " + str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)