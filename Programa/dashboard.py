import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="Dashboard de Videos en Tendencia", layout="wide")

# ==========================
# CONFIGURACIÓN DE RUTAS
# ==========================
csv_path = "data/USvideos_cc50_202101.csv"
json_path = "data/US_category_id.json"
clean_path = "data_limpios/EEUU_limpio.csv"
stats_path = "data_limpios/stats.json"
state_chart_path = "data_limpios/state_chart.json"
freq_path = "data_limpios/freq_cat.json"
pub_path = "data_limpios/pub_years.json"
dtype_path = "data_limpios/dtype_distribution.json"

@st.cache_data
def cargar_datos():
    df = pd.read_csv(csv_path)

    # Cargar categorías
    with open(json_path, "r", encoding="utf-8") as f:
        cat_map = {int(i["id"]): i["snippet"]["title"] for i in json.load(f)["items"]}
    df["category_name"] = df["category_id"].map(cat_map)

    # --- INSPECCIÓN Y LIMPIEZA ---
    df["description"] = df["description"].fillna("Sin descripción")
    df["state"] = df["state"].fillna("Desconocido")
    df["lat"] = df["lat"].fillna(0.0)
    df["lon"] = df["lon"].fillna(0.0)

    for col in ["views", "likes", "dislikes", "comment_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        lim = df[col].quantile(0.999)
        df[col] = np.where(df[col] > lim, lim, df[col])

    df["log_views"] = np.log1p(df["views"])
    df["title_length"] = df["title"].astype(str).apply(len)
    df["desc_length"] = df["description"].astype(str).apply(len)
    df["tag_count"] = df["tags"].astype(str).apply(lambda x: len(x.split("|")) if x != "[None]" else 0)
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    df["publish_hour"] = df["publish_time"].dt.hour
    df["trending_date_dt"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m", errors="coerce")
    df["publish_year"] = df["publish_time"].dt.year

    # Guardar CSV limpio
    os.makedirs("Programa/data_limpios", exist_ok=True)
    df.to_csv(clean_path, index=False)

    # Guardar estadísticas
    stats = {
        "total_rows": int(df.shape[0]),
        "total_views": int(df["views"].sum()),
        "total_likes": int(df["likes"].sum()),
        "total_dislikes": int(df["dislikes"].sum()),
        "total_comments": int(df["comment_count"].sum())
    }
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    # Frecuencia categorías
    freq_cat = df["category_name"].value_counts().head(10)
    freq_data = {
        "categories": freq_cat.index.tolist(),
        "counts": freq_cat.values.tolist()
    }
    with open(freq_path, "w", encoding="utf-8") as f:
        json.dump(freq_data, f, indent=2, ensure_ascii=False)

    # Estados
    state_counts = df["state"].value_counts().sort_index()
    state_data = {
        "labels": state_counts.index.tolist(),
        "values": state_counts.values.tolist()
    }
    with open(state_chart_path, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=2, ensure_ascii=False)

    # Distribución de tipos
    dtype_counts = df.dtypes.value_counts().to_dict()
    dtype_data = {
        "labels": [str(k) for k in dtype_counts.keys()],
        "values": list(dtype_counts.values())
    }
    with open(dtype_path, "w", encoding="utf-8") as f:
        json.dump(dtype_data, f, indent=2, ensure_ascii=False)

    # Publicaciones por año
    yearly_stats = df.groupby("publish_year").agg({
        "video_id": "count",
        "views": "mean"
    }).rename(columns={"video_id": "count_videos", "views": "avg_views"}).dropna()
    pub_years_data = {
        "labels": yearly_stats.index.astype(str).tolist(),
        "values": yearly_stats["count_videos"].astype(int).tolist(),
        "avg_views": yearly_stats["avg_views"].round(0).astype(int).tolist()
    }
    with open(pub_path, "w", encoding="utf-8") as f:
        json.dump(pub_years_data, f, indent=2, ensure_ascii=False)

    return df

# ========================
# CARGAR DATOS YA LIMPIOS
# ========================
df = cargar_datos()

def agregar_estilos():
    st.markdown("""
        <style>
            body {
                background-color: #1e1e2f; /* Cambia esto al color que quieras */
                color: white;
            }
            .stApp {
                background-color: #1e1e2f; /* Fondo general de la app */
            }
        </style>
    """, unsafe_allow_html=True)

agregar_estilos()


preguntas = [
    "A. Clasificación con Regresión Logística",
    "1. Categorías con mayor número de videos",
    "2a. Categorías con más likes promedio",
    "2b. Categorías con menos likes promedio",
    "3. Mejor ratio Likes/Dislikes",
    "4. Mejor ratio Views/Comments",
    "5. Evolución por fecha",
    "6a. Top canales con más tendencias",
    "6b. Top canales con menos tendencias",
    "7. Mapa Vistas, Likes y Dislikes por Estado",
    "8. Videos con más comentarios",
    "9. Matriz de correlación"
]

opcion = st.selectbox("Elige una sección del análisis", preguntas)

if opcion == preguntas[0]:   
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

    st.header("✅ Clasificación de Videos Populares con Regresión Logística")

    st.markdown("""
    Este modelo predice si un video será **popular** (top 25% de vistas) según:

    - Likes
    - Dislikes
    - Comentarios
    - Longitud del título
    - Longitud de la descripción
    - Número de tags
    """)

    # Preparar variable objetivo
    threshold = df["views"].quantile(0.75)
    df["is_popular"] = np.where(df["views"] >= threshold, 1, 0)

    # Entrenamiento
    X = df[["likes", "dislikes", "comment_count", "title_length", "desc_length", "tag_count"]]
    y = df["is_popular"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    modelo = LogisticRegression(max_iter=1000)
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    # Resultados
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)

    st.subheader("🎯 Exactitud del Modelo")
    st.metric("Accuracy", f"{accuracy * 100:.2f}%")

    st.subheader("📊 Matriz de Confusión")
    fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale="Blues",
                       labels=dict(x="Predicción", y="Real", color="Cantidad"))
    st.plotly_chart(fig_cm, use_container_width=True)
    st.markdown("""
    - Esta matriz compara las predicciones generadas por el modelo con los valores reales del conjunto de prueba (y_test), después de entrenar sobre una muestra de entrenamiento (X_train, y_train).
    - Las variables con mayor influencia en la predicción fueron los likes y la cantidad de comentarios.
    - El análisis permite identificar con buena precisión qué características impulsan la viralidad
    """)


    st.subheader("📋 Reporte de Clasificación")
    st.markdown("""
    - **Precision**: Mide qué tan precisas son las predicciones positivas del modelo. En este caso, el 90% de los videos clasificados como *no populares* (clase 0) efectivamente no lo son, y el 89% de los videos predichos como *populares* (clase 1) realmente lo son. Esto indica una alta precisión en ambas clases.

    - **Recall**: Mide la capacidad del modelo para encontrar todos los casos verdaderos de una clase. El modelo identifica correctamente el 97% de los videos realmente *no populares*, pero solo el 67% de los videos que realmente fueron *populares*. Esto sugiere que, aunque el modelo es muy eficaz para reconocer los que no son populares, podría mejorar su sensibilidad para detectar los que sí lo son.

    - **F1-score**: Es el promedio armónico entre precisión y recall. Tiene un valor alto (0.93 para clase 0 y 0.76 para clase 1), lo que indica un buen equilibrio entre ambas métricas, especialmente para los videos no populares.

    - **Support**: Representa cuántos videos reales pertenecen a cada clase dentro del conjunto de prueba. En este caso, hubo 7664 videos no populares y 2574 populares evaluados. Esta diferencia explica parcialmente por qué el recall en la clase 1 es más bajo: hay menos ejemplos positivos que aprender.

    - **Accuracy**: El modelo tiene una exactitud general del 90%, lo que significa que 9 de cada 10 predicciones fueron correctas.

    - **Macro avg y Weighted avg**:  
        - **Macro avg** promedia las métricas de ambas clases sin considerar su proporción, lo que ayuda a identificar si hay desbalance.  
        - **Weighted avg** promedia las métricas considerando cuántos datos hay por clase (el soporte), y refleja mejor el rendimiento general cuando las clases están desbalanceadas.
    """)

    st.dataframe(pd.DataFrame(report).transpose().round(2))


    st.subheader("📌 Importancia de Variables (Coeficientes)")
    st.markdown("""
    Según los resultados obtenidos:

    - La longitud del título (title_length) y la cantidad de etiquetas (tag_count) son las variables más influyentes y con impacto positivo. Es decir, los títulos más largos y videos con más etiquetas tienden a ser más populares.
    - Las variables como dislikes, desc_length, likes y comment_count tienen coeficientes cercanos a cero o negativos, lo que sugiere un menor o nulo impacto en la predicción del modelo.
    
    Estas interpretaciones ayudan a comprender cómo el modelo toma decisiones y qué características podrían potenciar el alcance de un video.
    """)

    coef_df = pd.DataFrame({
        "Variable": X.columns,
        "Coeficiente": modelo.coef_[0]
    }).sort_values(by="Coeficiente", key=abs, ascending=False)
    st.dataframe(coef_df.style.format({"Coeficiente": "{:.4f}"}))

    st.subheader("📈 Predicción Manual ")

    with st.form("form_predict"):
        likes = st.number_input("Likes", min_value=0, value=1000)
        dislikes = st.number_input("Dislikes", min_value=0, value=50)
        comments = st.number_input("Comentarios", min_value=0, value=200)
        title_len = st.number_input("Longitud del título", min_value=0, value=30)
        desc_len = st.number_input("Longitud de la descripción", min_value=0, value=150)
        tags = st.number_input("Cantidad de tags", min_value=0, value=5)
        submitted = st.form_submit_button("Predecir Popularidad")

        if submitted:
            entrada = np.array([[likes, dislikes, comments, title_len, desc_len, tags]])
            pred = modelo.predict(entrada)[0]
            st.success(f"Resultado: **{'🔥 Video Popular' if pred == 1 else '👎 Poco Popular'}**")


elif opcion == preguntas[1]:
    cat_counts = df["category_name"].value_counts().head(10).reset_index()
    
    col1, col2 = st.columns([2, 1])  
    with col1:  
        fig = px.bar(cat_counts, x='count', y='category_name',
                    title=preguntas[1],
                    labels={'count': 'Cantidad de Videos', 'category_name': 'Categoría'}
                    ,color_discrete_sequence=["#0AF163"],
                    orientation='h')
        fig.update_layout(yaxis=dict(categoryorder="total ascending"), 
                          plot_bgcolor="#2b2b3d",
                          paper_bgcolor="#1e1e2f",   
                          font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:    
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
            <div style="color: #dddddd; font-size: 14px;">
                <ul>
                <li><b>Entertainment</b> se posiciona como la categoría líder en número de videos en tendencia, lo que evidencia su enorme capacidad para captar la atención de los usuarios. Esta categoría suele incluir contenido de celebridades, retos virales y programas de entretenimiento masivo.Le siguen de cerca <b>Music</b> y <b>Howto & Style</b>.</li>
                <li>Estas dos categorías en conjunto abarcan una porción significativa del contenido viral en YouTube, revelando una clara preferencia del público por formatos visualmente atractivos, emocionales o de fácil consumo.</li>
                <li>Además, este patrón puede reflejar tanto el algoritmo de recomendación de la plataforma como las estrategias de contenido de los creadores más influyentes.</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li><b>Entertainment</b> se posiciona como la categoría líder, lo que representa una oportunidad clave para orientar campañas hacia este tipo de contenido.</li>
                <li>Se recomienda a la empresa <b>crear o apoyar contenido de entretenimiento</b> para maximizar visibilidad y viralidad.</li>
                <li>Además, explorar categorías como <b>Music</b> y <b>Howto & Style</b> puede diversificar el impacto dentro de nichos populares.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        


elif opcion == preguntas[2]:
    likes_cat = df.groupby("category_name")["likes"].mean().sort_values().tail(10).reset_index()
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(likes_cat, x='likes', y='category_name',
                    title=preguntas[2],
                    labels={'likes': 'Likes Promedio', 'category_name': 'Categoría'},
                    orientation='h',
                    color_discrete_sequence=["#515BE6"])
        fig.update_layout(yaxis=dict(categoryorder="total ascending"), plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f",   font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Las categorías con más <b>likes en promedio</b> suelen ser <b>Music</b> y <b>Nonprofits & Activism</b>, lo que refleja su amplio alcance y la fuerte conexión emocional que generan en los espectadores.</li>
                <li>Estos contenidos tienden a provocar reacciones inmediatas, como dar "me gusta", debido a su valor de entretenimiento o fenómenos virales.</li>
                <li>Este comportamiento sugiere un alto nivel de <b>engagement</b>, especialmente en videos musicales, que suelen ser compartidos, comentados y revisitados con frecuencia.</li>
                <li>Además, esto podría estar influenciado por el algoritmo de YouTube, que prioriza este tipo de contenido en las recomendaciones, amplificando aún más su visibilidad.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Fomentar la creación de contenido viral como <b>videos musicales</b> o de <b>activismo</b> puede generar una mayor conexión con el público.</li>
                <li>Se aconseja alentar a sus clientes a aprovechar <b>temáticas musicales y sociales</b>.</li>
                <li>Estos datos permiten orientar campañas hacia formatos que históricamente generan más "me gusta" y respuestas afectivas.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif opcion == preguntas[3]:
    likes_cat = df.groupby("category_name")["likes"].mean().sort_values().head(10).reset_index()
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(likes_cat, x='likes', y='category_name',
                    title=preguntas[3],
                    labels={'likes': 'Likes Promedio', 'category_name': 'Categoría'},
                    orientation='h',
                    color_discrete_sequence=["#E02323"])
        fig.update_layout(yaxis=dict(categoryorder="total ascending"),  
                          plot_bgcolor="#2b2b3d", 
                          paper_bgcolor="#1e1e2f",   
                          font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Las categorías con <b>menos likes en promedio</b> incluyen <b>News & Politics</b>, <b>Autos & Vehicles</b> y <b>Travel & Events</b>, lo que puede reflejar un menor nivel de conexión emocional o viralidad en comparación con otras categorías.</li>
                <li>Este comportamiento sugiere que los usuarios tienden a interactuar menos con contenido que es más <b>informativo, técnico o situacional</b>, como noticias, coberturas de eventos o contenido especializado en automóviles.</li>
                <li>Además, estas categorías podrían estar dirigidas a <b>audiencias más específicas</b> o de nicho, lo cual limita el volumen general de reacciones como los "me gusta".</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Para mejorar la interacción, se recomienda explorar formas de hacer más atractivo el contenido informativo, técnico o de nicho.</li>
                <li>Incluir elementos visuales o enfoques emocionales puede aumentar la recepción de estos videos.</li>
                <li>También puede ser útil implementar <b>estrategias de microsegmentación</b> para alcanzar públicos realmente interesados.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif opcion == preguntas[4]:
    df["ratio_likes_dislikes"] = df["likes"] / (df["dislikes"] + 1)
    ratio_ld = df.groupby("category_name")["ratio_likes_dislikes"].mean().dropna().sort_values(ascending=False).head(10).reset_index()
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(ratio_ld, x='ratio_likes_dislikes', y='category_name',
                    title=preguntas[4],
                    labels={'ratio_likes_dislikes': 'Ratio Likes/Dislikes', 'category_name': 'Categoría'},
                    orientation='h',
                    color_discrete_sequence=["#9625F3"])
        fig.update_layout(yaxis=dict(categoryorder="total ascending"), plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f",   font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Un <b>alto ratio de Likes/Dislikes</b> indica que el contenido ha sido recibido de manera <b>muy positiva</b> por parte del público, reflejando aprobación y satisfacción general.</li>
                <li>Las categorías con los mejores promedios en este ratio son <b>Pets & Animals</b>, <b>Music</b> y <b>People & Blogs</b>, lo que sugiere que estos tipos de contenido generan reacciones predominantemente favorables.</li>
                <li>Estos temas suelen ser <b>emocionales, entretenidos o personales</b>, por lo que es más probable que provoquen "me gusta" en lugar de críticas.</li>
                <li>Este patrón puede ser útil para creadores que buscan <b>maximizar la aprobación del público</b>, ya que apunta hacia temáticas que despiertan simpatía y engagement positivo.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Promover contenido en categorías como <b>Pets & Animals</b>, <b>Music</b> y <b>People & Blogs</b> puede aumentar significativamente la aprobación del público.</li>
                <li>Estas áreas temáticas son ideales para <b>posicionar marcas con imagen positiva y emocional</b>.</li>
                <li>Se sugiere orientar campañas hacia experiencias agradables, familiares o personales.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif opcion == preguntas[5]:
    df["ratio_views_comments"] = df["views"] / (df["comment_count"] + 1)
    ratio_vc = df.groupby("category_name")["ratio_views_comments"].mean().dropna().sort_values(ascending=False).head(10).reset_index()
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(ratio_vc, x='ratio_views_comments', y='category_name',
                    title=preguntas[5],
                    labels={'ratio_views_comments': 'Ratio Views/Comments', 'category_name': 'Categoría'},
                    orientation='h',
                    color_discrete_sequence=["#332263"])
        fig.update_layout(yaxis=dict(categoryorder="total ascending"), plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f",   font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Un <b>alto ratio de comentarios por vistas</b> refleja una <b>audiencia altamente participativa</b>, que no solo consume el contenido, sino que también interactúa activamente con él.</li>
                <li>Las categorías que destacan en este aspecto son <b>People & Blogs</b> y <b>Science & Technology</b>, lo que sugiere que estos videos despiertan opiniones, preguntas o emociones que llevan a los usuarios a comentar.</li>
                <li>Esto puede deberse a que se abordan <b>temas personales, científicos o de actualidad</b> que generan discusión.</li>
                <li>Para los creadores de contenido, este ratio es una métrica clave para identificar <b>contenidos que promueven comunidad y conversación</b>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Fomentar contenido en categorías que generen conversación como <b>People & Blogs</b> o <b>Science & Technology</b> puede ayudar a construir comunidades activas.</li>
                <li>Se recomienda utilizar <b>llamados a la acción</b> y temáticas participativas para incentivar los comentarios.</li>
                <li>La agencia puede enfocar campañas en formatos que promuevan el debate o interacción reflexiva.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif opcion == preguntas[6]:
    trend_counts = df["trending_date_dt"].value_counts().sort_index().reset_index()
    trend_counts.columns = ['Fecha', 'Cantidad']
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.line(trend_counts, x='Fecha', y='Cantidad',
                    title=preguntas[6],
                    labels={'Fecha': 'Fecha', 'Cantidad': 'Cantidad de Videos'})
        fig.update_layout(plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f", font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Se observa una <b>tendencia creciente</b> en la cantidad de videos en tendencia a lo largo del tiempo, lo cual sugiere un ecosistema más activo y competitivo en YouTube.</li>
                <li>El <b>pico más notable ocurre en febrero de 2018</b>, lo que podría estar relacionado con <b>eventos virales específicos, lanzamientos importantes</b> o campañas globales que impulsaron masivamente la visibilidad de ciertos contenidos.</li>
                <li>Este comportamiento estacional puede reflejar también <b>factores externos</b> como festividades, vacaciones o coyunturas mediáticas que incentivan el consumo digital.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)    
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
<div style="color: #dddddd; font-size: 14px;">
    <ul>
        <li>Planificar campañas considerando <b>picos estacionales</b> y tendencias históricas puede mejorar el alcance y la oportunidad del contenido.</li>
        <li>Se aconseja a la empresa vincular sus publicaciones con <b>eventos de alto tráfico digital</b> como festividades o lanzamientos virales.</li>
        <li>Analizar el comportamiento temporal puede ayudar a prever y aprovechar momentos óptimos de visibilidad.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

elif opcion == preguntas[7]:
    chan_counts = df["channel_title"].value_counts().head(10).reset_index()
    chan_counts.columns = ['Canal', 'Cantidad']
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(chan_counts, x='Canal', y='Cantidad',
                    title=preguntas[7],
                    labels={'count': 'Cantidad', 'channel_title': 'Canal'},
                    color_discrete_sequence=["#24B973"])
        fig.update_layout(plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f", font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Identificar estos canales líderes permite entender qué tipo de contenido tiene mayor potencial de tendencia y qué prácticas editoriales son efectivas en YouTube.</li>
                <li>Esto sugiere que los eventos deportivos, resúmenes, entrevistas y momentos destacados generan <b>alto engagement y viralidad</b> en la plataforma.</li>
                <li>El dominio de canales como ESPN también puede atribuirse a una <b>estrategia de publicación consistente</b>, aprovechamiento de fechas clave (como partidos o torneos importantes) y una base de audiencia fiel y activa.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
<div style="color: #dddddd; font-size: 14px;">
    <ul>
        <li>Estudiar el contenido de canales líderes como ESPN puede revelar prácticas efectivas de engagement y contenido.</li>
        <li>La empresa puede recomendar replicar estas estrategias, adaptándolas a otras temáticas como tecnología o educación.</li>
        <li>También se sugiere alinear publicaciones con <b>eventos relevantes</b> para aprovechar picos de atención masiva.</li>
    </ul>
</div>
""", unsafe_allow_html=True)


elif opcion == preguntas[8]:
    chan_counts = df["channel_title"].value_counts().tail(10).reset_index()
    chan_counts.columns = ['Canal', 'Cantidad']
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(chan_counts, x='Canal', y='Cantidad',
                    title=preguntas[8],
                    labels={'count': 'Cantidad', 'channel_title': 'Canal'},
                    color_discrete_sequence=["#CF3BFC"])
        fig.update_layout(plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f", font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Los canales con menor frecuencia en tendencias suelen ser <b>creadores emergentes o especializados en nichos</b> poco explotados.</li>
                <li>Estos canales representan una <b>gran oportunidad para descubrir contenido auténtico y fresco</b> que aún no ha alcanzado la viralidad masiva.</li>
                <li>Analizar este grupo ayuda a identificar <b>nuevas voces y tendencias incipientes</b> que podrían crecer con mayor exposición o cambios en el algoritmo de recomendación.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
<div style="color: #dddddd; font-size: 14px;">
    <ul>
        <li>Explorar colaboraciones con <b>creadores emergentes</b> puede ofrecer acceso a audiencias nuevas y nichos poco saturados.</li>
        <li>La agencia podría mapear estos canales para identificar oportunidades de <b>coproducción o patrocinio</b>.</li>
        <li>También es posible utilizar estas colaboraciones para probar nuevos formatos o enfoques.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

elif opcion == preguntas[9]:
    state_summary = df.groupby("state").agg({
        "views": "sum",
        "likes": "sum",
        "dislikes": "sum",
        "lat": "mean",
        "lon": "mean"
    }).reset_index()
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.scatter_mapbox(
            state_summary,
            lat="lat", lon="lon",
            size="likes", color="likes",
            color_continuous_scale="plasma",
            size_max=25, zoom=3,
            hover_name="state",
            hover_data={"views": True, "likes": True, "dislikes": True},
            title=preguntas[9]
        )
        fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":50,"l":0,"b":0}, 
                          plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f",   font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Algunos estados sobresalen significativamente en el volumen de <b>vistas, likes y dislikes</b>, lo que sugiere una mayor participación de usuarios en estas regiones.</li>
                <li>Este comportamiento puede estar vinculado a factores como <b>densidad poblacional, acceso a internet, y cultura digital activa</b>.</li>
                <li>Estados con grandes centros urbanos o fuerte presencia de creadores de contenido tienden a generar más interacciones.</li>
                <li>El análisis geográfico permite detectar <b>focos de influencia cultural</b> dentro del país, así como identificar <b>posibles mercados clave</b> para campañas o estrategias de contenido.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
<div style="color: #dddddd; font-size: 14px;">
    <ul>
        <li>Analizar la geolocalización del engagement permite orientar campañas según <b>hábitos de consumo por región</b>.</li>
        <li>Se recomienda crear contenido adaptado a estados con alto volumen de likes y vistas.</li>
        <li>También puede aprovecharse para <b>personalizar estrategias publicitarias regionales</b>.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
        
        
elif opcion == preguntas[10]:
    top_com = df.sort_values("comment_count", ascending=False).head(10)
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(top_com, x="comment_count", y="title", orientation='h',
                    title=preguntas[10],
                    labels={"comment_count": "Comentarios", "title": "Título del Video"},
                    color_discrete_sequence=["#F07050"])
        fig.update_layout(yaxis=dict(categoryorder="total ascending"), plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f",   font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Los videos con mayor cantidad de <b>comentarios</b> reflejan un <b>elevado nivel de participación</b> por parte de la audiencia, evidenciando una conexión emocional o intelectual significativa.</li>
                <li>Este tipo de contenido suele estar asociado a <b>temas de interés público, canciones o  videos altamente virales</b>.</li>
                <li>La sección de comentarios se convierte en un espacio activo donde la comunidad expresa <b>acuerdo, desacuerdo, humor o apoyo</b>, ampliando el alcance del video.</li>
                <li>Analizar estos videos puede ayudar a entender qué <b>temáticas generan conversación</b> y cómo fomentar mayor interacción en futuras publicaciones.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Los videos con más comentarios pueden ser aprovechados como referencia para replicar <b>temáticas de alto interés</b>.</li>
                <li>Se recomienda fomentar contenido polémico o emotivo para promover conversaciones significativas.</li>
                <li>Este enfoque puede posicionar a las marcas como actores relevantes en el diálogo digital.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif opcion == preguntas[11]:
    corr = df[["views","likes","dislikes","comment_count"]].corr()
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.imshow(corr, text_auto=True, title=preguntas[11], color_continuous_scale='RdBu_r')
        fig.update_layout(plot_bgcolor="#2b2b3d", paper_bgcolor="#1e1e2f", font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown('<h3 style="color:#dddddd;">📝 Insights</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>Se observa una <b>fuerte correlación positiva</b> entre métricas clave como <b>vistas, likes y comentarios</b>, lo que indica que los videos más vistos también tienden a ser los más valorados e interactuados.</li>
                <li>Esta relación sugiere que <b>la popularidad de un video impulsa tanto la aprobación como la conversación</b> en torno a él, reforzando su visibilidad en la plataforma.</li>
                <li>En contraste, los <b>dislikes muestran menor correlación</b> con el resto de métricas, lo que podría indicar que la desaprobación no sigue necesariamente el mismo patrón de crecimiento que la popularidad general.</li>
                <li>Estas correlaciones pueden ser útiles para <b>predecir el rendimiento</b> de un video o evaluar el <b>impacto de una estrategia de contenido</b>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<h3 style="color:#dddddd;">💡 Recomendaciones</h3>', unsafe_allow_html=True)
        st.markdown("""
        <div style="color: #dddddd; font-size: 14px;">
            <ul>
                <li>El fuerte vínculo entre vistas, likes y comentarios puede guiar la <b>priorización de métricas clave</b> en el diseño de campañas.</li>
                <li>La empresa debería fomentar contenido que combine <b>visual appeal</b> con capacidad de generar conversación.</li>
                <li>También se sugiere monitorear los dislikes para evitar impactos negativos en la percepción de marca.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


