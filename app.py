"""Interfaz educativa con lectura profesional y técnica del modelo."""

import os
from pathlib import Path

import altair as alt
import pandas as pd
import requests
import streamlit as st

from src.modeling import CATEGORICAL_FEATURES, FEATURES


API_URL = os.environ.get("MODEL_API_URL", "http://127.0.0.1:8000").rstrip("/")
TEST_CORRECT = 59
TEST_TOTAL = 76
TEST_ACCURACY = TEST_CORRECT / TEST_TOTAL
EXAMPLE_PROFILES = {
    "Ejemplo A": {
        "age": 56, "sex": 1, "cp": 0, "trestbps": 130, "chol": 240,
        "fbs": 0, "restecg": 1, "thalach": 153, "exang": 0,
        "oldpeak": 0.8, "slope": 2, "ca": 0, "thal": 2,
    },
    "Ejemplo B": {
        "age": 68, "sex": 0, "cp": 2, "trestbps": 150, "chol": 275,
        "fbs": 1, "restecg": 2, "thalach": 112, "exang": 1,
        "oldpeak": 2.4, "slope": 0, "ca": 2, "thal": 3,
    },
}

FIELD_LABELS = {
    "age": "Edad (años)",
    "sex": "Sexo registrado",
    "cp": "Tipo de dolor torácico",
    "trestbps": "Presión arterial en reposo (mmHg)",
    "chol": "Colesterol sérico (mg/dL)",
    "fbs": "Glucosa en ayunas >120 mg/dL",
    "restecg": "Electrocardiograma en reposo",
    "thalach": "Frecuencia cardíaca máxima (lpm)",
    "exang": "Angina durante el ejercicio",
    "oldpeak": "Depresión ST durante el ejercicio (oldpeak)",
    "slope": "Pendiente del segmento ST",
    "ca": "Vasos principales observados",
    "thal": "Resultado de la prueba de talio",
}

FIELD_HELP = {
    "age": "Edad registrada en años.",
    "sex": "Selecciona la categoría registrada en la ficha de referencia.",
    "cp": "Las opciones usan nombres habituales para el tipo de dolor, pero la correspondencia con esta copia no está confirmada. Verifica el registro original antes de interpretar el resultado.",
    "trestbps": "Presión arterial en reposo, expresada en mmHg.",
    "chol": "Colesterol sérico, expresado en mg/dL.",
    "fbs": "Indica si la glucosa en ayunas supera 120 mg/dL.",
    "restecg": "0 = normal; 1 = anomalía ST-T; 2 = hipertrofia ventricular izquierda probable o definida.",
    "thalach": "Frecuencia cardíaca máxima alcanzada, en latidos por minuto.",
    "exang": "Indica si se observó angina durante el ejercicio.",
    "oldpeak": "Valor numérico registrado por el conjunto de datos.",
    "slope": "Las opciones describen la dirección de la pendiente ST. La correspondencia de esta copia con la referencia clínica no está confirmada.",
    "ca": "Número de vasos principales observados por fluoroscopia. Esta copia contiene una categoría adicional cuyo significado no está confirmado.",
    "thal": "Las categorías de esta copia no tienen una correspondencia clínica verificada; cada opción se conserva tal como aparece en la fuente.",
}

CATEGORY_LABELS = {
    "sex": {0: "Mujer", 1: "Hombre"},
    "cp": {
        0: "Angina típica*",
        1: "Angina atípica*",
        2: "Dolor no anginoso*",
        3: "Sin dolor*",
    },
    "fbs": {0: "No", 1: "Sí"},
    "restecg": {
        0: "Normal",
        1: "Anomalía ST-T",
        2: "Hipertrofia ventricular izquierda",
    },
    "exang": {0: "No", 1: "Sí"},
    "slope": {
        0: "Ascendente*",
        1: "Plana*",
        2: "Descendente*",
    },
    "ca": {
        0: "Ningún vaso observado",
        1: "1 vaso observado",
        2: "2 vasos observados",
        3: "3 vasos observados",
        4: "Categoría adicional*",
    },
    "thal": {
        0: "Opción A*",
        1: "Opción B*",
        2: "Opción C*",
        3: "Opción D*",
    },
}

CHART_FIELDS = {
    "Frecuencia cardíaca máxima (lpm)": "thalach",
    "Presión arterial en reposo (mmHg)": "trestbps",
    "Colesterol sérico (mg/dL)": "chol",
    "Depresión ST durante ejercicio": "oldpeak",
}


@st.cache_data
def load_schema():
    response = requests.get(f"{API_URL}/schema", timeout=10)
    response.raise_for_status()
    return response.json()


def add_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ink: #17324d;
            --muted: #52677c;
            --teal: #087f8c;
            --teal-soft: #e7f4f4;
            --blue: #326a91;
            --line: #d9e3ea;
            --paper: #f5f8fb;
            --white: #ffffff;
        }
        .stApp { background: var(--paper); color: var(--ink); }
        [data-testid="stHeader"] { background: rgba(244,248,250,.96); }
        [data-testid="stAppViewContainer"] > .main .block-container {
            max-width: 1540px; padding: 1rem 2rem 3rem;
        }
        h1, h2, h3, p, label { color: var(--ink); }
        h1 { font-size: 2.35rem !important; letter-spacing: -.035em; margin-bottom: .15rem; }
        h2 { font-size: 1.3rem !important; letter-spacing: -.015em; }
        h3 { font-size: 1.05rem !important; }
        [data-testid="stForm"] {
            background: var(--white); border: 1px solid var(--line);
            border-radius: 18px; padding: 1rem 1.1rem .9rem;
        }
        [data-testid="stForm"] [data-testid="stMarkdownContainer"] p { margin-bottom: .5rem; }
        [data-testid="stMetric"] {
            background: var(--white); border: 1px solid var(--line);
            border-radius: 14px; padding: 16px 18px;
        }
        [data-testid="stMetricLabel"] p { color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--ink); }
        [data-testid="stProgressBar"] > div > div { background: var(--teal); }
        .metric-card { background: var(--white); border: 1px solid var(--line);
            border-radius: 14px; padding: .85rem 1rem; min-height: 112px; }
        .metric-label { color: var(--muted); font-size: .82rem; line-height: 1.3; }
        .metric-value { color: var(--ink); font-size: 1.24rem; font-weight: 700;
            line-height: 1.28; margin-top: .45rem; overflow-wrap: anywhere; }
        .metric-note { color: var(--muted); font-size: .72rem; line-height: 1.35;
            margin-top: .35rem; }
        [data-testid="stAlert"] {
            background: #fff7e8 !important; border: 1px solid #ead39d !important;
            border-left: 5px solid #c68b21 !important; border-radius: 12px;
        }
        [data-testid="stAlert"] * { color: #604817 !important; }
        div.stButton > button[kind="primaryFormSubmit"],
        div.stFormSubmitButton > button {
            background: var(--teal); border: 0; color: white;
            border-radius: 10px; min-height: 2.8rem; font-weight: 650;
        }
        div.stButton > button[kind="primaryFormSubmit"]:hover,
        div.stFormSubmitButton > button:hover { background: #066a75; color: white; }
        div[data-baseweb="select"] > div, div[data-testid="stNumberInput"] input {
            border-radius: 9px; border-color: var(--line);
        }
        [data-testid="stAlert"] { border-radius: 12px; }
        .eyebrow { color: var(--teal); font-size: .78rem; letter-spacing: .09em;
            font-weight: 700; text-transform: uppercase; margin-bottom: -.45rem; }
        .result-card { background: white; border: 1px solid var(--line);
            border-left: 5px solid var(--teal); border-radius: 14px;
            padding: 1.1rem 1.3rem; margin: .7rem 0 1rem; }
        .result-title { font-size: 1.23rem; font-weight: 700; color: var(--ink); }
        .result-copy { color: var(--muted); margin-top: .35rem; line-height: 1.55; }
        .small-note { color: var(--muted); font-size: .88rem; line-height: 1.5; }
        .notice { background: #fff7e8; border: 1px solid #ead39d;
            border-left: 5px solid #c68b21; border-radius: 12px; color: #604817;
            padding: .85rem 1rem; margin: 1rem 0 1.15rem; line-height: 1.5; }
        [data-testid="stRadio"] > div { gap: .55rem; }
        [data-testid="stRadio"] label {
            background: white; border: 1px solid var(--line); border-radius: 10px;
            padding: .45rem .85rem; color: var(--ink);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_input_form(schema: dict) -> dict | None:
    categories = schema["category_domains"]
    numeric_bounds = schema["numeric_bounds"]
    sections = [
        ("1 · Datos generales", ["age", "sex"]),
        ("2 · Antecedentes y evaluación", ["cp", "trestbps", "chol", "fbs", "restecg"]),
        ("3 · Prueba de esfuerzo", ["thalach", "exang", "oldpeak", "slope", "ca", "thal"]),
    ]
    values = {}
    with st.form("individual_prediction"):
        st.subheader("Datos del perfil · 13 campos")
        st.caption("Ingresa los valores del registro. Completa todos los campos; la selección se adapta automáticamente al modelo.")
        st.caption("* Equivalencia clínica pendiente de confirmar en la fuente del dataset.")
        for section_title, features in sections:
            st.markdown(f"<p class='eyebrow'>{section_title}</p>", unsafe_allow_html=True)
            columns = st.columns(2)
            for index, feature in enumerate(features):
                with columns[index % 2]:
                    label = FIELD_LABELS[feature]
                    if feature in CATEGORICAL_FEATURES:
                        domain = sorted(categories.get(feature, []))
                        if not domain:
                            st.error(f"El modelo no informa categorías para {feature}.")
                            return None
                        values[feature] = st.selectbox(
                            label,
                            [None, *domain],
                            index=0,
                            format_func=lambda value, feature=feature: (
                                "Selecciona una opción" if value is None
                                else CATEGORY_LABELS.get(feature, {}).get(
                                    value, "Categoría adicional (sin descripción validada)"
                                )
                            ),
                            help=FIELD_HELP[feature],
                            key=f"input_{feature}",
                        )
                    else:
                        minimum, maximum = numeric_bounds[feature]
                        if feature == "oldpeak":
                            values[feature] = st.number_input(
                                label, min_value=float(minimum), max_value=float(maximum),
                                value=None, step=0.1, format="%.1f",
                                placeholder="Ingresa un valor", help=FIELD_HELP[feature],
                                key=f"input_{feature}",
                            )
                        else:
                            values[feature] = st.number_input(
                                label, min_value=int(minimum), max_value=int(maximum),
                                value=None, step=1, format="%d",
                                placeholder="Ingresa un valor", help=FIELD_HELP[feature],
                                key=f"input_{feature}",
                            )
        submitted = st.form_submit_button("Analizar perfil", type="primary", width="stretch")
    if submitted:
        missing = [FIELD_LABELS[feature] for feature, value in values.items() if value is None]
        if missing:
            st.error("Completa todos los campos antes de analizar el perfil.")
            return None
        return {feature: values[feature] for feature in FEATURES}
    return None


def request_prediction(values: dict) -> dict:
    response = requests.post(f"{API_URL}/predict", json={"values": values}, timeout=30)
    response.raise_for_status()
    return response.json()


def render_example_profiles(schema: dict) -> str | None:
    selected = None
    with st.expander("Demostración · usar un perfil ficticio", expanded=False):
        st.caption("Perfiles inventados para mostrar la interfaz; no representan pacientes ni casos reales.")
        columns = st.columns(len(EXAMPLE_PROFILES))
        for column, (name, profile) in zip(columns, EXAMPLE_PROFILES.items()):
            with column:
                if st.button(f"Probar {name}", width="stretch", key=f"load_{name}"):
                    selected = name
    if selected is None:
        return None

    profile = EXAMPLE_PROFILES[selected]
    for feature in CATEGORICAL_FEATURES:
        if profile[feature] not in schema["category_domains"].get(feature, []):
            st.error(f"El {selected} contiene un código no admitido para {FIELD_LABELS[feature]}.")
            return None
    for feature, bounds in schema["numeric_bounds"].items():
        if not bounds[0] <= profile[feature] <= bounds[1]:
            st.error(f"El {selected} contiene un valor fuera del rango para {FIELD_LABELS[feature]}.")
            return None

    try:
        st.session_state["prediction_result"] = request_prediction(profile)
    except Exception as error:
        st.error(f"No se pudo analizar {selected}: {error}")
        return None
    st.session_state["prediction_values"] = profile
    st.session_state["active_example_profile"] = selected
    for feature, value in profile.items():
        st.session_state[f"input_{feature}"] = value
    return selected


@st.cache_data
def load_reference_data() -> pd.DataFrame:
    path = Path(__file__).resolve().parent / "data" / "processed" / "heart_unique.csv"
    return pd.read_csv(path)


def prepare_explanation(result: dict) -> pd.DataFrame:
    explanation = pd.DataFrame(result["local_explanation"])
    explanation["Variable"] = explanation["Variable"].map(
        lambda name: FIELD_LABELS.get(name, name)
    )
    explanation["Dirección del score"] = explanation["Dirección del score"].replace({
        "Hacia clase 0": "Hacia Grupo A",
        "Hacia clase 1": "Hacia Grupo B",
    })
    total_magnitude = explanation["Contribución SHAP (log-odds)"].abs().sum()
    if total_magnitude:
        explanation["Porcentaje de contribución"] = (
            explanation["Contribución SHAP (log-odds)"].abs() / total_magnitude * 100
        )
    else:
        explanation["Porcentaje de contribución"] = 0.0
    return explanation.sort_values(
        "Contribución SHAP (log-odds)", key=lambda values: values.abs(), ascending=False
    ).reset_index(drop=True)


def render_summary_view(result: dict, explanation: pd.DataFrame) -> None:
    prediction = int(result["prediction"])
    top = explanation.iloc[0]
    st.subheader("Resumen del análisis")
    group_label = "Grupo A" if prediction == 0 else "Grupo B"
    st.markdown(
        f"<div class='result-card'><div class='result-title'>Resultado del modelo: {group_label}</div>"
        "<div class='result-copy'>Categoría experimental, sin equivalencia diagnóstica validada.</div></div>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown("**Cómo leer los grupos del dataset**")
        group_cols = st.columns(2, gap="small")
        group_cols[0].markdown("**Grupo A · target 0**  \nEtiqueta de la fuente: **sin enfermedad**")
        group_cols[1].markdown("**Grupo B · target 1**  \nEtiqueta de la fuente: **con enfermedad**")
        st.caption(
            "Es la definición publicada para las etiquetas del dataset; no confirma ni descarta "
            "enfermedad en una persona. El resultado del prototipo no es un diagnóstico."
        )
    metric_cols = st.columns(2, gap="small")
    metric_cols[0].markdown(
        f"<div class='metric-card'><div class='metric-label'>Acierto en evaluación interna</div>"
        f"<div class='metric-value'>{TEST_ACCURACY:.0%}</div>"
        f"<div class='metric-note'>{TEST_CORRECT} de {TEST_TOTAL} perfiles de prueba; no es un pronóstico individual.</div></div>",
        unsafe_allow_html=True,
    )
    metric_cols[1].markdown(
        f"<div class='metric-card'><div class='metric-label'>Variable que más influyó en este perfil</div>"
        f"<div class='metric-value'>{top['Variable']}</div>"
        f"<div class='metric-note'>Explicación SHAP: contribución al resultado del modelo, no una causa clínica.</div></div>",
        unsafe_allow_html=True,
    )
    st.caption(
        f"El resultado del modelo es {group_label}; la equivalencia clínica de estas categorías no está validada."
    )
    render_compact_reference()


def render_compact_reference() -> None:
    values = st.session_state.get("prediction_values")
    if not values:
        return
    age = int(values["age"])
    decade = (age // 10) * 10
    reference = load_reference_data()
    peers = reference[(reference["age"] >= decade) & (reference["age"] < decade + 10)]
    if peers.empty:
        return
    patient_value = float(values["thalach"])
    mean_value = float(peers["thalach"].mean())
    st.markdown("#### Frecuencia cardíaca máxima")
    st.caption("Tu perfil frente al promedio de la muestra en su grupo de edad.")
    comparison = pd.DataFrame(
        {"lpm": [patient_value, mean_value]},
        index=["Este perfil", "Promedio de la muestra"],
    )
    mini_chart = alt.Chart(comparison.reset_index(names="grupo")).mark_bar(
        cornerRadiusEnd=5
    ).encode(
        x=alt.X("lpm:Q", title="Latidos por minuto", scale=alt.Scale(zero=False)),
        y=alt.Y("grupo:N", title=None, sort=["Este perfil", "Promedio de la muestra"]),
        color=alt.Color(
            "grupo:N",
            scale=alt.Scale(
                domain=["Este perfil", "Promedio de la muestra"],
                range=["#d97706", "#087f8c"],
            ),
            legend=None,
        ),
        tooltip=[alt.Tooltip("grupo:N", title="Referencia"), alt.Tooltip("lpm:Q", title="lpm", format=".1f")],
    ).properties(height=115)
    st.altair_chart(mini_chart, width="stretch")
    st.caption(f"Grupo de edad {decade}–{decade + 9}; muestra n={len(peers)}. No es un rango normal clínico.")


def render_reference_chart(values: dict) -> None:
    st.subheader("Comparación descriptiva por edad")
    st.caption(
        "Compara el valor ingresado con personas del mismo grupo de edad dentro de la muestra "
        "académica. No representa valores normales ni rangos clínicos."
    )
    selected_label = st.selectbox("Variable para comparar", list(CHART_FIELDS))
    feature = CHART_FIELDS[selected_label]
    reference = load_reference_data().copy()
    reference["grupo_edad"] = (reference["age"] // 10) * 10
    reference["grupo"] = reference["grupo_edad"].map(lambda decade: f"{decade}–{decade + 9}")
    stats = (
        reference.groupby(["grupo_edad", "grupo"])[feature]
        .agg(
            promedio="mean",
            p25=lambda column: column.quantile(0.25),
            p75=lambda column: column.quantile(0.75),
            n="count",
        )
        .reset_index()
        .sort_values("grupo_edad")
    )
    age_order = stats["grupo"].tolist()
    patient_group_start = (int(values["age"]) // 10) * 10
    patient_group = f"{patient_group_start}–{patient_group_start + 9}"
    patient_value = float(values[feature])
    patient = pd.DataFrame({"grupo": [patient_group], "valor": [patient_value]})
    x_axis = alt.X(
        "grupo:N", sort=age_order, title="Edad (años)", axis=alt.Axis(labelAngle=0)
    )
    interval = alt.Chart(stats).mark_rule(color="#8aa1b2", strokeWidth=8).encode(
        x=x_axis,
        y=alt.Y("p25:Q", title=selected_label, scale=alt.Scale(zero=False)),
        y2="p75:Q",
        tooltip=[
            alt.Tooltip("grupo:N", title="Edad"),
            alt.Tooltip("promedio:Q", title="Promedio de la muestra", format=".1f"),
            alt.Tooltip("p25:Q", title="Percentil 25", format=".1f"),
            alt.Tooltip("p75:Q", title="Percentil 75", format=".1f"),
            alt.Tooltip("n:Q", title="Personas", format="d"),
        ],
    )
    mean_line = alt.Chart(stats).mark_line(point=True, color="#087f8c", strokeWidth=3).encode(
        x=x_axis,
        y=alt.Y("promedio:Q", title=selected_label, scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("grupo:N", title="Edad"), alt.Tooltip("promedio:Q", title="Promedio", format=".1f")],
    )
    patient_rule = alt.Chart(patient).mark_rule(color="#d97706", strokeDash=[6, 4]).encode(
        y=alt.Y("valor:Q", title=selected_label, scale=alt.Scale(zero=False)),
    )
    patient_point = alt.Chart(patient).mark_point(
        filled=True, color="#d97706", size=150, shape="diamond"
    ).encode(
        x=alt.X("grupo:N", sort=age_order),
        y=alt.Y("valor:Q", title=selected_label, scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("grupo:N", title="Grupo de edad"), alt.Tooltip("valor:Q", title="Valor del perfil", format=".1f")],
    )
    chart = (interval + mean_line + patient_rule + patient_point).properties(height=330)
    st.altair_chart(chart, width="stretch")
    st.caption(
        "Línea turquesa: promedio de la muestra · banda vertical: percentiles 25–75 · "
        "rombo y línea ámbar: valor del perfil ingresado."
    )


def explain_score_limit() -> None:
    st.info(
        "El puntaje interno es una salida matemática del modelo. No está calibrado y no debe leerse "
        "como probabilidad de enfermedad, riesgo individual ni posibilidad de acierto."
    )


def render_professional_view(result: dict, explanation: pd.DataFrame) -> None:
    top = explanation.iloc[0]
    prediction = int(result["prediction"])
    target_group = "Grupo B" if prediction == 1 else "Grupo A"
    support = explanation[
        explanation["Dirección del score"] == f"Hacia {target_group}"
    ]
    strongest_support = support.iloc[0] if not support.empty else top
    top_direction = top["Dirección del score"]
    st.subheader("¿Qué variables influyeron más en el resultado?")
    st.caption(
        "Las barras comparan la magnitud relativa de las contribuciones de este perfil. "
        "La dirección indica hacia qué clase movió el score el modelo."
    )
    for _, row in explanation.head(5).iterrows():
        left, right = st.columns([5, 1])
        direction = row["Dirección del score"]
        left.markdown(f"**{row['Variable']}** · {direction}")
        right.markdown(f"**{row['Porcentaje de contribución']:.0f}%**")
        st.progress(min(float(row["Porcentaje de contribución"]) / 100, 1.0))

    st.markdown(
        f"<p class='small-note'>La variable con mayor contribución absoluta fue "
        f"<b>{top['Variable']}</b> ({top['Porcentaje de contribución']:.0f}% de la magnitud "
        "total SHAP del perfil). Este porcentaje describe cómo el modelo distribuyó sus "
        "contribuciones; no es un efecto causal ni clínico.</p>",
        unsafe_allow_html=True,
    )

    st.subheader("Lectura sugerida")
    st.write(
        f"Entre las señales que apoyaron la clase asignada, destacó "
        f"**{strongest_support['Variable']}**. La mayor contribución absoluta fue "
        f"**{top['Variable']}** ({top['Porcentaje de contribución']:.0f}% del total SHAP), "
        f"con dirección **{top_direction.lower()}**."
    )
    st.caption(
        "La etiqueta positiva de la fuente no tiene equivalencia clínica verificada para esta copia. "
        "El resultado no reemplaza una evaluación clínica."
    )


def render_technical_view(result: dict, explanation: pd.DataFrame) -> None:
    prediction = int(result["prediction"])
    score = float(result["score_class_1_uncalibrated"])
    group_label = "Grupo A" if prediction == 0 else "Grupo B"
    metric_cols = st.columns(3)
    metric_cols[0].metric("Categoría asignada", group_label)
    metric_cols[1].metric("Puntaje matemático interno", f"{score:.6f}")
    metric_cols[2].metric("Acierto en evaluación interna", f"{TEST_ACCURACY:.0%}")
    st.caption(
        "La exactitud corresponde a una partición de prueba de 76 filas y no es una estimación individual."
    )
    explain_score_limit()

    st.subheader("Contribuciones locales SHAP")
    st.caption("Unidad: log-odds. El signo muestra hacia qué grupo interno mueve la contribución.")
    technical = explanation[[
        "Variable", "Valor ingresado", "Contribución SHAP (log-odds)",
        "Porcentaje de contribución", "Dirección del score",
    ]].copy()
    st.dataframe(technical, hide_index=True, width="stretch")
    chart = technical.head(8).set_index("Variable")["Contribución SHAP (log-odds)"]
    st.bar_chart(chart, color="#087f8c")

    st.subheader("Importancia global")
    global_display = pd.DataFrame(result["global_importance"])
    global_display["variable"] = global_display["variable"].map(
        lambda name: FIELD_LABELS.get(name, name)
    )
    global_display = global_display.rename(columns={
        "variable": "Variable",
        "mean_abs_shap_log_odds": "Media de |SHAP| (log-odds)",
        "mean_signed_shap_log_odds": "SHAP firmado medio (log-odds)",
    })
    st.dataframe(global_display, hide_index=True, width="stretch")


def main() -> None:
    st.set_page_config(page_title="Analizador Heart Disease", page_icon="🫀", layout="wide")
    add_theme()
    st.markdown("<p class='eyebrow'>Herramienta académica · Heart Disease</p>", unsafe_allow_html=True)
    st.title("Análisis de perfil")
    st.caption("Ingreso de variables, resultado del modelo y explicación de sus señales.")
    st.markdown(
        "<div class='notice' role='note'><b>Prototipo educativo.</b> No está validado para uso "
        "clínico; no diagnostica ni debe usarse para decidir tratamientos.</div>",
        unsafe_allow_html=True,
    )

    try:
        schema = load_schema()
    except Exception as error:
        st.error(f"No se pudo conectar con el servicio del modelo en {API_URL}: {error}")
        st.stop()

    input_col, result_col = st.columns([1.08, 0.92], gap="large", vertical_alignment="top")
    with input_col:
        st.markdown("### Ingreso de datos")
        render_example_profiles(schema)
        values = render_input_form(schema)
        if values is not None:
            try:
                st.session_state["prediction_result"] = request_prediction(values)
                st.session_state["prediction_values"] = values
                st.session_state["active_example_profile"] = None
            except Exception as error:
                st.error(f"El servicio de inferencia no respondió correctamente: {error}")
                st.stop()

    result = st.session_state.get("prediction_result")
    with result_col:
        if result is None:
            st.markdown("### Resultado")
            st.info("Completa los campos y selecciona **Analizar perfil** para ver aquí el resumen.")
        else:
            explanation = prepare_explanation(result)
            if st.session_state.get("active_example_profile"):
                st.caption(
                    f"Demostración ficticia: {st.session_state['active_example_profile']}. "
                    "Los datos se cargaron en el formulario."
                )
            render_summary_view(result, explanation)

    if result is None:
        return

    explanation = prepare_explanation(result)
    result_values = st.session_state["prediction_values"]
    st.divider()
    st.markdown("## Detalle y comparación")
    render_reference_chart(result_values)
    with st.expander("Ver explicación del modelo", expanded=False):
        view = st.radio(
            "Nivel de detalle",
            ["Lectura simple", "Detalle técnico"],
            horizontal=True,
            key="explanation_view",
        )
        if view == "Lectura simple":
            render_professional_view(result, explanation)
        else:
            render_technical_view(result, explanation)


if __name__ == "__main__":
    main()
