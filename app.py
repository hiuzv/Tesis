from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

# Configurar la clave de la API de OpenAI desde las variables de entorno
openai.api_key = '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'

# Palabras clave relacionadas con minería de datos
palabras_clave_mineria = ['mineria de datos', 'minería de datos', 'analisis de datos', 'análisis de datos', 'big data', 'data mining',
    'ciencia de datos', 'machine learning', 'aprendizaje automatico', 'aprendizaje automático', 'inteligencia artificial',
    'ia', 'algoritmos', 'modelos de datos', 'patrones de datos', 'patron de datos', 'patrón de datos',
    'extracción de datos', 'extraccion de datos', 'bases de datos', 'clusters', 'clustering', 'segmentación de datos',
    'segmentacion de datos', 'prediccion', 'predicción', 'clasificacion', 'clasificación', 'regresión', 'regresion',
    'k-means', 'kmeans', 'árboles de decisión', 'arboles de decision', 'decision trees', 'random forest', 'bosque aleatorio',
    'redes neuronales', 'neural networks', 'text mining', 'minería de texto', 'mineria de texto', 'procesamiento de lenguaje natural',
    'natural language processing', 'nlp', 'exploración de datos', 'exploracion de datos', 'data exploration', 'limpieza de datos',
    'preprocesamiento de datos', 'preprocesado de datos', 'data preprocessing', 'reducción de dimensionalidad', 'reduccion de dimensionalidad',
    'pca', 'componentes principales', 'principal component analysis', 'análisis predictivo', 'analisis predictivo',
    'modelado predictivo', 'predictive modeling', 'reglas de asociación', 'association rules', 'outliers', 'valores atípicos',
    'valores atipicos', 'análisis de correlación', 'analisis de correlacion', 'correlation analysis', 'análisis estadístico',
    'analisis estadistico', 'estadística descriptiva', 'estadistica descriptiva', 'estadística inferencial', 'estadistica inferencial',
    'data science', 'ciudadanos de datos', 'data citizens', 'bigquery', 'google analytics', 'power bi', 'tableau', 'visualización de datos',
    'visualizacion de datos', 'data visualization', 'data warehouse', 'almacenamiento de datos', 'data lakes', 'lagos de datos',
    'procesamiento de datos', 'data processing', 'limpieza de datos', 'cleaning data', 'modelo supervisado', 'modelo no supervisado',
    'supervised learning', 'unsupervised learning', 'clustering jerárquico', 'hierarchical clustering', 'categorización de datos',
    'categorization of data', 'dataframes', 'pandas', 'numpy', 'estadística bayesiana', 'estadistica bayesiana', 'bayesian statistics',
    'descubrimiento de patrones', 'discovery of patterns', 'detección de fraudes', 'deteccion de fraudes', 'fraud detection',
    'optimización de modelos', 'optimizacion de modelos', 'model optimization', 'validación cruzada', 'validacion cruzada',
    'cross validation', 'recolección de datos', 'recoleccion de datos', 'data collection', 'curación de datos', 'curacion de datos',
    'data curation', 'técnicas de muestreo', 'tecnicas de muestreo', 'sampling techniques', 'muestreo aleatorio', 'random sampling',
    'muestreo estratificado', 'stratified sampling', 'muestreo sistemático', 'muestreo sistematico', 'systematic sampling',
    'muestreo por conglomerados', 'cluster sampling', 'overfitting', 'sobreajuste', 'underfitting', 'subajuste', 'validación del modelo',
    'validacion del modelo', 'model validation', 'precisión del modelo', 'precision del modelo', 'accuracy', 'matriz de confusión',
    'matriz de confusion', 'confusion matrix', 'area bajo la curva', 'area bajo la curva roc', 'roc auc', 'tasa de falsos positivos',
    'false positive rate', 'recall', 'precisión', 'precision', 'f1 score', 'tokenización', 'tokenization', 'word embeddings',
    'vectores de palabras', 'agrupamiento de datos', 'data clustering', 'segmentación de clientes', 'segmentacion de clientes'
]

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get("prompt").lower()

    # Verificar si la pregunta está relacionada con minería de datos
    if not any(palabra in prompt for palabra in palabras_clave_mineria):
        return jsonify({"response": "Solo puedo responder preguntas relacionadas con minería de datos."})

    try:
        # Usar el nuevo método de la API de chat completions
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Modelo más reciente para chats
            messages=[
                {"role": "system", "content": "Solo puedes responder preguntas relacionadas con minería de datos."},
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
