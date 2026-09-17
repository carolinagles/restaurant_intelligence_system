
from html import escape

import pandas as pd
import streamlit as st


aspect_actions = {
    'Comida y sabor': {
        'action': (
            'Revisar los platos citados en las reseñas negativas y comprobar '
            'la consistencia del sabor, la temperatura y la presentación.'
        ),
        'measurement': (
            'Comprobar si disminuye el porcentaje de reseñas negativas que '
            'mencionan comida y sabor.'
        )
    },
    'Servicio y atención': {
        'action': (
            'Revisar la atención en horas de mayor demanda, la asignación de '
            'personal y los protocolos de seguimiento al cliente.'
        ),
        'measurement': (
            'Comprobar si disminuyen las menciones negativas sobre servicio '
            'en las reseñas posteriores.'
        )
    },
    'Ambiente': {
        'action': (
            'Revisar los comentarios sobre ruido, iluminación, comodidad, '
            'música, terraza y distribución del espacio.'
        ),
        'measurement': (
            'Comprobar si aumenta la proporción de reseñas positivas que '
            'mencionan el ambiente.'
        )
    },
    'Precio y valor': {
        'action': (
            'Revisar la relación percibida entre precio, porciones, calidad '
            'y experiencia, además de la claridad de la carta.'
        ),
        'measurement': (
            'Comprobar si disminuyen las menciones negativas relacionadas '
            'con precio y valor.'
        )
    },
    'Espera y rapidez': {
        'action': (
            'Medir los tiempos de espera y revisar la coordinación entre '
            'reservas, cocina y sala durante los periodos de mayor demanda.'
        ),
        'measurement': (
            'Comprobar si disminuyen las reseñas negativas que mencionan '
            'esperas, demoras o lentitud.'
        )
    },
    'Limpieza': {
        'action': (
            'Aplicar listas de comprobación y controles periódicos en sala, '
            'baños y zonas visibles para el cliente.'
        ),
        'measurement': (
            'Comprobar si dejan de aparecer menciones negativas sobre '
            'limpieza e higiene.'
        )
    }
}


def get_supported_aspects(
    review_aspects,
    item_id,
    minimum_mentions=5
):
    """Obtener temas con soporte mínimo."""

    return review_aspects.loc[
        review_aspects['item_id'].eq(str(item_id))
        & review_aspects['mentions'].ge(minimum_mentions)
    ].copy()


def get_temporal_drivers(aspects):
    """Obtener temas negativos que aumentaron recientemente."""

    required_columns = {
        'temporal_aspect_evaluable',
        'temporal_negative_change',
        'previous_mentions',
        'previous_negative_percentage',
        'recent_mentions',
        'recent_negative_reviews',
        'recent_negative_percentage'
    }
    if not required_columns.issubset(aspects.columns):
        return aspects.iloc[0:0].copy()

    return (
        aspects.loc[
            aspects['temporal_aspect_evaluable']
            & aspects['temporal_negative_change'].gt(0)
            & aspects['recent_negative_reviews'].gt(0)
        ]
        .sort_values(
            [
                'temporal_negative_change',
                'recent_negative_reviews',
                'recent_mentions'
            ],
            ascending=False
        )
        .copy()
    )


def get_reference_group(restaurant_groups):
    """Seleccionar el grupo con mayor soporte."""

    if restaurant_groups.empty:
        return None

    return (
        restaurant_groups
        .sort_values('group_restaurants', ascending=False)
        .iloc[0]
    )


def build_restaurant_insights(
    restaurant,
    restaurant_groups,
    review_aspects
):
    """Construir el plan de mejora y las fortalezas."""

    aspects = get_supported_aspects(
        review_aspects,
        restaurant['item_id']
    )
    priorities = []
    strengths = []
    reference_group = get_reference_group(restaurant_groups)
    temporal_drivers = get_temporal_drivers(aspects)
    temporal_driver_names = set(temporal_drivers['aspect'])

    if bool(restaurant['alert_evaluable']):
        alert_level = str(restaurant['alert_level'])
        if alert_level != 'Sin alerta':
            alert_scores = {
                'Vigilancia': 80,
                'Alerta alta': 90,
                'Alerta crítica': 100
            }
            minimum_reviews = int(
                restaurant['minimum_window_reviews']
            )
            priority_title = (
                'Atender el deterioro reciente'
                if minimum_reviews >= 10
                else 'Validar el deterioro reciente'
            )
            priorities.append(
                {
                    'title': priority_title,
                    'evidence': (
                        f"El rating cambió {restaurant['rating_change']:.2f} "
                        'puntos y las reseñas negativas cambiaron '
                        f"{restaurant['negative_percentage_point_change']:.2f} "
                        'puntos porcentuales. El soporte mínimo es de '
                        f'{minimum_reviews} reseñas por ventana.'
                    ),
                    'action': (
                        'Revisar las reseñas de la ventana reciente y '
                        'comprobar si el deterioro coincide con cambios en '
                        'personal, carta, horarios o funcionamiento.'
                    ),
                    'measurement': (
                        'Recalcular el indicador cuando existan nuevas '
                        'reseñas y comprobar si deja de cumplir los límites '
                        'de vigilancia.'
                    ),
                    'score': alert_scores.get(alert_level, 80)
                }
            )

            for row in temporal_drivers.head(2).itertuples():
                guidance = aspect_actions[row.aspect]
                priorities.append(
                    {
                        'title': f'Revisar {row.aspect.lower()}',
                        'evidence': (
                            'Las menciones negativas del tema aumentaron de '
                            f'{row.previous_negative_percentage:.1f} % en la '
                            'ventana anterior a '
                            f'{row.recent_negative_percentage:.1f} % en la '
                            'reciente '
                            f'({row.temporal_negative_change:+.1f} puntos). '
                            'Se observaron '
                            f'{int(row.previous_mentions)} y '
                            f'{int(row.recent_mentions)} menciones.'
                        ),
                        'action': guidance['action'],
                        'measurement': guidance['measurement'],
                        'score': 85 + row.temporal_negative_change
                    }
                )

    if not aspects.empty:
        aspects['negative_difference'] = (
            aspects['negative_percentage']
            - float(restaurant['negative_percentage'])
        )
        minimum_negative_percentage = max(
            20.00,
            float(restaurant['negative_percentage'])
        )
        negative_aspects = (
            aspects.loc[
                aspects['negative_reviews'].ge(3)
                & aspects['negative_percentage'].ge(
                    minimum_negative_percentage
                )
                & ~aspects['aspect'].isin(temporal_driver_names)
            ]
            .sort_values(
                [
                    'negative_difference',
                    'negative_reviews',
                    'mentions'
                ],
                ascending=False
            )
            .head(2)
        )

        for row in negative_aspects.itertuples():
            guidance = aspect_actions[row.aspect]
            priorities.append(
                {
                    'title': f'Mejorar {row.aspect.lower()}',
                    'evidence': (
                        f'{int(row.negative_reviews)} de las '
                        f'{int(row.mentions)} reseñas que mencionan este '
                        'tema son negativas '
                        f'({row.negative_percentage:.1f} %). El soporte es '
                        f'{row.support_level.lower()}.'
                    ),
                    'action': guidance['action'],
                    'measurement': guidance['measurement'],
                    'score': (
                        75
                        + max(0, row.negative_difference)
                        + min(row.mentions, 30) / 10
                    )
                }
            )

        aspects['positive_difference'] = (
            aspects['positive_percentage']
            - float(restaurant['positive_percentage'])
        )
        minimum_positive_percentage = max(
            50.00,
            float(restaurant['positive_percentage'])
        )
        positive_aspects = (
            aspects.loc[
                aspects['positive_reviews'].ge(3)
                & aspects['positive_percentage'].ge(
                    minimum_positive_percentage
                )
            ]
            .sort_values(
                [
                    'positive_difference',
                    'positive_reviews',
                    'mentions'
                ],
                ascending=False
            )
            .head(2)
        )

        for row in positive_aspects.itertuples():
            strengths.append(
                {
                    'title': row.aspect,
                    'evidence': (
                        f'{int(row.positive_reviews)} de las '
                        f'{int(row.mentions)} reseñas que mencionan este '
                        'tema son positivas '
                        f'({row.positive_percentage:.1f} %).'
                    )
                }
            )

    if reference_group is not None:
        if reference_group['rating_gap'] < -0.10:
            priorities.append(
                {
                    'title': 'Cerrar la brecha de rating',
                    'evidence': (
                        f"El rating está {abs(reference_group['rating_gap']):.2f} "
                        f"puntos por debajo del grupo "
                        f"{reference_group['group_label']}."
                    ),
                    'action': (
                        'Comparar los temas negativos del restaurante con '
                        'los indicadores del grupo y actuar primero sobre '
                        'el tema con mayor proporción negativa.'
                    ),
                    'measurement': (
                        'Volver a comparar el rating cuando se acumulen '
                        'nuevas reseñas y comprobar si la brecha disminuye.'
                    ),
                    'score': 60 + abs(reference_group['rating_gap']) * 10
                }
            )
        elif reference_group['rating_gap'] > 0.10:
            strengths.append(
                {
                    'title': 'Rating competitivo',
                    'evidence': (
                        f"Supera al grupo {reference_group['group_label']} "
                        f"por {reference_group['rating_gap']:.2f} puntos."
                    )
                }
            )

        if reference_group['negative_gap'] > 2.00:
            priorities.append(
                {
                    'title': 'Reducir las reseñas negativas',
                    'evidence': (
                        'La proporción negativa supera la referencia de '
                        'sus pares por '
                        f"{reference_group['negative_gap']:.2f} puntos "
                        'porcentuales.'
                    ),
                    'action': (
                        'Revisar primero los temas con mayor porcentaje '
                        'negativo y registrar las acciones aplicadas.'
                    ),
                    'measurement': (
                        'Comparar nuevamente el porcentaje negativo con el '
                        'grupo y comprobar si la diferencia disminuye.'
                    ),
                    'score': 60 + reference_group['negative_gap']
                }
            )
        elif reference_group['negative_gap'] < -2.00:
            strengths.append(
                {
                    'title': 'Menor proporción negativa que sus pares',
                    'evidence': (
                        'Se sitúa '
                        f"{abs(reference_group['negative_gap']):.2f} puntos "
                        'porcentuales por debajo del grupo.'
                    )
                }
            )

    priorities = sorted(
        priorities,
        key=lambda priority: priority['score'],
        reverse=True
    )[:3]

    if not priorities:
        priorities = [
            {
                'title': 'Mantener el seguimiento',
                'evidence': (
                    'No se detectan brechas cuantitativas relevantes con '
                    'el soporte disponible.'
                ),
                'action': (
                    'Continuar revisando las nuevas reseñas y conservar '
                    'los procesos asociados a las fortalezas observadas.'
                ),
                'measurement': (
                    'Actualizar el diagnóstico cuando se acumulen nuevas '
                    'reseñas y confirmar que los indicadores permanecen '
                    'estables.'
                ),
                'score': 0
            }
        ]

    if not strengths:
        strengths = [
            {
                'title': 'Evidencia todavía insuficiente',
                'evidence': (
                    'No existen al menos cinco menciones de un mismo tema '
                    'para identificar una fortaleza temática.'
                )
            }
        ]

    evidence_note = (
        'Los temas se detectan mediante palabras clave en las reseñas. La '
        'polaridad corresponde al sentimiento global de cada reseña. Las '
        'acciones son sugerencias operativas y no resultados causales.'
    )

    return priorities, strengths[:3], evidence_note


def render_deterioration_drivers(restaurant, review_aspects):
    """Explicar las señales asociadas al deterioro."""

    aspects = get_supported_aspects(
        review_aspects,
        restaurant['item_id']
    )
    drivers = get_temporal_drivers(aspects)

    st.markdown(
        '''
        <section class="driver-section">
            <span class="section-eyebrow">SEÑALES DE DETERIORO</span>
            <h2>Qué puede estar impulsando el cambio</h2>
            <p>
                Se comparan los temas negativos de la ventana anterior con
                los de la ventana reciente. El resultado orienta la revisión,
                pero no demuestra causalidad.
            </p>
        </section>
        ''',
        unsafe_allow_html=True
    )

    if not bool(restaurant['alert_evaluable']):
        st.info(
            'No existen al menos cinco reseñas en cada ventana para evaluar '
            'el cambio del restaurante. Esto significa falta de evidencia, '
            'no ausencia de riesgo.'
        )
        return

    if str(restaurant['alert_level']) == 'Sin alerta':
        st.success(
            'Las dos condiciones de deterioro no se cumplen simultáneamente: '
            'caída del rating y aumento de reseñas negativas.'
        )
        return

    if not {
        'temporal_aspect_evaluable',
        'temporal_negative_change'
    }.issubset(aspects.columns):
        st.warning(
            'El archivo temático debe actualizarse para mostrar las señales '
            'temporales. Ejecuta nuevamente la sección 7.7.1.'
        )
        return

    if drivers.empty:
        st.info(
            'El deterioro general está confirmado, pero ningún tema cuenta '
            'con al menos tres menciones en ambas ventanas. Conviene revisar '
            'directamente las reseñas recientes.'
        )
        return

    for row in drivers.head(3).itertuples():
        aspect = escape(str(row.aspect))
        st.markdown(
            f'''
            <article class="driver-card">
                <div>
                    <span class="card-label">TEMA A REVISAR</span>
                    <h3>{aspect}</h3>
                    <p>
                        La proporción negativa aumentó
                        <strong>{row.temporal_negative_change:+.1f} pp</strong>.
                    </p>
                </div>
                <div class="driver-comparison">
                    <div>
                        <span>VENTANA ANTERIOR</span>
                        <strong>{row.previous_negative_percentage:.1f} %</strong>
                        <small>{int(row.previous_mentions)} menciones</small>
                    </div>
                    <div class="driver-arrow">→</div>
                    <div>
                        <span>VENTANA RECIENTE</span>
                        <strong>{row.recent_negative_percentage:.1f} %</strong>
                        <small>{int(row.recent_mentions)} menciones</small>
                    </div>
                </div>
            </article>
            ''',
            unsafe_allow_html=True
        )

    st.caption(
        'Solo se muestran temas con al menos tres menciones en cada ventana. '
        'Un aumento indica asociación temporal, no una causa comprobada.'
    )


def build_actionable_summary(
    restaurant,
    restaurant_groups,
    review_aspects
):
    """Convertir los indicadores en una lectura operativa."""

    negative_percentage = float(restaurant['negative_percentage'])
    summary_parts = [
        f'El {negative_percentage:.1f} % de las reseñas del restaurante es '
        'negativo.'
    ]
    reference_group = get_reference_group(restaurant_groups)

    if reference_group is not None:
        negative_gap = float(reference_group['negative_gap'])
        comparison = 'más' if negative_gap > 0 else 'menos'
        if abs(negative_gap) < 0.05:
            summary_parts.append(
                'Su proporción negativa es prácticamente igual a la de sus '
                f"pares del grupo {reference_group['group_label']}."
            )
        else:
            summary_parts.append(
                f'Tiene {abs(negative_gap):.1f} puntos porcentuales {comparison} '
                'de reseñas negativas que sus pares del grupo '
                f"{reference_group['group_label']}."
            )
    else:
        summary_parts.append(
            'No dispone de un grupo competitivo elegible para calcular una '
            'brecha frente a pares.'
        )

    aspects = get_supported_aspects(
        review_aspects,
        restaurant['item_id']
    )
    drivers = get_temporal_drivers(aspects)
    selected_aspect = None

    if (
        bool(restaurant['alert_evaluable'])
        and str(restaurant['alert_level']) != 'Sin alerta'
        and not drivers.empty
    ):
        driver = drivers.iloc[0]
        selected_aspect = str(driver['aspect'])
        summary_parts.append(
            f'La señal reciente más clara se concentra en '
            f'"{selected_aspect}": su proporción negativa aumentó '
            f"{driver['temporal_negative_change']:.1f} puntos entre ventanas."
        )
    elif not aspects.empty:
        recurring_aspects = (
            aspects.loc[aspects['negative_reviews'].ge(3)]
            .sort_values(
                ['negative_percentage', 'negative_reviews'],
                ascending=False
            )
        )
        if not recurring_aspects.empty:
            recurring = recurring_aspects.iloc[0]
            selected_aspect = str(recurring['aspect'])
            summary_parts.append(
                f'El problema histórico con mayor concentración negativa es '
                f'"{selected_aspect}": '
                f"{recurring['negative_reviews']:.0f} de "
                f"{recurring['mentions']:.0f} menciones son negativas."
            )

    if selected_aspect is not None:
        summary_parts.append(
            'Prioridad sugerida: '
            + aspect_actions[selected_aspect]['action']
        )
    else:
        summary_parts.append(
            'No existe soporte temático suficiente para atribuir el problema '
            'a un área concreta; conviene revisar las reseñas recientes.'
        )

    return ' '.join(summary_parts)


def render_actionable_summary(
    restaurant,
    restaurant_groups,
    review_aspects
):
    """Mostrar la lectura ejecutiva accionable."""

    summary = escape(
        build_actionable_summary(
            restaurant,
            restaurant_groups,
            review_aspects
        )
    )
    st.markdown(
        f'''
        <article class="decision-summary">
            <span class="card-label">LECTURA PARA DECIDIR</span>
            <p>{summary}</p>
        </article>
        ''',
        unsafe_allow_html=True
    )


def render_restaurant_insights(
    restaurant,
    restaurant_groups,
    review_aspects
):
    """Mostrar el plan de mejora antes de las fortalezas."""

    priorities, strengths, evidence_note = build_restaurant_insights(
        restaurant,
        restaurant_groups,
        review_aspects
    )

    render_actionable_summary(
        restaurant,
        restaurant_groups,
        review_aspects
    )

    render_deterioration_drivers(
        restaurant,
        review_aspects
    )

    st.markdown(
        '''
        <section class="action-section">
            <span class="section-eyebrow">PLAN DE ACCIÓN</span>
            <h2>Qué mejorar primero</h2>
            <p>
                Prioridades ordenadas por gravedad, evidencia temática y
                brecha frente a restaurantes similares.
            </p>
        </section>
        ''',
        unsafe_allow_html=True
    )

    for position, priority in enumerate(priorities, start=1):
        title = escape(str(priority['title']))
        evidence = escape(str(priority['evidence']))
        action = escape(str(priority['action']))
        measurement = escape(str(priority['measurement']))
        st.markdown(
            f'''
            <article class="priority-card">
                <div class="priority-card__head">
                    <span class="priority-number">{position:02d}</span>
                    <div>
                        <span class="card-label">PRIORIDAD</span>
                        <h3>{title}</h3>
                    </div>
                </div>
                <div class="priority-evidence">
                    <span class="card-label">EVIDENCIA</span>
                    <p>{evidence}</p>
                </div>
                <div class="priority-grid">
                    <div>
                        <span class="card-label">ACCIÓN SUGERIDA</span>
                        <p>{action}</p>
                    </div>
                    <div>
                        <span class="card-label">CÓMO MEDIRLA</span>
                        <p>{measurement}</p>
                    </div>
                </div>
            </article>
            ''',
            unsafe_allow_html=True
        )

    st.markdown(
        '''
        <section class="strength-section">
            <span class="section-eyebrow">FORTALEZAS</span>
            <h2>Qué conviene conservar</h2>
        </section>
        ''',
        unsafe_allow_html=True
    )
    for strength in strengths:
        title = escape(str(strength['title']))
        evidence = escape(str(strength['evidence']))
        st.markdown(
            f'''
            <article class="strength-card">
                <span class="card-label">FORTALEZA OBSERVADA</span>
                <h3>{title}</h3>
                <p>{evidence}</p>
            </article>
            ''',
            unsafe_allow_html=True
        )

    with st.expander('Cómo se generan las recomendaciones'):
        st.write(evidence_note)
        st.write(
            'Solo se interpretan temas con al menos cinco reseñas que los '
            'mencionan. Los indicadores temporales y competitivos se muestran '
            'únicamente cuando cuentan con el soporte definido en el análisis.'
        )
