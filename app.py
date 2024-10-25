from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pg8000
import requests
import openai
import os

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

# Conexión a la base de datos PostgreSQL
def get_db_connection():
    conn = pg8000.connect(
        user='postgres',
        password='SWGblPkwOyrUuDjxvWsCpPOBhzZOYaOC',
        host='postgres.railway.internal',
        port=5432,
        database='railway'
    )
    return conn


# Función para recuperar el historial del usuario
def get_user_history(user_ip):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT role, message FROM chat_history WHERE user_id = %s ORDER BY timestamp', (user_ip,))
    history = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in history]

# Función para guardar el historial
def save_message(user_ip, role, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat_history (user_id, role, message) VALUES (%s, %s, %s)', (user_ip, role, message))
    conn.commit()
    conn.close()

@app.route('/', methods=['GET'])
def chat():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    data = request.get_json()

    # Recupera el user_ip, si no existe uno, genera uno nuevo
    user_ip = request.remote_addr
    prompt = data.get("prompt").lower()

    try:
        web_data = search_web(prompt)
        gpt_prompt = f"Contexto de la búsqueda en la web: {web_data}. Pregunta del usuario: {prompt}"
               
        # Recuperar historial previo
        conversation_history = get_user_history(user_ip)

        # Llamada a OpenAI
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
                                                "Sigue estas reglas al responder cada pregunta."}] + conversation_history + [
                {"role": "user", "content": gpt_prompt}
            ]
        )

        assistant_response = response['choices'][0]['message']['content']

        # Guardar los mensajes del usuario y del asistente
        save_message(user_ip, "user", prompt)
        save_message(user_ip, "assistant", assistant_response)

        return jsonify({"response": assistant_response, "user_ip": user_ip})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"response": "Error al conectarse con la API: " + str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
