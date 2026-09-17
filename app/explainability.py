
from time import perf_counter

import numpy as np
from lime.lime_text import LimeTextExplainer

from app.inference import (
    load_sentiment_model,
    validate_review_text
)


random_state = 42


def predict_normalized_scores(
    review_texts
):
    """Normalizar los márgenes del modelo."""

    sentiment_model = (
        load_sentiment_model()
    )

    decision_scores = (
        sentiment_model.decision_function(
            review_texts
        )
    )

    shifted_scores = (
        decision_scores
        - decision_scores.max(
            axis=1,
            keepdims=True
        )
    )

    exponential_scores = np.exp(
        shifted_scores
    )

    return (
        exponential_scores
        / exponential_scores.sum(
            axis=1,
            keepdims=True
        )
    )


def explain_sentiment(
    review_text: str,
    num_features: int = 10,
    num_samples: int = 1_000
) -> dict:
    """Explicar una predicción con LIME."""

    normalized_text = validate_review_text(
        review_text
    )

    sentiment_model = (
        load_sentiment_model()
    )

    sentiment_classes = [
        str(sentiment_class)
        for sentiment_class in (
            sentiment_model
            .named_steps['classifier']
            .classes_
        )
    ]

    predicted_sentiment = str(
        sentiment_model.predict(
            [normalized_text]
        )[0]
    )

    predicted_class_index = (
        sentiment_classes.index(
            predicted_sentiment
        )
    )

    lime_explainer = LimeTextExplainer(
        class_names=sentiment_classes,
        random_state=random_state
    )

    start_time = perf_counter()

    explanation = (
        lime_explainer.explain_instance(
            text_instance=normalized_text,
            classifier_fn=(
                predict_normalized_scores
            ),
            labels=[
                predicted_class_index
            ],
            num_features=num_features,
            num_samples=num_samples
        )
    )

    explanation_seconds = (
        perf_counter() - start_time
    )

    terms = [
        {
            'term': term,
            'contribution': round(
                float(contribution),
                4
            ),
            'effect': (
                f'Apoya {predicted_sentiment}'
                if contribution > 0
                else (
                    f'Contradice '
                    f'{predicted_sentiment}'
                )
            )
        }
        for term, contribution
        in explanation.as_list(
            label=predicted_class_index
        )
    ]

    return {
        'sentiment': predicted_sentiment,
        'normalized_class_score': round(
            float(
                explanation.predict_proba[
                    predicted_class_index
                ]
            ),
            4
        ),
        'local_fidelity_r2': round(
            float(explanation.score),
            4
        ),
        'explanation_seconds': round(
            explanation_seconds,
            4
        ),
        'terms': terms
    }
