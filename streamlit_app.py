
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.explainability import explain_sentiment
from app.inference import predict_sentiment
from app.insights import render_restaurant_insights
from app.ui import apply_style, render_header, style_figure
from app.benchmarking import (
    build_executive_summary,
    get_restaurant_groups,
    render_benchmarking,
    render_market_explorer
)


project_path = Path(__file__).resolve().parent
data_path = project_path / 'data'
primary_color = '#05402B'
sentiment_colors = {
    'Negativa': '#8B1E1E',
    'Neutral': '#A8874F',
    'Positiva': primary_color
}

st.set_page_config(
    page_title='Madrid Restaurant Intelligence',
    layout='wide'
)
apply_style()


@st.cache_data
def load_project_data():
    """Cargar los productos analíticos."""

    diagnostics = pd.read_parquet(
        data_path / 'restaurant_diagnostics.parquet'
    )
    membership = pd.read_parquet(
        data_path / 'benchmark_membership.parquet'
    )
    groups = pd.read_parquet(
        data_path / 'benchmark_groups.parquet'
    ).rename(
        columns={
            'restaurants': 'group_restaurants',
            'reviews': 'group_reviews'
        }
    )
    review_aspects = pd.read_parquet(
        data_path / 'restaurant_review_aspects.parquet'
    )

    diagnostics['item_id'] = diagnostics['item_id'].astype(str)
    membership['item_id'] = membership['item_id'].astype(str)
    review_aspects['item_id'] = review_aspects['item_id'].astype(str)

    for data_frame in [membership, groups]:
        data_frame['specialty'] = data_frame['specialty'].astype(str)
        data_frame['price_interval'] = (
            data_frame['price_interval'].astype(str)
        )

    diagnostics['restaurant_label'] = (
        diagnostics['name'].astype(str)
        + ' | '
        + diagnostics['item_id']
    )

    group_metrics = (
        membership
        .merge(
            diagnostics[
                ['item_id', 'mean_review_rating', 'negative_percentage']
            ],
            on='item_id',
            how='left',
            validate='many_to_one'
        )
        .groupby(
            ['specialty', 'price_interval'],
            as_index=False,
            observed=True
        )
        .agg(
            group_mean_rating=('mean_review_rating', 'mean'),
            group_negative_percentage=('negative_percentage', 'mean')
        )
    )
    groups = groups.merge(
        group_metrics,
        on=['specialty', 'price_interval'],
        how='left',
        validate='one_to_one'
    )
    return diagnostics, membership, groups, review_aspects


def format_number(value, decimals=2, suffix=''):
    """Formatear un indicador."""

    if pd.isna(value):
        return 'No disponible'
    return f'{float(value):,.{decimals}f}{suffix}'


try:
    diagnostics, membership, groups, review_aspects = load_project_data()
except Exception as error:
    st.error(f'No fue posible cargar los datos: {error}')
    st.stop()

active_levels = ['Vigilancia', 'Alerta alta', 'Alerta crítica']
alert_names = {
    'Sin alerta': 'Estable',
    'Vigilancia': 'Vigilancia',
    'Alerta alta': 'Deterioro alto',
    'Alerta crítica': 'Deterioro severo',
    'No evaluable': 'Sin datos temporales suficientes'
}
render_header()

# Navegar entre las dos vistas principales
if 'active_page' not in st.session_state:
    st.session_state['active_page'] = 'restaurant'

st.sidebar.markdown('### Navegación')
if st.sidebar.button(
    'Diagnóstico del restaurante',
    use_container_width=True,
    type=(
        'primary'
        if st.session_state['active_page'] == 'restaurant'
        else 'secondary'
    )
):
    st.session_state['active_page'] = 'restaurant'

if st.sidebar.button(
    'Explorar competencia · Top 10',
    use_container_width=True,
    type=(
        'primary'
        if st.session_state['active_page'] == 'market'
        else 'secondary'
    )
):
    st.session_state['active_page'] = 'market'

st.sidebar.divider()

if st.session_state['active_page'] == 'market':
    render_market_explorer(
        groups,
        membership,
        diagnostics
    )
    st.divider()
    st.caption('TFM | Ciencia de Datos, Big Data y Business Analytics')
    st.stop()

# Indicadores generales
evaluable_count = int(diagnostics['alert_evaluable'].sum())
temporal_coverage = evaluable_count / len(diagnostics) * 100
overview = st.columns(4)
overview[0].metric('Restaurantes', f"{diagnostics['item_id'].nunique():,}")
overview[1].metric('Reseñas', f"{diagnostics['reviews'].sum():,}")
overview[2].metric('Grupos competitivos', f'{len(groups):,}')
overview[3].metric(
    'Cobertura temporal',
    f'{evaluable_count:,} ({temporal_coverage:.1f} %)'
)

with st.expander('Cómo interpretar toda la aplicación'):
    st.markdown(
        '- **Diagnóstico:** resume el historial completo de reseñas.\n'
        '- **Pares:** comparten especialidad y rango de precio.\n'
        '- **Brecha de rating:** positiva significa mejor desempeño.\n'
        '- **Brecha de negativas:** positiva significa peor desempeño.\n'
        '- **Monitoreo temporal:** compara dos ventanas consecutivas.\n'
        '- **Sin datos temporales suficientes:** no es una alerta.\n'
        '- **Temas de reseñas:** requieren al menos cinco menciones.\n'
        '- **Modelo de texto:** su puntuación normalizada no es una '
        'probabilidad calibrada.'
    )

# Restaurante seleccionado
restaurant_search = st.sidebar.text_input(
    'Buscar restaurante',
    placeholder='Escribe el nombre'
).strip()

if restaurant_search:
    filtered_restaurants = diagnostics.loc[
        diagnostics['name'].astype(str).str.contains(
            restaurant_search,
            case=False,
            na=False,
            regex=False
        )
    ]
else:
    filtered_restaurants = diagnostics

if filtered_restaurants.empty:
    st.sidebar.warning('No se encontraron restaurantes con ese nombre.')
    filtered_restaurants = diagnostics

restaurant_options = (
    filtered_restaurants
    .sort_values(['name', 'item_id'])['restaurant_label']
    .tolist()
)
selected_label = st.sidebar.selectbox('Resultados', restaurant_options)
restaurant = diagnostics.loc[
    diagnostics['restaurant_label'].eq(selected_label)
].iloc[0]

restaurant_groups = get_restaurant_groups(
    restaurant,
    membership,
    groups
)

(
    diagnosis_tab,
    benchmark_tab,
    alerts_tab,
    review_tab,
    methodology_tab
) = st.tabs(
    [
        'Diagnóstico',
        'Comparación con pares',
        'Alertas del mercado',
        'Analizar reseña',
        'Cómo se calcula'
    ]
)


with diagnosis_tab:
    st.header(str(restaurant['name']))

    metrics = st.columns(4)
    metrics[0].metric('Reseñas', f"{int(restaurant['reviews']):,}")
    metrics[1].metric(
        'Rating medio',
        format_number(restaurant['mean_review_rating'])
    )
    metrics[2].metric(
        'Positivas',
        format_number(restaurant['positive_percentage'], suffix='%')
    )
    metrics[3].metric(
        'Negativas',
        format_number(restaurant['negative_percentage'], suffix='%')
    )
    st.caption(
        f"Soporte: {restaurant['diagnostic_support']} | "
        f"Estado: {restaurant['diagnostic_status']}"
    )

    with st.expander('Qué significan estos indicadores'):
        st.markdown(
            '- **Reseñas:** volumen histórico disponible.\n'
            '- **Rating medio:** promedio de valoraciones entre 1 y 5.\n'
            '- **Positivas y negativas:** distribución del sentimiento '
            'derivada de la valoración.\n'
            '- **Soporte:** estabilidad esperada según el número de reseñas.'
        )

    st.subheader('Lectura ejecutiva')
    st.info(
        build_executive_summary(
            restaurant,
            restaurant_groups
        )
    )

    alert_metrics = st.columns(4)
    displayed_alert = alert_names.get(
        str(restaurant['alert_level']),
        str(restaurant['alert_level'])
    )
    alert_metrics[0].metric('Estado temporal', displayed_alert)
    alert_metrics[1].metric(
        'Acción recomendada',
        str(restaurant['operational_priority'])
    )
    alert_metrics[2].metric(
        'Cambio rating',
        format_number(restaurant['rating_change'])
    )
    alert_metrics[3].metric(
        'Cambio negativas',
        format_number(
            restaurant['negative_percentage_point_change'],
            suffix=' pp'
        )
    )

    st.caption(
        'El cambio compara la ventana reciente con la anterior. Un descenso '
        'del rating y un aumento de negativas indican deterioro.'
    )

    render_restaurant_insights(
        restaurant,
        restaurant_groups,
        review_aspects
    )

    with st.expander('Ver distribución histórica del sentimiento'):
        sentiment_data = pd.DataFrame(
            {
                'Sentimiento': ['Negativa', 'Neutral', 'Positiva'],
                'Porcentaje': [
                    restaurant['negative_percentage'],
                    restaurant['neutral_percentage'],
                    restaurant['positive_percentage']
                ]
            }
        )
        sentiment_figure = px.bar(
            sentiment_data,
            x='Sentimiento',
            y='Porcentaje',
            color='Sentimiento',
            color_discrete_map=sentiment_colors
        )
        sentiment_figure.update_layout(showlegend=False)
        st.plotly_chart(
            style_figure(sentiment_figure),
            use_container_width=True
        )
        st.caption(
            'La gráfica muestra la distribución histórica, no únicamente '
            'el periodo reciente.'
        )


with benchmark_tab:
    render_benchmarking(
        restaurant,
        restaurant_groups,
        membership,
        diagnostics
    )


with alerts_tab:
    st.header('Monitoreo temporal de la reputación')

    st.info(
        'Solo se evalúan restaurantes con al menos cinco reseñas en cada '
        'ventana. Los demás no tienen una alerta: carecen de soporte temporal.'
    )

    evaluable = diagnostics.loc[diagnostics['alert_evaluable']]
    signals = evaluable.loc[evaluable['alert_level'].isin(active_levels)]
    stable = evaluable['alert_level'].eq('Sin alerta').sum()

    alert_overview = st.columns(4)
    alert_overview[0].metric(
        'Cobertura',
        f'{len(evaluable):,} ({len(evaluable) / len(diagnostics) * 100:.1f} %)'
    )
    alert_overview[1].metric('Estables', f'{stable:,}')
    alert_overview[2].metric('Con señal', f'{len(signals):,}')
    alert_overview[3].metric(
        'Deterioro severo',
        f"{evaluable['alert_level'].eq('Alerta crítica').sum():,}"
    )

    with st.expander('Qué significa cada nivel'):
        st.markdown(
            '- **Vigilancia:** rating −0.40 o más y negativas +10 puntos '
            'porcentuales o más.\n'
            '- **Deterioro alto:** rating −0.80 o más y negativas +20 puntos.\n'
            '- **Deterioro severo:** rating −1.00 o más y negativas +30 puntos.\n'
            '- Las dos condiciones deben cumplirse. La señal describe un '
            'cambio observado y no predice el futuro.'
        )

    selected_levels = st.multiselect(
        'Filtrar señales',
        active_levels,
        default=['Alerta alta', 'Alerta crítica'],
        format_func=lambda level: alert_names[level]
    )
    alert_table = (
        signals.loc[
            signals['alert_level'].isin(selected_levels),
            [
                'name',
                'price_interval',
                'recent_reviews',
                'rating_change',
                'negative_percentage_point_change',
                'alert_level',
                'operational_priority'
            ]
        ]
        .sort_values('rating_change')
        .rename(
            columns={
                'name': 'Restaurante',
                'price_interval': 'Precio',
                'recent_reviews': 'Reseñas recientes',
                'rating_change': 'Cambio rating',
                'negative_percentage_point_change': 'Cambio negativas (pp)',
                'alert_level': 'Alerta',
                'operational_priority': 'Prioridad'
            }
        )
    )
    alert_table['Alerta'] = alert_table['Alerta'].map(alert_names)
    st.dataframe(
        alert_table.round(2),
        hide_index=True,
        use_container_width=True
    )


with review_tab:
    st.header('Clasificación explicable de una reseña')

    with st.expander('Qué analiza el modelo'):
        st.markdown(
            '- Clasifica el texto como **Negativa**, **Neutral** o '
            '**Positiva**.\n'
            '- La puntuación normalizada facilita la comparación entre '
            'clases, pero no es una probabilidad.\n'
            '- LIME muestra qué términos apoyan o contradicen la clase '
            'predicha.\n'
            '- La explicación corresponde únicamente a la reseña escrita.'
        )

    review_text = st.text_area(
        'Texto de la reseña',
        value='La comida estaba fría y el servicio fue demasiado lento.',
        height=140,
        max_chars=5_000
    )

    if st.button('Analizar reseña', type='primary'):
        try:
            prediction = predict_sentiment(review_text)
            explanation = explain_sentiment(review_text)
        except Exception as error:
            st.error(f'No fue posible analizar la reseña: {error}')
        else:
            sentiment = prediction['sentiment']
            message_method = {
                'Negativa': st.error,
                'Neutral': st.warning,
                'Positiva': st.success
            }[sentiment]
            message_method(f'Sentimiento: {sentiment}')

            explanation_metrics = st.columns(3)
            explanation_metrics[0].metric(
                'Puntuación normalizada',
                format_number(explanation['normalized_class_score'], 4)
            )
            explanation_metrics[1].metric(
                'Fidelidad local R²',
                format_number(explanation['local_fidelity_r2'], 4)
            )
            explanation_metrics[2].metric(
                'Inferencia',
                format_number(
                    prediction['prediction_milliseconds'],
                    2,
                    ' ms'
                )
            )

            contribution_rows = explanation.get(
                'contributions',
                explanation.get('terms', [])
            )
            contributions = pd.DataFrame(contribution_rows)
            contributions['Dirección'] = (
                contributions['contribution']
                .gt(0)
                .map({True: 'Apoya', False: 'Contradice'})
            )
            lime_figure = px.bar(
                contributions.sort_values('contribution'),
                x='contribution',
                y='term',
                color='Dirección',
                orientation='h',
                color_discrete_map={
                    'Apoya': primary_color,
                    'Contradice': '#A8B6AE'
                },
                labels={
                    'contribution': 'Contribución',
                    'term': 'Término'
                }
            )
            st.plotly_chart(
                style_figure(lime_figure),
                use_container_width=True
            )
            st.caption(
                'La puntuación normalizada no es una probabilidad calibrada.'
            )


with methodology_tab:
    st.header('Cómo se calcula cada resultado')
    st.info(
        'Esta sección explica el origen, el cálculo y los límites de todos '
        'los indicadores de la aplicación.'
    )

    with st.expander('1. Datos utilizados', expanded=True):
        st.markdown(
            f'- Se utilizan **{diagnostics["reviews"].sum():,} reseñas** de '
            f'**{diagnostics["item_id"].nunique():,} restaurantes** de Madrid.\n'
            '- Se conservaron reseñas en español e inglés.\n'
            '- Los duplicados y registros fuera de las reglas de calidad se '
            'corrigieron en el Notebook 1.\n'
            '- El Notebook 2 construyó el diagnóstico, los grupos competitivos '
            'y las ventanas temporales.\n'
            '- El Notebook 3 entrenó el modelo de sentimiento y construyó '
            'esta aplicación.'
        )

    with st.expander('2. Diagnóstico histórico'):
        st.markdown(
            '- **Rating medio:** promedio de las valoraciones de todas las '
            'reseñas del restaurante, expresado entre 1 y 5.\n'
            '- **Negativa:** valoración 1 o 2.\n'
            '- **Neutral:** valoración 3.\n'
            '- **Positiva:** valoración 4 o 5.\n'
            '- **Soporte muy bajo:** 1–9 reseñas; **bajo:** 10–29; '
            '**adecuado:** 30–99; **alto:** 100 o más.\n'
            '- El soporte indica cuánta evidencia respalda el diagnóstico; '
            'no califica la calidad del restaurante.'
        )

    with st.expander('3. Comparación con pares'):
        st.markdown(
            '- Un par comparte **especialidad** y **rango de precio**.\n'
            '- Un grupo competitivo se conserva si contiene al menos '
            '**30 restaurantes y 1,000 reseñas**.\n'
            '- **Brecha de rating = rating del restaurante − rating del grupo.** '
            'Un valor positivo es favorable.\n'
            '- **Brecha de negativas = % negativo del restaurante − % negativo '
            'del grupo.** Un valor positivo es desfavorable.\n'
            '- Los promedios del grupo se calculan a nivel de restaurante para '
            'que el volumen de un solo establecimiento no domine el resultado.'
        )

    with st.expander('4. Alertas de deterioro'):
        st.markdown(
            '- Se excluye el último mes observado porque puede estar incompleto.\n'
            '- Se comparan dos ventanas consecutivas de **seis meses completos**.\n'
            '- Un restaurante es evaluable si tiene al menos **cinco reseñas '
            'en cada ventana**.\n'
            '- **Cambio de rating = rating reciente − rating anterior.**\n'
            '- **Cambio de negativas = % negativo reciente − % negativo '
            'anterior.**\n'
            '- **Vigilancia:** rating ≤ −0.40 y negativas ≥ +10 puntos.\n'
            '- **Deterioro alto:** rating ≤ −0.80 y negativas ≥ +20 puntos.\n'
            '- **Deterioro severo:** rating ≤ −1.00 y negativas ≥ +30 puntos.\n'
            '- Las dos condiciones deben cumplirse simultáneamente.\n'
            '- **Sin datos temporales suficientes no es una alerta:** significa '
            'que no existe evidencia suficiente para evaluar el cambio.\n'
            '- La alerta describe un deterioro observado; no predice que '
            'continuará en el futuro.'
        )

    with st.expander('5. Temas asociados al deterioro'):
        st.markdown(
            '- Se buscan expresiones en español e inglés relacionadas con '
            'comida, servicio, ambiente, precio, espera y limpieza.\n'
            '- Para mostrar un tema temporal se exigen al menos **tres '
            'menciones en cada ventana**.\n'
            '- Se compara el porcentaje de reseñas negativas que menciona '
            'cada tema entre ambas ventanas.\n'
            '- Un aumento ayuda a identificar qué revisar, pero representa '
            'una **asociación temporal y no una causa comprobada**.\n'
            '- Si no existe soporte temático, la aplicación recomienda revisar '
            'directamente las reseñas recientes.'
        )

    with st.expander('6. Recomendaciones operativas'):
        st.markdown(
            '- Se combinan cuatro evidencias: gravedad de la alerta, cambio '
            'temático, problemas históricos y brecha frente a pares.\n'
            '- Las evidencias se ordenan y se muestran hasta tres prioridades.\n'
            '- Cada prioridad incluye el dato observado, una acción sugerida '
            'y la forma de comprobar si mejora.\n'
            '- Las acciones son reglas transparentes de apoyo a la decisión; '
            'deben validarse con la operación real del restaurante.'
        )

    with st.expander('7. Modelo de sentimiento y LIME'):
        st.markdown(
            '- El modelo final es **TF-IDF + LinearSVC**, seleccionado mediante '
            'validación y evaluado una sola vez sobre prueba.\n'
            '- En prueba obtuvo `accuracy=0.9048`, `macro_f1=0.8078` y '
            '`negative_recall=0.8793`.\n'
            '- LIME modifica localmente el texto para estimar qué palabras '
            'apoyan o contradicen la predicción.\n'
            '- La puntuación normalizada facilita la lectura, pero no es una '
            'probabilidad calibrada ni explica el restaurante completo.'
        )


st.divider()
st.caption('TFM | Ciencia de Datos, Big Data y Business Analytics')
