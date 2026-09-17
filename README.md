# Sistema inteligente de análisis de reseñas para restaurantes de Madrid

**Trabajo de Fin de Máster**  
**María Carolina González Bernal**  
**Universidad Complutense de Madrid**  
**Máster Data Science, Big Data & Business Analytics 2025-2026**

[Acceder a la aplicación](https://restaurantintelligencesystem-mcgb.streamlit.app/)

## Descripción

Sistema de apoyo a la gestión de restaurantes basado en reseñas de TripAdvisor. Permite analizar la reputación de un establecimiento, compararlo con competidores similares, detectar cambios recientes y clasificar nuevas opiniones mediante procesamiento de lenguaje natural.

## Datos

- **Fuente:** [TripAdvisor Restaurant Reviews, versión 2.0.0](https://doi.org/10.5281/zenodo.14622324)
- **Ámbito:** restaurantes de Madrid
- **Periodo:** 2002-2023
- **Dataset final:** 1,157,800 reseñas y 10,056 restaurantes
- **Licencia:** CC BY 4.0

El sentimiento se definió a partir de la valoración de cada reseña:

- 1-2 estrellas: negativa
- 3 estrellas: neutral
- 4-5 estrellas: positiva

Las valoraciones fueron excluidas de las variables predictoras para evitar fuga de información.

## Metodología

1. Limpieza, integración y validación de los datos.
2. Análisis exploratorio de sentimiento, precio, especialidad y evolución temporal.
3. División de entrenamiento, validación y prueba por restaurante, sin establecimientos compartidos entre conjuntos.
4. Comparación de DummyClassifier, regresión logística y LinearSVC con TF-IDF.
5. Evaluación final, explicabilidad con LIME y productivización con Streamlit, FastAPI y MLflow.

## Modelo final

Se seleccionó **TF-IDF + LinearSVC**, con `C = 0.05`.

| Métrica en prueba | Resultado |
|---|---:|
| Accuracy | 0.9048 |
| Balanced accuracy | 0.8164 |
| Macro F1 | 0.8078 |
| Recall negativo | 0.8793 |

La prueba se realizó con 110,912 reseñas de 996 restaurantes no vistos durante el entrenamiento. La clase neutral fue la más difícil de identificar y representa la principal oportunidad de mejora.

## Funcionalidades

- Diagnóstico reputacional por restaurante.
- Comparación con establecimientos de la misma especialidad y rango de precio.
- Alertas basadas en dos periodos consecutivos de seis meses.
- Clasificación de nuevas reseñas como negativas, neutrales o positivas.
- Explicación local de las predicciones mediante LIME.
- Explorador Top 10 por rating, sentimiento positivo, volumen de reseñas, mejora o deterioro reciente.

El benchmarking incluye 55 grupos competitivos y 32 especialidades. El diagnóstico completo cubre 4,670 restaurantes, que concentran el 95.35 % de las reseñas.

## Estructura

```text
├── 01_data_cleaning.ipynb
├── 02_exploratory_data_analysis.ipynb
├── 03_modeling_and_productization_streamlit.ipynb
├── app/
├── tests/
├── requirements.txt
└── streamlit_app.py
```

## Ejecución local

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Pruebas automatizadas:

```bash
python -m pytest tests -v
```

## Limitaciones

- El sentimiento es una etiqueta proxy derivada de las estrellas.
- Los datos finalizan en 2023 y no representan la situación actual en tiempo real.
- Las alertas y rankings son descriptivos; no demuestran causalidad ni garantizan rentabilidad.

## Referencia del dataset

Pablo Pérez-Núñez, Blanco, E., Bolon-Canedo, V., & Beatriz Remeseiro. (2025). *TripAdvisor Restaurant Reviews* (Version 2.0.0) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.14622324


[Descargar el proyecto completo](https://drive.google.com/drive/folders/1Mu_Ffn0CY86r3qfyK-DkX3umPt-f0Pi6?usp=sharing)
