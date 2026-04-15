import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

def preprocess_data(file_path):
    # Cargar datos
    df = pd.read_csv(file_path)

    # Inicializar Encoders para convertir texto a números
    le_cultivo = LabelEncoder()
    le_fert = LabelEncoder()
    le_res = LabelEncoder()

    # Aplicar transformaciones
    df['tipo_cultivo'] = le_cultivo.fit_transform(df['tipo_cultivo'])
    df['tipo_fertilizante'] = le_fert.fit_transform(df['tipo_fertilizante'])
    df['resultado'] = le_res.fit_transform(df['resultado']) # exito=0, no_exito=1 (depende del orden)

    # Guardar los encoders para usarlos luego en app.py (predicción)
    # Sin esto, app.py no sabrá qué número es "Yuca"
    joblib.dump(le_cultivo, 'models/le_cultivo.pkl')
    joblib.dump(le_fert, 'models/le_fertilizante.pkl')
    joblib.dump(le_res, 'models/le_resultado.pkl')

    # Separar características (X) y etiqueta (y)
    X = df.drop('resultado', axis=1)
    y = df['resultado']

    # Escalar datos numéricos (Temperatura, Humedad, pH)
    scaler = StandardScaler()
    X[['temperatura', 'humedad_suelo', 'ph_suelo']] = scaler.fit_transform(X[['temperatura', 'humedad_suelo', 'ph_suelo']])
    
    # Guardar el scaler
    joblib.dump(scaler, 'models/scaler.pkl')

    return train_test_split(X, y, test_size=0.2, random_state=42)

if __name__ == "__main__":
    # Prueba rápida
    X_train, X_test, y_train, y_test = preprocess_data('data/raw/datos.csv')
    print("Datos procesados correctamente.")