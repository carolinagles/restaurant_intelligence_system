
import pandas as pd
import plotly.express as px
import streamlit as st

from app.ui import style_figure


primary_color = '#05402B'

top_ten_rules = {
    'Mejor rating': ('mean_review_rating', False, 'Rating'),
    'Mayor porcentaje positivo': (
        'positive_percentage',
        False,
        'Positivas'
    ),
    'Mayor volumen de reseñas': ('reviews', False, 'Reseñas'),
    'Mayor mejora reciente': ('rating_change', False, 'Cambio'),
    'Mayor deterioro reciente': ('rating_change', True, 'Cambio')
}

criterion_explanations = {
    'Mejor rating': (
        'Ordena por la valoración media de las reseñas. Un valor mayor indica '
        'una mejor experiencia general reportada por los clientes.'
    ),
    'Mayor porcentaje positivo': (
        'Ordena por la proporción de reseñas clasificadas como positivas. '
        'Permite comparar consistencia, no solo el promedio de estrellas.'
    ),
    'Mayor volumen de reseñas': (
        'Ordena por cantidad de reseñas. Refleja visibilidad y actividad, '
        'pero un volumen alto no implica mejor calidad.'
    ),
    'Mayor mejora reciente': (
        'Ordena por el aumento del rating entre dos ventanas consecutivas de '
        'seis meses completos. Solo incluye restaurantes evaluables.'
    ),
    'Mayor deterioro reciente': (
        'Ordena por la mayor caída del rating entre las dos ventanas. Es una '
        'señal de cambio observado, no una predicción.'
    )
}


def get_restaurant_groups(restaurant, membership, groups):
    """Obtener los grupos del restaurante."""

    restaurant_groups = (
        membership.loc[
            membership['item_id'].eq(restaurant['item_id'])
        ]
        .merge(
            groups,
            on=['specialty', 'price_interval'],
            how='left',
            validate='many_to_one'
        )
    )

    if restaurant_groups.empty:
        return restaurant_groups

    restaurant_groups['group_label'] = (
        restaurant_groups['specialty']
        + ' | '
        + restaurant_groups['price_interval']
    )
    restaurant_groups['rating_gap'] = (
        restaurant['mean_review_rating']
        - restaurant_groups['group_mean_rating']
    )
    restaurant_groups['negative_gap'] = (
        restaurant['negative_percentage']
        - restaurant_groups['group_negative_percentage']
    )
    return restaurant_groups


def get_group_restaurants(
    specialty,
    price_interval,
    membership,
    diagnostics,
    minimum_reviews=30
):
    """Obtener restaurantes comparables."""

    group_members = membership.loc[
        membership['specialty'].eq(specialty)
        & membership['price_interval'].eq(price_interval),
        ['item_id']
    ].drop_duplicates()

    return (
        group_members
        .merge(
            diagnostics,
            on='item_id',
            how='left',
            validate='one_to_one'
        )
        .loc[lambda data: data['reviews'].ge(minimum_reviews)]
        .copy()
    )


def build_executive_summary(restaurant, restaurant_groups):
    """Explicar el diagnóstico principal."""

    support_text = (
        f"El diagnóstico se basa en {int(restaurant['reviews']):,} reseñas "
        f"y tiene soporte {restaurant['diagnostic_support']}."
    )

    if restaurant_groups.empty:
        comparison_text = (
            ' No existe un grupo competitivo elegible para este restaurante.'
        )
    else:
        group = (
            restaurant_groups
            .sort_values('group_restaurants', ascending=False)
            .iloc[0]
        )
        rating_gap = float(group['rating_gap'])
        negative_gap = float(group['negative_gap'])
        rating_text = (
            f"supera a sus pares por {abs(rating_gap):.2f} puntos"
            if rating_gap >= 0
            else f"está por debajo de sus pares por {abs(rating_gap):.2f} puntos"
        )
        negative_text = (
            f"tiene {abs(negative_gap):.2f} puntos porcentuales menos de negativas"
            if negative_gap <= 0
            else f"tiene {abs(negative_gap):.2f} puntos porcentuales más de negativas"
        )
        comparison_text = (
            f" Frente al grupo {group['group_label']}, {rating_text} y "
            f"{negative_text}."
        )

    if not bool(restaurant['alert_evaluable']):
        alert_text = (
            ' La evolución reciente todavía no puede evaluarse con soporte suficiente.'
        )
    elif restaurant['alert_level'] == 'Sin alerta':
        alert_text = ' No se detectan señales recientes de deterioro.'
    else:
        alert_text = (
            f" La señal actual es {restaurant['alert_level']} y la prioridad "
            f"es {restaurant['operational_priority']}."
        )

    return support_text + comparison_text + alert_text


def render_benchmarking(
    restaurant,
    restaurant_groups,
    membership,
    diagnostics
):
    """Mostrar la comparación con pares."""

    st.header('Comparación con grupos similares')

    with st.expander('Qué significa esta comparación'):
        st.markdown(
            '- **Pares:** restaurantes de la misma especialidad y rango de '
            'precio.\n'
            '- **Posición:** lugar por rating entre pares con al menos 30 '
            'reseñas.\n'
            '- **Brecha de rating:** positiva significa mejor desempeño.\n'
            '- **Brecha de negativas:** positiva significa peor desempeño.'
        )

    if restaurant_groups.empty:
        st.info('El restaurante no pertenece a un grupo competitivo elegible.')
        return

    selected_label = st.selectbox(
        'Grupo de comparación',
        restaurant_groups['group_label'].tolist(),
        key='benchmark_group'
    )
    group = restaurant_groups.loc[
        restaurant_groups['group_label'].eq(selected_label)
    ].iloc[0]

    peers = get_group_restaurants(
        group['specialty'],
        group['price_interval'],
        membership,
        diagnostics
    )
    ranked_peers = (
        peers
        .dropna(subset=['mean_review_rating'])
        .sort_values(
            ['mean_review_rating', 'reviews'],
            ascending=[False, False]
        )
        .reset_index(drop=True)
    )
    rank_match = ranked_peers.index[
        ranked_peers['item_id'].eq(restaurant['item_id'])
    ].tolist()
    position = (
        f'{rank_match[0] + 1} de {len(ranked_peers)}'
        if rank_match
        else 'Sin soporte'
    )

    metrics = st.columns(4)
    metrics[0].metric('Posición', position)
    metrics[1].metric('Pares con soporte', f'{len(ranked_peers):,}')
    metrics[2].metric('Brecha de rating', f"{group['rating_gap']:.2f}")
    metrics[3].metric(
        'Brecha de negativas',
        f"{group['negative_gap']:.2f} pp"
    )

    rating_data = pd.DataFrame(
        {
            'Referencia': ['Restaurante', 'Pares'],
            'Valor': [
                restaurant['mean_review_rating'],
                group['group_mean_rating']
            ]
        }
    )
    negative_data = pd.DataFrame(
        {
            'Referencia': ['Restaurante', 'Pares'],
            'Valor': [
                restaurant['negative_percentage'],
                group['group_negative_percentage']
            ]
        }
    )

    rating_column, negative_column = st.columns(2)
    rating_figure = px.bar(
        rating_data,
        x='Referencia',
        y='Valor',
        color='Referencia',
        text='Valor',
        title='Rating medio: mayor es mejor',
        color_discrete_map={
            'Restaurante': primary_color,
            'Pares': '#B8C8BB'
        }
    )
    rating_figure.update_traces(
        texttemplate='%{text:.2f}',
        textposition='outside'
    )
    rating_figure.update_layout(showlegend=False)
    rating_figure.update_yaxes(range=[0, 5.4])
    rating_column.plotly_chart(
        style_figure(rating_figure),
        use_container_width=True
    )

    negative_figure = px.bar(
        negative_data,
        x='Referencia',
        y='Valor',
        color='Referencia',
        text='Valor',
        title='Reseñas negativas: menor es mejor',
        color_discrete_map={
            'Restaurante': '#8B1E1E',
            'Pares': '#D8D3C8'
        }
    )
    negative_figure.update_traces(
        texttemplate='%{text:.2f}%',
        textposition='outside'
    )
    negative_figure.update_layout(showlegend=False)
    negative_figure.update_yaxes(
        range=[0, min(100, max(20, negative_data['Valor'].max() * 1.25))]
    )
    negative_column.plotly_chart(
        style_figure(negative_figure),
        use_container_width=True
    )

    if group['rating_gap'] < 0 and group['negative_gap'] > 0:
        message = (
            'Prioridad de mejora: elevar el rating y reducir las reseñas '
            'negativas para cerrar la brecha con los pares.'
        )
    elif group['rating_gap'] < 0:
        message = (
            'El porcentaje negativo es competitivo, pero el rating permanece '
            'por debajo del grupo.'
        )
    elif group['negative_gap'] > 0:
        message = (
            'El rating es competitivo, pero las reseñas negativas superan '
            'la referencia del grupo.'
        )
    else:
        message = (
            'El restaurante supera a sus pares en rating y en proporción '
            'de reseñas negativas.'
        )
    st.info(message)

    with st.expander('Ver todos los grupos del restaurante'):
        table = restaurant_groups[
            [
                'group_label',
                'group_restaurants',
                'group_reviews',
                'rating_gap',
                'negative_gap'
            ]
        ].rename(
            columns={
                'group_label': 'Grupo competitivo',
                'group_restaurants': 'Restaurantes',
                'group_reviews': 'Reseñas',
                'rating_gap': 'Brecha de rating',
                'negative_gap': 'Brecha de negativas'
            }
        )
        st.dataframe(
            table.round(2),
            hide_index=True,
            use_container_width=True
        )


def get_top_ranking(
    specialty,
    price_interval,
    criterion,
    membership,
    diagnostics
):
    """Construir el ranking del grupo."""

    column, ascending, label = top_ten_rules[criterion]
    ranking = get_group_restaurants(
        specialty,
        price_interval,
        membership,
        diagnostics
    ).dropna(subset=[column])
    if column == 'rating_change':
        ranking = ranking.loc[ranking['alert_evaluable']]
    ranking = (
        ranking
        .sort_values(
            [column, 'reviews'],
            ascending=[ascending, False]
        )
        .reset_index(drop=True)
    )
    ranking['position'] = ranking.index + 1
    return ranking, column, label


def render_market_explorer(
    groups,
    membership,
    diagnostics
):
    """Mostrar el explorador competitivo."""

    specialties = sorted(groups['specialty'].dropna().unique())

    st.markdown(
        '''
        <section class="market-hero">
            <span class="section-eyebrow">EXPLORADOR DE MERCADO</span>
            <h1>Conoce la competencia de Madrid</h1>
            <p>
                Compara restaurantes de la misma especialidad y rango de
                precio. Cambia los filtros para descubrir referentes,
                volumen de actividad y señales recientes del mercado.
            </p>
        </section>
        ''',
        unsafe_allow_html=True
    )

    guide_columns = st.columns(3)
    guide_columns[0].info(
        '**Quiénes son comparables**\n\n'
        'Restaurantes que comparten especialidad y rango de precio.'
    )
    guide_columns[1].info(
        '**Qué entra al ranking**\n\n'
        'Solo restaurantes con al menos 30 reseñas.'
    )
    guide_columns[2].info(
        '**Cómo debe usarse**\n\n'
        'Como referencia competitiva, no como recomendación comercial.'
    )

    filter_columns = st.columns(3)
    specialty = filter_columns[0].selectbox(
        'Especialidad',
        specialties,
        key='market_specialty'
    )
    price_options = sorted(
        groups.loc[
            groups['specialty'].eq(specialty),
            'price_interval'
        ].dropna().unique()
    )
    price_interval = filter_columns[1].selectbox(
        'Rango de precio',
        price_options,
        key='market_price'
    )
    criterion = filter_columns[2].selectbox(
        'Criterio del Top 10',
        list(top_ten_rules),
        key='market_criterion'
    )

    st.info(criterion_explanations[criterion])

    ranking, column, label = get_top_ranking(
        specialty,
        price_interval,
        criterion,
        membership,
        diagnostics
    )

    if ranking.empty:
        st.warning('No existen restaurantes con soporte para este criterio.')
        return

    selected_group = groups.loc[
        groups['specialty'].eq(specialty)
        & groups['price_interval'].eq(price_interval)
    ].iloc[0]

    market_metrics = st.columns(4)
    market_metrics[0].metric(
        'Restaurantes comparables',
        f'{len(ranking):,}'
    )
    market_metrics[1].metric(
        'Reseñas del grupo',
        f"{int(selected_group['group_reviews']):,}"
    )
    market_metrics[2].metric(
        'Rating medio del grupo',
        f"{selected_group['group_mean_rating']:.2f}"
    )
    market_metrics[3].metric(
        'Negativas del grupo',
        f"{selected_group['group_negative_percentage']:.2f} %"
    )
    st.caption(
        'Los dos promedios del grupo se calculan a nivel de restaurante para '
        'evitar que los establecimientos con más reseñas dominen la comparación.'
    )

    top_ten = ranking.head(10).copy()
    top_ten['restaurant_name'] = top_ten['name'].astype(str).str.slice(0, 42)
    top_ten['ranking_value'] = top_ten[column]
    chart_data = top_ten.sort_values('position', ascending=False)

    ranking_figure = px.bar(
        chart_data,
        x='ranking_value',
        y='restaurant_name',
        orientation='h',
        text='ranking_value',
        color_discrete_sequence=[primary_color],
        labels={
            'ranking_value': label,
            'restaurant_name': 'Restaurante'
        },
        title=f'Top 10: {criterion.lower()}'
    )
    if column == 'reviews':
        ranking_figure.update_traces(texttemplate='%{text:,.0f}')
    elif column == 'positive_percentage':
        ranking_figure.update_traces(texttemplate='%{text:.1f}%')
    else:
        ranking_figure.update_traces(texttemplate='%{text:.2f}')
    ranking_figure.update_traces(textposition='outside')
    st.plotly_chart(
        style_figure(ranking_figure),
        use_container_width=True
    )

    table_columns = [
        'position',
        'name',
        'reviews',
        'mean_review_rating',
        'positive_percentage',
        'negative_percentage'
    ]
    if column not in table_columns:
        table_columns.insert(2, column)
    ranking_table = top_ten[table_columns].rename(
        columns={
            'position': 'Posición',
            'name': 'Restaurante',
            'reviews': 'Reseñas',
            'mean_review_rating': 'Rating',
            'positive_percentage': 'Positivas (%)',
            'negative_percentage': 'Negativas (%)',
            'rating_change': 'Cambio de rating'
        }
    )
    st.dataframe(
        ranking_table.round(2),
        hide_index=True,
        use_container_width=True
    )

    with st.expander('De dónde salen estos resultados'):
        st.markdown(
            '- Los restaurantes proceden del conjunto depurado de Madrid.\n'
            '- Un grupo combina **especialidad** y **rango de precio**.\n'
            '- Los grupos elegibles contienen al menos 30 restaurantes y '
            '1,000 reseñas en conjunto.\n'
            '- El Top 10 exige al menos 30 reseñas por restaurante.\n'
            '- Los criterios recientes usan dos ventanas consecutivas de '
            'seis meses completos.\n'
            '- El ranking describe los datos observados y no garantiza '
            'calidad futura, ventas ni rentabilidad.'
        )
