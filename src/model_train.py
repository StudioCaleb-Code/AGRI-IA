import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# -------------------------------
# CARGAR DATASET
# -------------------------------
def load_data(path):
    df = pd.read_csv(path)

    # limpiar por si acaso
    df = df.dropna()

    return df


# -------------------------------
# ENTRENAMIENTO
# -------------------------------
def train_model():

    print("📊 Cargando dataset...")

    df = load_data('data/raw/dataset_cultivos_500.csv')

    # -------------------------------
    # ENCODERS (IMPORTANTE)
    # -------------------------------
    le_cultivo = LabelEncoder()
    le_fertilizante = LabelEncoder()
    le_resultado = LabelEncoder()

    df['tipo_cultivo'] = le_cultivo.fit_transform(df['tipo_cultivo'])
    df['tipo_fertilizante'] = le_fertilizante.fit_transform(df['tipo_fertilizante'])
    df['resultado'] = le_resultado.fit_transform(df['resultado'])

    # -------------------------------
    # FEATURES Y TARGET
    # -------------------------------
    X = df[['tipo_cultivo', 'temperatura', 'humedad_suelo',
            'tipo_fertilizante', 'ph_suelo']]

    y = df['resultado']

    # -------------------------------
    # SPLIT
    # -------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # -------------------------------
    # MODELO
    # -------------------------------
    print("🌱 Entrenando modelo...")

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    # -------------------------------
    # EVALUACIÓN
    # -------------------------------
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)

    print(f"✅ Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, preds))

    # -------------------------------
    # GUARDAR MODELOS
    # -------------------------------
    os.makedirs('models', exist_ok=True)

    joblib.dump(model, 'models/agri_model.pkl')
    joblib.dump(le_cultivo, 'models/le_cultivo.pkl')
    joblib.dump(le_fertilizante, 'models/le_fertilizante.pkl')
    joblib.dump(le_resultado, 'models/le_resultado.pkl')

    print("💾 Modelos guardados correctamente")


# -------------------------------
if __name__ == "__main__":
    train_model()
