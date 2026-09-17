
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.inference import (
    get_model_information,
    predict_sentiment
)


class PredictionRequest(BaseModel):
    review_text: str = Field(
        min_length=3,
        max_length=5_000
    )


class PredictionResponse(BaseModel):
    sentiment: str
    decision_scores: dict[str, float]
    model_name: str
    model_version: str
    prediction_milliseconds: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    model_version: str
    classes: list[str]


app = FastAPI(
    title='Restaurant Sentiment API',
    description=(
        'Clasificación del sentimiento '
        'de reseñas de restaurantes.'
    ),
    version='1.0.0'
)


@app.get(
    '/health',
    response_model=HealthResponse
)
def health_check():
    # Comprobar el modelo
    try:
        model_information = (
            get_model_information()
        )

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        ) from error

    return {
        'status': 'ok',
        **model_information
    }


@app.post(
    '/api/v1/sentiment',
    response_model=PredictionResponse
)
def predict_review_sentiment(
    request: PredictionRequest
):
    # Generar la predicción
    try:
        return predict_sentiment(
            request.review_text
        )

    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error
