from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Configura tu clave de API de OpenAI
openai.api_key = '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'

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get("prompt")

    if not prompt:
        return jsonify({"response": "Escribe algo para que te pueda ayudar."})

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # O el motor que prefieras
            prompt=prompt,
            max_tokens=150
        )
        return jsonify({"response": response.choices[0].text.strip()})
    except Exception as e:
        return jsonify({"response": "Error al conectarse con la API de ChatGPT: " + str(e)})

if __name__ == '__main__':
    app.run(debug=True)

