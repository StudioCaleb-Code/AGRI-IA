import os
from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import numpy as np

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS ABSOLUTAS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_CSV = os.path.join(BASE_DIR, 'data', 'raw', 'dataset_cultivos_500.csv')

# --- CARGAR EL CEREBRO DEL MODELO Y TRADUCTORES ---
try:
    model = joblib.load(os.path.join(MODELS_DIR, 'agri_model.pkl'))
    scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
    le_cultivo = joblib.load(os.path.join(MODELS_DIR, 'le_cultivo.pkl'))
    le_fertilizante = joblib.load(os.path.join(MODELS_DIR, 'le_fertilizante.pkl'))
    le_resultado = joblib.load(os.path.join(MODELS_DIR, 'le_resultado.pkl'))
    print("SISTEMA AGRI-IA: Modelos y Encoders cargados correctamente.")
except Exception as e:
    print(f"ERROR CRÍTICO AL CARGAR MODELOS: {e}")
    model = scaler = le_cultivo = le_fertilizante = le_resultado = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/opciones')
def opciones():
    try:
        # Leemos el CSV para obtener la lista de plantas única para el Modal
        df = pd.read_csv(DATA_CSV)
        # Obtenemos nombres únicos, quitamos vacíos y ordenamos
        lista_plantas = sorted(df['tipo_cultivo'].unique())
        # Formateamos para que se vean bien en el HTML (Primera letra mayúscula)
        lista_plantas = [p.strip().capitalize() for p in lista_plantas]
        
        return render_template('opciones.html', plantas_csv=lista_plantas)
    except Exception as e:
        print(f"Error al leer plantas del CSV: {e}")
        return render_template('opciones.html', plantas_csv=[])

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"status": "error", "message": "Modelos no cargados"}), 500
        
    try:
        data = request.get_json()
        plantas = data['plantas'] 
        temp = float(data['temperatura'])
        hum = float(data['humedad'])
        ph = float(data['ph'])
        fert = data['fertilizante'].lower().strip() 

        resultados = []

        for planta in plantas:
            planta_clean = planta.lower().strip()
            
            try:
                # 1. Transformar categorías a números
                planta_encoded = le_cultivo.transform([planta_clean])[0]
                fert_encoded = le_fertilizante.transform([fert])[0]

                # 2. Crear DataFrame de entrada
                input_data = pd.DataFrame([[planta_encoded, temp, hum, fert_encoded, ph]],
                                         columns=['tipo_cultivo', 'temperatura', 'humedad_suelo', 'tipo_fertilizante', 'ph_suelo'])

                # 3. Escalar numéricos
                input_data[['temperatura', 'humedad_suelo', 'ph_suelo']] = scaler.transform(
                    input_data[['temperatura', 'humedad_suelo', 'ph_suelo']]
                )

                # 4. Predicción de probabilidad
                probabilidades = model.predict_proba(input_data)[0]
                
                # Identificar cuál columna es 'exito'
                idx_exito = np.where(le_resultado.classes_ == 'exito')[0][0]
                prob_final = round(probabilidades[idx_exito] * 100, 2)

                resultados.append({
                    "planta": planta,
                    "probabilidad": prob_final,
                    "crecera": "SÍ" if prob_final >= 65 else "NO"
                })
            except Exception as inner_e:
                print(f"Error procesando {planta}: {inner_e}")
                continue 

        if resultados:
            promedio_gral = round(sum(r['probabilidad'] for r in resultados) / len(resultados), 2)
        else:
            promedio_gral = 0

        return jsonify({
            "status": "success",
            "promedio": promedio_gral,
            "detalles": resultados
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
