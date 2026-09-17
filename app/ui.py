
import streamlit as st

app_css = """
<style>
:root {
    --forest: #05402B;
    --forest_soft: #1D5A43;
    --sage: #B8C8BB;
    --ivory: #F7F5EF;
    --paper: #FFFEFA;
    --ink: #183027;
    --muted: #6F7B74;
    --gold: #A8874F;
}

html,
body,
[class*='css'] {
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        'Helvetica Neue',
        Arial,
        sans-serif;
    color: var(--ink);
}

.stApp {
    background:
        radial-gradient(
            circle at 92% 0%,
            rgba(184, 200, 187, 0.34),
            transparent 28rem
        ),
        var(--ivory);
}

[data-testid='stHeader'] {
    background: rgba(247, 245, 239, 0.88);
    border-bottom: 1px solid rgba(5, 64, 43, 0.08);
    backdrop-filter: blur(18px);
}

.block-container {
    max-width: 1240px;
    padding-top: 2.8rem;
    padding-bottom: 4rem;
}

h1,
h2,
h3 {
    color: var(--forest);
    font-family:
        Georgia,
        'Times New Roman',
        serif;
    letter-spacing: -0.025em;
}

.hero {
    padding: 3.6rem 3.8rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(5, 64, 43, 0.10);
    border-radius: 28px;
    background:
        linear-gradient(
            125deg,
            rgba(255, 254, 250, 0.98),
            rgba(229, 235, 227, 0.88)
        );
    box-shadow:
        0 24px 70px rgba(5, 64, 43, 0.08);
}

.hero-label {
    margin-bottom: 1rem;
    color: var(--gold);
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}

.hero h1 {
    max-width: 780px;
    margin: 0;
    font-size: clamp(
        2.6rem,
        5vw,
        4.8rem
    );
    font-weight: 500;
    line-height: 0.98;
}

.hero p {
    max-width: 720px;
    margin: 1.4rem 0 0;
    color: var(--muted);
    font-size: 1.06rem;
    line-height: 1.7;
}

[data-testid='stMetric'] {
    min-height: 126px;
    padding: 1.25rem 1.35rem;
    border: 1px solid rgba(5, 64, 43, 0.10);
    border-radius: 20px;
    background: rgba(255, 254, 250, 0.88);
    box-shadow:
        0 12px 30px rgba(5, 64, 43, 0.05);
}

[data-testid='stMetricLabel'] {
    color: var(--muted);
    font-size: 0.76rem;
    font-weight: 650;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

[data-testid='stMetricValue'] {
    color: var(--forest);
    font-family:
        Georgia,
        'Times New Roman',
        serif;
    font-size: 2rem;
}

[data-testid='stSidebar'] {
    background: var(--forest);
    border-right: 0;
}

[data-testid='stSidebar'] h1,
[data-testid='stSidebar'] h2,
[data-testid='stSidebar'] h3,
[data-testid='stSidebar'] p,
[data-testid='stSidebar'] label {
    color: var(--ivory) !important;
}

[data-testid='stSidebar']
[data-baseweb='select'] * {
    color: var(--ink) !important;
}

.sidebar-brand {
    padding: 1.2rem 0 1.8rem;
    margin-bottom: 1.5rem;
    border-bottom:
        1px solid rgba(255, 255, 255, 0.18);
}

.sidebar-brand strong {
    display: block;
    color: var(--ivory);
    font-family:
        Georgia,
        'Times New Roman',
        serif;
    font-size: 1.7rem;
    font-weight: 500;
}

.sidebar-brand span {
    display: block;
    margin-top: 0.45rem;
    color: rgba(247, 245, 239, 0.66);
    font-size: 0.72rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
}

.stTabs [data-baseweb='tab-list'] {
    gap: 0.4rem;
    padding: 0.35rem;
    border: 1px solid rgba(5, 64, 43, 0.09);
    border-radius: 16px;
    background: rgba(255, 254, 250, 0.72);
}

.stTabs [data-baseweb='tab'] {
    height: 44px;
    padding: 0 1rem;
    border-radius: 12px;
    color: var(--muted);
    font-weight: 600;
}

.stTabs [aria-selected='true'] {
    color: var(--ivory) !important;
    background: var(--forest);
}

.stTabs [data-baseweb='tab-highlight'] {
    display: none;
}

.stButton > button {
    min-height: 46px;
    border: 1px solid var(--forest);
    border-radius: 999px;
    color: var(--ivory);
    background: var(--forest);
    font-weight: 650;
    transition:
        transform 160ms ease,
        box-shadow 160ms ease;
}

.stButton > button:hover {
    border-color: var(--forest_soft);
    color: var(--ivory);
    background: var(--forest_soft);
    box-shadow:
        0 10px 24px rgba(5, 64, 43, 0.16);
    transform: translateY(-1px);
}

[data-baseweb='select'] > div,
[data-baseweb='input'] > div,
textarea {
    border-color:
        rgba(5, 64, 43, 0.14) !important;
    border-radius: 14px !important;
    background: var(--paper) !important;
}

[data-testid='stDataFrame'] {
    overflow: hidden;
    border:
        1px solid rgba(5, 64, 43, 0.10);
    border-radius: 18px;
    background: var(--paper);
}

[data-testid='stAlert'] {
    border-radius: 16px;
}

@media (max-width: 760px) {
    .block-container {
        padding-top: 1.4rem;
    }

    .hero {
        padding: 2.2rem 1.5rem;
        border-radius: 22px;
    }
}


/* Plan de acción */
.action-section,
.strength-section,
.driver-section {
    margin: 2.4rem 0 1rem;
}

.action-section h2,
.strength-section h2,
.driver-section h2 {
    color: #183027;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 2rem;
    margin: 0.2rem 0 0.35rem;
}

.action-section p,
.driver-section p {
    color: #66736D;
    margin: 0;
    max-width: 760px;
}

.section-eyebrow,
.card-label {
    color: #A8874F;
    font-size: 0.70rem;
    font-weight: 750;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.priority-card {
    background: linear-gradient(135deg, #FFFEFB 0%, #FBF4EF 100%);
    border: 1px solid rgba(139, 30, 30, 0.14);
    border-left: 5px solid #8B1E1E;
    border-radius: 20px;
    box-shadow: 0 14px 32px rgba(24, 48, 39, 0.07);
    margin: 1rem 0;
    padding: 1.45rem;
}

.priority-card__head {
    align-items: flex-start;
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.priority-card h3,
.strength-card h3 {
    color: #183027;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.35rem;
    line-height: 1.25;
    margin: 0.15rem 0 0;
}

.priority-number {
    align-items: center;
    background: #8B1E1E;
    border-radius: 999px;
    color: #FFFFFF;
    display: inline-flex;
    flex: 0 0 2.65rem;
    font-size: 0.82rem;
    font-weight: 750;
    height: 2.65rem;
    justify-content: center;
    letter-spacing: 0.06em;
}

.priority-evidence {
    background: rgba(139, 30, 30, 0.055);
    border-radius: 14px;
    margin-bottom: 0.85rem;
    padding: 0.9rem 1rem;
}

.priority-evidence p,
.priority-grid p,
.strength-card p {
    color: #3E4B46;
    line-height: 1.55;
    margin: 0.3rem 0 0;
}

.priority-grid {
    display: grid;
    gap: 0.85rem;
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.priority-grid > div {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(5, 64, 43, 0.10);
    border-radius: 14px;
    padding: 0.9rem 1rem;
}

.strength-card {
    background: linear-gradient(135deg, #F9FCF8 0%, #EEF5EF 100%);
    border: 1px solid rgba(5, 64, 43, 0.13);
    border-left: 5px solid #05402B;
    border-radius: 18px;
    margin: 0.75rem 0;
    padding: 1.1rem 1.25rem;
}

/* Señales de deterioro */
.driver-card {
    align-items: center;
    background: #FFFFFF;
    border: 1px solid rgba(139, 30, 30, 0.14);
    border-radius: 18px;
    display: grid;
    gap: 1.2rem;
    grid-template-columns: 1fr 1.3fr;
    margin: 0.8rem 0;
    padding: 1.15rem 1.25rem;
}

.driver-card h3 {
    color: #183027;
    font-family: Georgia, 'Times New Roman', serif;
    margin: 0.2rem 0 0;
}

.driver-card p {
    color: #56635E;
    margin: 0.45rem 0 0;
}

.driver-comparison {
    align-items: center;
    background: #FBF7F3;
    border-radius: 14px;
    display: grid;
    gap: 0.7rem;
    grid-template-columns: 1fr auto 1fr;
    padding: 0.85rem;
    text-align: center;
}

.driver-comparison div:not(.driver-arrow) {
    display: flex;
    flex-direction: column;
}

.driver-comparison span,
.driver-comparison small {
    color: #69746F;
    font-size: 0.66rem;
}

.driver-comparison strong {
    color: #8B1E1E;
    font-size: 1.25rem;
    margin: 0.2rem 0;
}

.driver-arrow {
    color: #A8874F;
    font-size: 1.4rem;
}

.decision-summary {
    background: linear-gradient(135deg, #05402B 0%, #1D5A43 100%);
    border-radius: 20px;
    box-shadow: 0 16px 34px rgba(5, 64, 43, 0.16);
    margin: 1.2rem 0;
    padding: 1.35rem 1.5rem;
}

.decision-summary .card-label {
    color: #D4BA88;
}

.decision-summary p {
    color: #FFFFFF;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 1.15rem;
    line-height: 1.6;
    margin: 0.45rem 0 0;
}

/* Explorador de mercado */
.market-hero {
    background: linear-gradient(135deg, #FFFEFB 0%, #EAF2EC 100%);
    border: 1px solid rgba(5, 64, 43, 0.10);
    border-radius: 24px;
    margin: 1rem 0 1.3rem;
    padding: 2rem;
}

.market-hero h1 {
    color: #183027;
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 2.4rem;
    line-height: 1.1;
    margin: 0.35rem 0 0.75rem;
}

.market-hero p {
    color: #5E6D66;
    line-height: 1.6;
    margin: 0;
    max-width: 760px;
}

section[data-testid="stSidebar"] div.stButton > button {
    border-radius: 12px;
    font-weight: 650;
    min-height: 2.8rem;
}

@media (max-width: 760px) {
    .priority-grid,
    .driver-card {
        grid-template-columns: 1fr;
    }
}

</style>
"""


def apply_style():
    """Aplicar el diseño visual."""

    st.markdown(
        app_css,
        unsafe_allow_html=True
    )
def render_header():
    """Mostrar la cabecera."""

    hero_html = (
        '<section class="hero">'
        '<div class="hero-label">'
        'Madrid · Restaurant Intelligence'
        '</div>'
        '<h1>'
        'Reputación que se convierte en decisiones.'
        '</h1>'
        '<p>'
        'Diagnóstico, comparación competitiva y alertas '
        'tempranas construidas a partir de la voz real '
        'de los clientes.'
        '</p>'
        '</section>'
    )

    sidebar_html = (
        '<div class="sidebar-brand">'
        '<strong>'
        'Madrid Intelligence'
        '</strong>'
        '<span>'
        'Restaurant reputation system'
        '</span>'
        '</div>'
    )

    st.markdown(
        hero_html,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        sidebar_html,
        unsafe_allow_html=True
    )

    st.sidebar.caption(
        'Selecciona un restaurante para comenzar.'
    )
def style_figure(figure):
    """Aplicar el estilo a Plotly."""

    figure.update_layout(
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor=(
            'rgba(255, 254, 250, 0.72)'
        ),
        font={
            'family': (
                '-apple-system, '
                'BlinkMacSystemFont, '
                'Helvetica Neue'
            ),
            'color': '#183027'
        },
        margin={
            'l': 20,
            'r': 20,
            't': 35,
            'b': 20
        }
    )

    figure.update_xaxes(
        gridcolor='rgba(5, 64, 43, 0.08)'
    )

    figure.update_yaxes(
        gridcolor='rgba(5, 64, 43, 0.08)'
    )

    return figure
