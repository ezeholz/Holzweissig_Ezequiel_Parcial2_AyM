"""
Entrenamiento del modelo de regresión logística para predicción de mora en préstamos.

Características (features):
  - dias_miembro      : Días que lleva el usuario registrado en la biblioteca
  - prestamos_previos : Cantidad de préstamos anteriores
  - multas_previas    : Cantidad de multas acumuladas
  - dias_prestamo     : Duración del período del préstamo (7, 14 o 21 días)
  - genero_id         : Género del libro (codificado 0-10)

Variable objetivo:
  - mora : 1 si el préstamo fue devuelto con retraso, 0 si fue a tiempo

Uso:
  python ml/train_model.py
"""

import os
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

SEED = 42
np.random.seed(SEED)
N_SAMPLES = 2000
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "modelo_mora.joblib")


def generar_datos_sinteticos(n: int) -> tuple:
    """Genera datos de entrenamiento sintéticos con distribuciones realistas."""
    dias_miembro = np.random.randint(1, 1500, n)
    prestamos_previos = np.random.poisson(lam=5, size=n).clip(0, 50)
    multas_previas = np.random.poisson(lam=0.8, size=n).clip(0, 10)
    dias_prestamo = np.random.choice([7, 14, 21], n, p=[0.3, 0.5, 0.2])
    genero_id = np.random.randint(0, 11, n)

    # Probabilidad de mora influenciada por los factores
    prob_mora = (
        0.08
        + 0.15 * (multas_previas / 10)  # más multas → más riesgo
        - 0.05 * (prestamos_previos / 50)  # más historial → menos riesgo
        - 0.03 * (dias_miembro / 1500)  # más antigüedad → menos riesgo
        + 0.04 * ((dias_prestamo - 7) / 14)  # períodos largos → más riesgo
        + np.random.normal(0, 0.05, n)  # ruido
    ).clip(0.03, 0.85)

    mora = (np.random.uniform(0, 1, n) < prob_mora).astype(int)

    X = np.column_stack(
        [dias_miembro, prestamos_previos, multas_previas, dias_prestamo, genero_id]
    )
    return X, mora


def entrenar_y_guardar():
    print("Generando datos de entrenamiento...")
    X, y = generar_datos_sinteticos(N_SAMPLES)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=1000, random_state=SEED, class_weight="balanced"
                ),
            ),
        ]
    )

    print("Entrenando modelo de regresión logística...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy en test: {acc:.4f}")
    print("\nReporte de clasificación:")
    print(classification_report(y_test, y_pred, target_names=["A tiempo", "Con mora"]))

    joblib.dump(pipeline, OUTPUT_PATH)
    print(f"\nModelo guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    entrenar_y_guardar()
