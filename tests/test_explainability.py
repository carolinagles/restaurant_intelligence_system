
from app.explainability import (
    explain_sentiment
)


def test_sentiment_explanation():
    result = explain_sentiment(
        (
            'La comida estaba fría, '
            'el servicio fue demasiado lento '
            'y la atención fue muy mala.'
        )
    )

    assert result['sentiment'] == 'Negativa'

    assert (
        0
        <= result['normalized_class_score']
        <= 1
    )

    assert (
        0
        <= result['local_fidelity_r2']
        <= 1
    )

    assert len(
        result['terms']
    ) == 10

    assert all(
        {
            'term',
            'contribution',
            'effect'
        }.issubset(term_result)
        for term_result in result['terms']
    )
