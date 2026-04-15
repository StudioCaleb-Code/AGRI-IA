import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from preprocessing import preprocess_data
import os

def train_model():
    print("Iniciando preprocesamiento...")
    X_train, X_test, y_train, y_test = preprocess_data('data/raw/dataset_cultivos_500.csv')

    print("Entrenando el modelo AGRI-IA...")
    # Creamos el modelo con 100 árboles de decisión
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Validar el entrenamiento
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    
    print(f"Entrenamiento completado.")
    print(f"Precisión del modelo: {acc * 100:.2f}%")
    print("\nReporte de Clasificación:")
    print(classification_report(y_test, predictions))

    # Guardar el modelo final en la carpeta models/
    if not os.path.exists('models'):
        os.makedirs('models')
        
    joblib.dump(model, 'models/agri_model.pkl')
    print("Modelo guardado en models/agri_model.pkl")

if __name__ == "__main__":
    train_model()