import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator
from streamlit_lottie import st_lottie
import json

# ---------------- CONFIGURACIÓN ----------------

st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# ---------------- FUNCIONES LOTTIE ----------------

def cargar_lottie(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

# ANIMACIONES
animacion_positiva = cargar_lottie("positivo.json")
animacion_negativa = cargar_lottie("negativo.json")
animacion_neutral = cargar_lottie("neutral.json")

# ---------------- TÍTULO ----------------

st.title("📝 Analizador de Texto con TextBlob")

st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:

- Análisis de sentimiento y subjetividad  
- Extracción de palabras clave  
- Análisis de frecuencia de palabras  
""")

# ---------------- SIDEBAR ----------------

st.sidebar.title("Opciones")

modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

# ---------------- CONTADOR DE PALABRAS ----------------

def contar_palabras(texto):

    stop_words = set([
        "a","al","algo","algunas","algunos","ante","antes","como","con",
        "contra","cual","cuando","de","del","desde","donde","durante",
        "e","el","ella","ellas","ellos","en","entre","era","eras","es",
        "esa","esas","ese","eso","esos","esta","estas","este","esto",
        "estos","ha","han","hasta","he","la","las","le","les","lo",
        "los","me","mi","mis","mucho","muy","nada","ni","no","nos",
        "o","otra","otro","para","pero","por","porque","que","se","si",
        "sin","sobre","su","sus","también","te","ti","tiene","todo",
        "tu","tus","un","una","uno","unos","y","ya","yo",

        "about","above","after","again","against","all","am","an","and",
        "any","are","as","at","be","because","been","before","being",
        "below","between","both","but","by","could","did","do","does",
        "doing","down","during","each","few","for","from","further",
        "had","has","have","having","he","her","here","hers","him",
        "his","how","if","in","into","is","it","its","itself","just",
        "more","most","my","no","nor","not","now","of","off","on",
        "once","only","or","other","our","out","over","own","same",
        "she","should","so","some","such","than","that","the","their",
        "them","then","there","these","they","this","those","through",
        "to","too","under","until","up","very","was","we","were",
        "what","when","where","which","while","who","why","with",
        "would","you","your"
    ])

    palabras = re.findall(r'\b\w+\b', texto.lower())

    palabras_filtradas = [
        palabra for palabra in palabras
        if palabra not in stop_words and len(palabra) > 2
    ]

    contador = {}

    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1

    contador_ordenado = dict(
        sorted(contador.items(), key=lambda x: x[1], reverse=True)
    )

    return contador_ordenado, palabras_filtradas

# ---------------- TRADUCTOR ----------------

translator = Translator()

def traducir_texto(texto):

    try:

        traduccion = translator.translate(
            texto,
            src='es',
            dest='en'
        )

        return traduccion.text

    except Exception as e:

        st.error(f"Error al traducir: {e}")
        return texto

# ---------------- PROCESAMIENTO ----------------

def procesar_texto(texto):

    texto_original = texto

    texto_ingles = traducir_texto(texto)

    blob = TextBlob(texto_ingles)

    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity

    frases_originales = [
        frase.strip()
        for frase in re.split(r'[.!?]+', texto_original)
        if frase.strip()
    ]

    frases_traducidas = [
        frase.strip()
        for frase in re.split(r'[.!?]+', texto_ingles)
        if frase.strip()
    ]

    frases_combinadas = []

    for i in range(min(len(frases_originales), len(frases_traducidas))):

        frases_combinadas.append({
            "original": frases_originales[i],
            "traducido": frases_traducidas[i]
        })

    contador_palabras, palabras = contar_palabras(texto_ingles)

    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

# ---------------- VISUALIZACIONES ----------------

def crear_visualizaciones(resultados):

    col1, col2 = st.columns(2)

    # SENTIMIENTO
    with col1:

        st.subheader("Análisis de Sentimiento y Subjetividad")

        sentimiento_norm = (
            resultados["sentimiento"] + 1
        ) / 2

        st.write("**Sentimiento:**")

        st.progress(sentimiento_norm)

        if resultados["sentimiento"] > 0.05:

            st.success(
                f"📈 Positivo ({resultados['sentimiento']:.2f})"
            )

        elif resultados["sentimiento"] < -0.05:

            st.error(
                f"📉 Negativo ({resultados['sentimiento']:.2f})"
            )

        else:

            st.info(
                f"📊 Neutral ({resultados['sentimiento']:.2f})"
            )

        st.write("**Subjetividad:**")

        st.progress(resultados["subjetividad"])

        if resultados["subjetividad"] > 0.5:

            st.warning(
                f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})"
            )

        else:

            st.info(
                f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})"
            )

    # PALABRAS FRECUENTES
    with col2:

        st.subheader("Palabras más frecuentes")

        if resultados["contador_palabras"]:

            palabras_top = dict(
                list(
                    resultados["contador_palabras"].items()
                )[:10]
            )

            st.bar_chart(palabras_top)

    # ---------------- ANIMACIÓN ----------------

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns([1,2,1])

    with col_b:

        if resultados["sentimiento"] > 0.05:

            st_lottie(
                animacion_positiva,
                height=250
            )

        elif resultados["sentimiento"] < -0.05:

            st_lottie(
                animacion_negativa,
                height=250
            )

        else:

            st_lottie(
                animacion_neutral,
                height=250
            )

    # ---------------- TEXTO TRADUCIDO ----------------

    st.subheader("Texto Traducido")

    with st.expander("Ver traducción completa"):

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("**Texto Original (Español):**")

            st.text(
                resultados["texto_original"]
            )

        with col2:

            st.markdown("**Texto Traducido (Inglés):**")

            st.text(
                resultados["texto_traducido"]
            )

    # ---------------- FRASES ----------------

    st.subheader("Frases detectadas")

    if resultados["frases"]:

        for i, frase_dict in enumerate(
            resultados["frases"][:10],
            1
        ):

            frase_original = frase_dict["original"]
            frase_traducida = frase_dict["traducido"]

            try:

                blob_frase = TextBlob(
                    frase_traducida
                )

                sentimiento = (
                    blob_frase.sentiment.polarity
                )

                if sentimiento > 0.05:
                    emoji = "😊"

                elif sentimiento < -0.05:
                    emoji = "😟"

                else:
                    emoji = "😐"

                st.write(
                    f"{i}. {emoji} **Original:** *\"{frase_original}\"*"
                )

                st.write(
                    f"   **Traducción:** *\"{frase_traducida}\"*"
                )

                st.write("---")

            except:

                st.write(
                    f"{i}. **Original:** *\"{frase_original}\"*"
                )

                st.write(
                    f"   **Traducción:** *\"{frase_traducida}\"*"
                )

                st.write("---")

# ---------------- MODOS ----------------

if modo == "Texto directo":

    st.subheader("Ingresa tu texto para analizar")

    texto = st.text_area(
        "",
        height=200,
        placeholder="Escribe o pega aquí el texto..."
    )

    if st.button("Analizar texto"):

        if texto.strip():

            with st.spinner(
                "Analizando texto..."
            ):

                resultados = procesar_texto(texto)

                crear_visualizaciones(resultados)

        else:

            st.warning(
                "Por favor ingresa texto."
            )

# ---------------- ARCHIVOS ----------------

elif modo == "Archivo de texto":

    st.subheader("Carga un archivo de texto")

    archivo = st.file_uploader(
        "",
        type=["txt", "csv", "md"]
    )

    if archivo is not None:

        try:

            contenido = archivo.getvalue().decode("utf-8")

            with st.expander(
                "Ver contenido del archivo"
            ):

                st.text(contenido[:1000])

            if st.button("Analizar archivo"):

                with st.spinner(
                    "Analizando archivo..."
                ):

                    resultados = procesar_texto(contenido)

                    crear_visualizaciones(resultados)

        except Exception as e:

            st.error(f"Error: {e}")

# ---------------- INFO ----------------

with st.expander(
    "📚 Información sobre el análisis"
):

    st.markdown("""
### Sobre el análisis de texto

- **Sentimiento**: Va de -1 (muy negativo) a 1 (muy positivo)
- **Subjetividad**: Va de 0 (objetivo) a 1 (subjetivo)

### Librerías utilizadas

```txt
streamlit
textblob
pandas
googletrans==4.0.0rc1
streamlit-lottie
