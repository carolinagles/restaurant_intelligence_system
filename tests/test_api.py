
from fastapi.testclient import TestClient

from app.api import app


api_client = TestClient(app)


def test_health():
    response = api_client.get(
        '/health'
    )

    result = response.json()

    assert response.status_code == 200
    assert result['status'] == 'ok'
    assert result['model_loaded'] is True


def test_sentiment_prediction():
    response = api_client.post(
        '/api/v1/sentiment',
        json={
            'review_text': (
                'La comida estaba fría y '
                'el servicio fue demasiado lento.'
            )
        }
    )

    result = response.json()

    assert response.status_code == 200
    assert result['sentiment'] == 'Negativa'
    assert set(
        result['decision_scores']
    ) == {
        'Negativa',
        'Neutral',
        'Positiva'
    }


def test_invalid_review():
    response = api_client.post(
        '/api/v1/sentiment',
        json={
            'review_text': ' '
        }
    )

    assert response.status_code == 422


def test_documentation():
    response = api_client.get(
        '/docs'
    )

    assert response.status_code == 200
