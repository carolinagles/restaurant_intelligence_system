# Análisis de reseñas de restaurantes de Madrid

**TFM · María Carolina González Bernal · Máster en Data Science, Big Data & Business Analytics, UCM**

[Aplicación Streamlit](https://restaurantintelligencesystem-mcgb.streamlit.app/) · [Repositorio](https://github.com/carolinagles/restaurant_intelligence_system)

## Proyecto

Sistema de apoyo para interpretar reseñas de TripAdvisor. La aplicación muestra el diagnóstico de cada restaurante, lo compara con establecimientos de especialidad y precio similares, señala cambios recientes en su reputación y clasifica nuevas reseñas como negativas, neutrales o positivas.

## Datos y método

Se utilizan [TripAdvisor Restaurant Reviews, versión 2.0.0](https://doi.org/10.5281/zenodo.14622324), con 1,157,800 reseñas y 10,056 restaurantes de Madrid tras la preparación. Las etiquetas de sentimiento se obtienen de las estrellas de cada reseña; la valoración no se usa para predecirlas.

Los tres notebooks documentan la limpieza, el análisis exploratorio y el modelado. Se comparan un modelo de referencia, regresión logística y LinearSVC sobre texto representado con TF-IDF. La división por restaurante evita compartir establecimientos entre entrenamiento y prueba. El modelo elegido es **TF-IDF + LinearSVC** (`C=0.05`), con **macro F1 de 0.8078** y **recall de la clase negativa de 0.8793** en prueba. Se emplean MLflow para registrar experimentos, LIME para explicar predicciones y Streamlit para la interfaz.

## Ejecución local

Con las dependencias, datos y artefactos del proyecto disponibles:

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Los notebooks se ejecutan en orden: `01_data_cleaning.ipynb`, `02_exploratory_data_analysis.ipynb` y `03_modeling_and_productization_streamlit.ipynb`. Los datos originales en formato `.pkl` van en `data/`.

## Alcance

Las etiquetas provienen de las estrellas, no de una anotación manual del texto. Las alertas describen cambios observados en periodos históricos; los datos terminan en 2023 y no reflejan la situación actual en tiempo real.

[Descargar el proyecto completo](https://drive.google.com/drive/folders/1Mu_Ffn0CY86r3qfyK-DkX3umPt-f0Pi6?usp=sharing)
