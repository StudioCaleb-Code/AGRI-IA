import os
from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

# --- RUTAS BASE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'dataset_cultivos_500.csv')

# --- CARGA SEGURA DE MODELOS ---
def load_model(path):
    try:
        return joblib.load(path)
    except Exception as e:
        print(f"ERROR cargando {path}: {e}")
        return None

model = load_model(os.path.join(MODELS_DIR, 'agri_model.pkl'))
scaler = load_model(os.path.join(MODELS_DIR, 'scaler.pkl'))
le_cultivo = load_model(os.path.join(MODELS_DIR, 'le_cultivo.pkl'))
le_fertilizante = load_model(os.path.join(MODELS_DIR, 'le_fertilizante.pkl'))
le_resultado = load_model(os.path.join(MODELS_DIR, 'le_resultado.pkl'))

print("✔ Sistema AGRI-IA iniciado")

# --- RUTAS WEB ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/opciones')
def opciones():
    try:
        df = pd.read_csv(DATA_CSV)

        lista_plantas = sorted(df['tipo_cultivo'].unique())
        lista_plantas = [p.strip().capitalize() for p in lista_plantas]

        return render_template('opciones.html', plantas_csv=lista_plantas)

    except Exception as e:
        print(f"Error CSV: {e}")
        return render_template('opciones.html', plantas_csv=[])

# --- PREDICCIÓN ---
@app.route('/predict', methods=['POST'])
def predict():

    # Validación de modelos
    if None in [model, scaler, le_cultivo, le_fertilizante, le_resultado]:
        return jsonify({
            "status": "error",
            "message": "Modelos no cargados en servidor"
        }), 500

    try:
        data = request.get_json()

        plantas = data.get('plantas', [])
        temp = float(data['temperatura'])
        hum = float(data['humedad'])
        ph = float(data['ph'])
        fert = data['fertilizante'].lower().strip()

        resultados = []

        for planta in plantas:

            try:
                planta_clean = planta.lower().strip()

                # Encoding
                planta_encoded = le_cultivo.transform([planta_clean])[0]
                fert_encoded = le_fertilizante.transform([fert])[0]

                # Input
                input_data = pd.DataFrame([[planta_encoded, temp, hum, fert_encoded, ph]],
                                          columns=['tipo_cultivo', 'temperatura', 'humedad_suelo', 'tipo_fertilizante', 'ph_suelo'])

                # Escalado
                input_data[['temperatura', 'humedad_suelo', 'ph_suelo']] = scaler.transform(
                    input_data[['temperatura', 'humedad_suelo', 'ph_suelo']]
                )

                # Predicción
                probs = model.predict_proba(input_data)[0]

                idx = np.where(le_resultado.classes_ == 'exito')[0][0]
                prob_final = round(probs[idx] * 100, 2)

                resultados.append({
                    "planta": planta,
                    "probabilidad": prob_final,
                    "crecera": "SÍ" if prob_final >= 65 else "NO"
                })

            except Exception as e:
                print(f"Error planta {planta}: {e}")
                continue

        promedio = round(
            sum(r['probabilidad'] for r in resultados) / len(resultados), 2
        ) if resultados else 0

        return jsonify({
            "status": "success",
            "promedio": promedio,
            "detalles": resultados
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


if __name__ == '__main__':
    app.run(debug=True)
