
from functools import lru_cache
from os import getenv
from pathlib import Path
from time import perf_counter

import joblib


# Definir la configuración del modelo
project_path = (
    Path(__file__)
    .resolve()
    .parents[1]
)

default_model_path = (
    project_path
    / 'artifacts'
    / 'models'
    / 'sentiment_tfidf_linear_svc.joblib'
)

model_path = Path(
    getenv(
        'SENTIMENT_MODEL_PATH',
        str(default_model_path)
    )
)

model_name = (
    'sentiment_tfidf_linear_svc'
)

model_version = getenv(
    'MODEL_VERSION',
    '1.0.0'
)

valid_sentiments = {
    'Negativa',
    'Neutral',
    'Positiva'
}


@lru_cache(maxsize=1)
def load_sentiment_model():
    """Cargar el pipeline una sola vez."""

    if not model_path.exists():
        raise FileNotFoundError(
            f'No se encontró el modelo en: {model_path}'
        )

    return joblib.load(
        model_path
    )


def validate_review_text(
    review_text: str
) -> str:
    """Validar y normalizar el texto recibido."""

    if not isinstance(
        review_text,
        str
    ):
        raise TypeError(
            'review_text debe ser una cadena de texto'
        )

    normalized_text = ' '.join(
        review_text.split()
    )

    if len(normalized_text) < 3:
        raise ValueError(
            'review_text debe contener al menos 3 caracteres'
        )

    if len(normalized_text) > 5_000:
        raise ValueError(
            'review_text no puede superar los 5,000 caracteres'
        )

    return normalized_text


def get_model_information() -> dict:
    """Obtener información del pipeline cargado."""

    sentiment_model = load_sentiment_model()

    classifier = (
        sentiment_model
        .named_steps['classifier']
    )

    return {
        'model_loaded': True,
        'model_name': model_name,
        'model_version': model_version,
        'classes': [
            str(model_class)
            for model_class in classifier.classes_
        ]
    }


def predict_sentiment(
    review_text: str
) -> dict:
    """Predecir el sentimiento de una reseña."""

    normalized_text = validate_review_text(
        review_text
    )

    sentiment_model = load_sentiment_model()

    start_time = perf_counter()

    predicted_sentiment = str(
        sentiment_model.predict(
            [normalized_text]
        )[0]
    )

    raw_decision_scores = (
        sentiment_model.decision_function(
            [normalized_text]
        )[0]
    )

    prediction_milliseconds = (
        perf_counter() - start_time
    ) * 1_000

    classifier = (
        sentiment_model
        .named_steps['classifier']
    )

    decision_scores = {
        str(model_class): round(
            float(score),
            4
        )
        for model_class, score in zip(
            classifier.classes_,
            raw_decision_scores
        )
    }

    if predicted_sentiment not in valid_sentiments:
        raise RuntimeError(
            'El modelo produjo una clase no reconocida'
        )

    return {
        'sentiment': predicted_sentiment,
        'decision_scores': decision_scores,
        'model_name': model_name,
        'model_version': model_version,
        'prediction_milliseconds': round(
            prediction_milliseconds,
            4
        )
    }
