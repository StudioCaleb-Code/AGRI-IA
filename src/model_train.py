import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder, StandardScaler
from preprocessing import preprocess_data

def train_model():

    print("Iniciando preprocesamiento...")

    X_train, X_test, y_train, y_test = preprocess_data(
        'data/raw/dataset_cultivos_500.csv'
    )

    print("Entrenando modelo AGRI-IA...")

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    # --- evaluación ---
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)

    print(f"Entrenamiento completado.")
    print(f"Precisión: {acc * 100:.2f}%")
    print(classification_report(y_test, predictions))

    # --- carpeta models ---
    os.makedirs('models', exist_ok=True)

    # --- guardar modelo ---
    joblib.dump(model, 'models/agri_model.pkl')

    # --- guardar clases (MUY IMPORTANTE PARA TU FLASK) ---
    joblib.dump(model.classes_, 'models/classes.pkl')

    print("Modelo y clases guardados correctamente.")

if __name__ == "__main__":
    train_model()
