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
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        results = []
        if "webPages" in search_results:
            for page in search_results["webPages"]["value"]:
                results.append(page["snippet"])
        return " ".join(results)

    except requests.exceptions.RequestException as e:
        # Captura cualquier error relacionado con la solicitud
        print(f"Error al conectarse a Bing: {e}")
        return "No se pudo obtener el contexto de búsqueda en este momento."

# Conexión a la base de datos PostgreSQL
def get_db_connection():
    conn = pg8000.connect(
        user='postgres',
        password='APCItQjaLpOjDXrVWgrhqZbhTxSHZIpu',
        host='postgres-_joe.railway.internal',
        port=5432,
        database='railway'
    )
    return conn

# Función para guardar el feedback
def save_feedback(user_ip, feedback, message_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_feedback (user_ip, feedback, message_id) VALUES (%s, %s, %s)', (user_ip, feedback, message_id))
    conn.commit()
    conn.close()

# Función para recuperar el historial del usuario
def get_user_history(user_ip):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT role, message FROM chat_history_ip WHERE user_id = %s AND AND fecha >= NOW() - INTERVAL ''3 hours'' ORDER BY fecha DESC LIMIT 6', (user_ip,))
    history = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "content": row[1]} for row in history]

# Función para guardar el historial
def save_message(user_ip, nombre_usuario, role, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
            '''
            INSERT INTO chat_history_ip (user_id, role, message, nombre_usuario)
            VALUES (%s, %s, %s, %s)
            RETURNING message_id
            ''',
            (user_ip, role, message, nombre_usuario)
        )
    message_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return message_id

@app.route('/', methods=['GET'])
def chat():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    data = request.get_json()

    # Recupera el user_ip, si no existe uno, genera uno nuevo
    user_ip = request.remote_addr
    prompt = data.get("prompt").lower()
    nombre_usuario = data.get("nombre_usuario", "Usuario Anónimo")

    try:
        # Contexto de la búsqueda en la web
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

        # Asegurarte de que el código esté encerrado en <pre><code> y </code></pre>
        if "```" in assistant_response:  # Si el asistente genera un bloque de código Markdown
            assistant_response = assistant_response.replace("```python", "<pre><code>")
            assistant_response = assistant_response.replace("```", "</code></pre>")

        assistant_response = format_response_as_html(assistant_response)

        # Guardar los mensajes del usuario y del asistente
        user_message_id = save_message(user_ip, nombre_usuario, "user", prompt)
        assistant_message_id = save_message(user_ip, nombre_usuario, "assistant", assistant_response)

        return jsonify({
            "response": assistant_response,
            "user_ip": user_ip,
            "user_message_id": user_message_id,
            "assistant_message_id": assistant_message_id
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"response": f"Error al conectarse con la API: {str(e)}", "user_ip": user_ip})

def format_response_as_html(response_text):
    """
    Convierte texto con formato Markdown en HTML.
    """
    import re

    # Convertir encabezados de nivel 3 (###) en etiquetas <h3>
    response_text = re.sub(r'### (.+)', r'<h3>\1</h3>', response_text)

    # Convertir listas numeradas en <ul> y <li>, eliminando los números
    def replace_numbered_list(match):
        items = match.group(0).split('\n')
        formatted_items = []
        for item in items:
            if item.strip():  # Ignorar líneas vacías
                _, text = item.split('.', 1)
                formatted_items.append(f"<li>{text.strip()}</li>")
        return f"<ul>{''.join(formatted_items)}</ul>"

    response_text = re.sub(r'(\d+\.\s.+(\n|$))+', replace_numbered_list, response_text)

    # Convertir texto en **negrita** en <b>
    response_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', response_text)

    # Convertir texto en *itálica* en <i>
    response_text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', response_text)

    # Reemplazar saltos de línea por <br> (opcional, según el caso)
    response_text = response_text.replace('\n', '<br>')

    return response_text


@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    feedback = data.get('feedback')  # 'like' o 'dislike'
    user_ip = request.remote_addr
    message_id = data.get('message_id')

    try:
        save_feedback(user_ip, feedback, message_id)
        return jsonify({"status": "success", "message": "Feedback saved"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
