import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="YouTube Trending Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTILO CSS PARA RÉPLICA EXACTA Y CONTROL DE CONTENEDORES
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp { background-color: #1e1e2f; color: white; font-family: 'Inter', sans-serif; }
    
    /* TOPBAR */
    .topbar { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; background: #1e1e2f; margin-bottom: 20px; }
    .search-box { background: #2b2b3d; border-radius: 20px; padding: 8px 15px; border: none; color: white; width: 250px; font-size: 13px; }
    .user-info { display: flex; align-items: center; gap: 12px; }
    .avatar { background-color: #444; padding: 8px; border-radius: 50%; font-size: 18px; border: 1px solid #555; }

    /* KPI CARDS */
    .highlights { display: flex; gap: 15px; margin-bottom: 20px; }
    .highlight-card { flex: 1; padding: 20px; border-radius: 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .yellow { background-color: #ffe066; color: #333 !important; }
    .blue { background-color: #2de1fc; color: #333 !important; }
    .green { background-color: #00ffae; color: #333 !important; }
    .pink { background-color: #ff77e9; color: #333 !important; }
    .hc-value { font-size: 26px; font-weight: 800; display: block; }
    .hc-label { font-size: 12px; font-weight: 600; opacity: 0.8; }

    /* CONTENEDORES Y CARDS */
    .card-dark { background-color: #2b2b3d; padding: 20px; border-radius: 20px; border: 1px solid #3d3d5c; margin-bottom: 15px; }
    .card-usa { 
        background-color: #2b2b3d; padding: 20px; border-radius: 20px; border: 1px solid #3d3d5c; 
        height: 385px; display: flex; flex-direction: column; overflow: hidden;
    }
    .card-black { background-color: #151522; padding: 20px; border-radius: 15px; border: 1px solid #333; height: 100%; }
    h4 { color: white !important; font-size: 16px; margin-bottom: 15px; font-weight: 600; }
    
    /* BARRAS DE PROGRESO */
    .progress-container { margin-bottom: 18px; }
    .progress-label { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; color: #bbb; }
    .progress-bar-bg { background: #151522; border-radius: 10px; height: 10px; width: 100%; overflow: hidden; }
    .progress-fill { background: linear-gradient(90deg, #a88beb, #6c5ce7); height: 100%; border-radius: 10px; }

    /* TABLA DE FRECUENCIA */
    .freq-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #3d3d5c; font-size: 13px; }
    .freq-val { background: #1e1e2f; padding: 2px 8px; border-radius: 5px; color: #fff; font-weight: 600; }

    /* IMAGENES */
    .bandera-img { width: 100%; border-radius: 10px; margin-top: auto; object-fit: cover; height: 150px; }

    /* INSIGHT BOXES */
    .insight-box { background: #1e1e2f; padding: 15px; border-left: 4px solid #a88beb; border-radius: 5px; margin-top: 10px; color: #ddd; font-size: 14px; }
    .recom-box { background: #1e1e2f; padding: 15px; border-left: 4px solid #00ffae; border-radius: 5px; margin-top: 10px; color: #ddd; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# 3. CARGA DE DATOS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_all_data():
    try:
        df = pd.read_csv(os.path.join(BASE_DIR, "data", "USvideos_cc50_202101.csv"))
        # Conversión de fechas para análisis temporal
        df['trending_date_dt'] = pd.to_datetime(df['trending_date'], format='%y.%d.%m', errors='coerce')
        
        with open(os.path.join(BASE_DIR, "data", "US_category_id.json"), "r") as f:
            cat_map = {int(i["id"]): i["snippet"]["title"] for i in json.load(f)["items"]}
        df["category_name"] = df["category_id"].map(cat_map)
        
        for col in ["views", "likes", "dislikes", "comment_count"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

df = load_all_data()

# 4. TOPBAR
st.markdown(f"""
<div class="topbar">
    <input type="text" class="search-box" placeholder="Search here...">
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png" width="35">
        <span style="font-size: 18px; font-weight: 700; color: white;">Trending YouTube Intelligence</span>
    </div>
    <div class="user-info">
        <div style="text-align: right; line-height: 1.1;">
            <div style="font-weight: 700; font-size: 14px; color: white;">Carlos Fabian</div>
            <div style="font-size: 11px; color: #888;">U20231c416@upc.edu.pe</div>
        </div>
        <div class="avatar">👦🏻</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. SIDEBAR
with st.sidebar:
    st.markdown("<div style='text-align:center; padding: 10px 0;'><img src='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQpI1JP5xjaPFWiCELO6_0nai_eVLttOmL4og&s' width='40'></div>", unsafe_allow_html=True)
    menu = st.radio("MENÚ PRINCIPAL", ["🏠 Inicio", "❗ Proyecto", "🗃️ Datos", "📊 Análisis Detallado"])

# 6. LÓGICA DE NAVEGACIÓN
if "Inicio" in menu:
    # KPIs
    st.markdown(f"""
    <div class="highlights">
        <div class="highlight-card yellow"><div><span class="hc-value">40,949</span><span class="hc-label">Registros Analizados</span></div><span style="font-size:24px;">💾</span></div>
        <div class="highlight-card blue"><div><span class="hc-value">{df['likes'].sum():,.0f}</span><span class="hc-label">Total Likes</span></div><span style="font-size:24px;">👍</span></div>
        <div class="highlight-card green"><div><span class="hc-value">{df['views'].sum():,.0f}</span><span class="hc-label">Total Vistas</span></div><span style="font-size:24px;">👁️</span></div>
        <div class="highlight-card pink"><div><span class="hc-value">{df['comment_count'].sum():,.0f}</span><span class="hc-label">Comentarios</span></div><span style="font-size:24px;">💬</span></div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1.2, 1, 0.8])

    with col_left:
        st.markdown('<div class="card-dark"><h4>Distribución Geográfica (Top 10)</h4>', unsafe_allow_html=True)
        state_data = df['state'].value_counts().head(10).reset_index()
        fig_st = px.bar(state_data, x='state', y='count', color='state', template="plotly_dark", height=300)
        fig_st.update_layout(showlegend=False, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_st, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_mid:
        st.markdown(f"""
        <div class="card-usa">
            <h4>Panorama Digital: EE.UU.</h4>
            <p style="font-size:13px; color:#aaa;">Estados Unidos representa el mercado más maduro de YouTube. La alta densidad de creadores permite que las tendencias se propaguen de forma segmentada pero masiva entre los 50 estados.</p>
            <img src="https://flagcdn.com/w640/us.png" class="bandera-img">
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card-dark"><h4>Estructura de Datos</h4>', unsafe_allow_html=True)
        fig_pie = px.pie(values=[10, 5, 3], names=['Cualitativos', 'Enteros', 'Flotantes'], hole=.6, height=180, template="plotly_dark")
        fig_pie.update_layout(margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card-dark"><h4>Densidad de Interacción</h4>', unsafe_allow_html=True)
        for k, v in {"Views": 40478, "Likes": 29850, "Comments": 13773}.items():
            perc = (v / 40478) * 100
            st.markdown(f"""<div class="progress-container"><div class="progress-label"><span>{k}</span><span>{v:,}</span></div>
            <div class="progress-bar-bg"><div class="progress-fill" style="width:{perc}%;"></div></div></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "❗ Proyecto":
    c1, c2, c3 = st.columns([1, 1, 0.7])
    with c1: st.markdown('<div class="card-black"><h4 style="color:#63b3ed;">🌐 Contexto</h4><p style="font-size:13px;">Exploración profunda de algoritmos de viralidad y comportamiento de audiencias digitales en el mercado estadounidense.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="card-black"><h4 style="color:#f687b3;">🎯 Objetivo</h4><p style="font-size:13px;">Extraer patrones de éxito mediante métricas de engagement (likes, views, comments) para predecir tendencias.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="card-black"><h4 style="color:#68d391;">📈 Valor</h4><p style="font-size:13px;">Transformar datos crudos en estrategias de posicionamiento y optimización de inversión publicitaria.</p></div>', unsafe_allow_html=True)

elif menu == "🗃️ Datos":
    st.markdown('<div class="card-dark"><h4>Exploración del Dataset</h4>', unsafe_allow_html=True)
    st.dataframe(df.head(100), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 7. SECCIÓN ANÁLISIS DETALLADO (PREGUNTAS) - AQUÍ ESTÁ LA CORRECCIÓN DE INDENTACIÓN
else:
    st.markdown('<div class="card-dark"><h2>📊 Análisis de Inteligencia de Audiencias</h2>', unsafe_allow_html=True)
    opcion = st.selectbox("Selecciona la pregunta de análisis:", [
        "1. Categorías con mayor número de videos",
        "2a. Categorías con más likes promedio",
        "2b. Categorías con menos likes promedio",
        "3. Mejor ratio Likes/Dislikes",
        "4. Mejor ratio Views/Comments",
        "5. Evolución por fecha",
        "6a. Top canales con más tendencias",
        "7. Mapa de Interacción por Estado",
        "8. Videos con más comentarios",
        "9. Matriz de correlación"
    ])
    
    cg, ct = st.columns([2, 1])
    
    # TODA LA LÓGICA DE LAS GRÁFICAS ESTÁ DENTRO DE ESTE BLOQUE ELSE
    if "1." in opcion:
        with cg: st.plotly_chart(px.bar(df["category_name"].value_counts().head(10).reset_index(), x='count', y='category_name', orientation='h', color_discrete_sequence=["#0AF163"], template="plotly_dark"), use_container_width=True)
        with ct: 
            st.markdown('<div class="insight-box"><h4>📝 Insights</h4><li><b>Saturación de Entretenimiento:</b> La categoría domina el feed, indicando que el algoritmo prioriza el "escapismo" masivo.</li><li><b>Fricción de Consumo:</b> Music y Howto & Style reflejan una audiencia que busca utilidad rápida.</li></div>', unsafe_allow_html=True)
            st.markdown('<div class="recom-box"><h4>💡 Recomendación</h4><li><b>Oportunidad de Nicho:</b> Si la marca no es de ocio, debe usar el formato "Infotainment" para competir por la atención.</li></div>', unsafe_allow_html=True)
    
    elif "2a." in opcion:
        with cg: st.plotly_chart(px.bar(df.groupby("category_name")["likes"].mean().sort_values().tail(10).reset_index(), x='likes', y='category_name', orientation='h', color_discrete_sequence=["#515BE6"], template="plotly_dark"), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Afinidad Emocional:</b> La música y el activismo generan una lealtad de marca mucho más profunda que el contenido puramente informativo.</div>', unsafe_allow_html=True)

    elif "2b." in opcion:
        with cg: st.plotly_chart(px.bar(df.groupby("category_name")["likes"].mean().sort_values().head(10).reset_index(), x='likes', y='category_name', orientation='h', color_discrete_sequence=["#E02323"], template="plotly_dark"), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Contenido Utilitario:</b> Noticias y Política reciben pocos likes porque el usuario consume por necesidad, resultando en un engagement funcional.</div>', unsafe_allow_html=True)

    elif "3." in opcion:
        with cg:
            df["ratio_ld"] = df["likes"] / (df["dislikes"] + 1)
            st.plotly_chart(px.bar(df.groupby("category_name")["ratio_ld"].mean().sort_values().tail(10).reset_index(), x='ratio_ld', y='category_name', orientation='h', color_discrete_sequence=["#9625F3"], template="plotly_dark"), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Zonas Seguras:</b> Pets & Animals posee el mayor ratio de aprobación. Es la categoría con menor riesgo reputacional para anunciantes.</div>', unsafe_allow_html=True)

    elif "4." in opcion:
        with cg:
            df["ratio_vc"] = df["views"] / (df["comment_count"] + 1)
            st.plotly_chart(px.bar(df.groupby("category_name")["ratio_vc"].mean().sort_values().tail(10).reset_index(), x='ratio_vc', y='category_name', orientation='h', color_discrete_sequence=["#332263"], template="plotly_dark"), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Comunidades Activas:</b> People & Blogs genera el mayor volumen de conversación. El contenido personal elimina la barrera entre creador y fan.</div>', unsafe_allow_html=True)

    elif "5." in opcion:
        with cg: 
            trend_counts = df["trending_date_dt"].value_counts().sort_index().reset_index()
            st.plotly_chart(px.line(trend_counts, x='trending_date_dt', y='count', title="Volumen de Tendencias", template="plotly_dark"), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Estacionalidad:</b> El pico de 2018 sugiere una respuesta a eventos externos masivos. La viralidad depende de ciclos culturales cortos.</div>', unsafe_allow_html=True)

    elif "6a." in opcion:
        with cg: st.plotly_chart(px.bar(df["channel_title"].value_counts().head(10).reset_index(), x='count', y='channel_title', orientation='h', color_discrete_sequence=["#24B973"], template="plotly_dark"), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Dominio Institucional:</b> Canales como ESPN demuestran que la frecuencia de publicación industrializada es la clave del éxito algorítmico.</div>', unsafe_allow_html=True)

    elif "7." in opcion:
        with cg:
            summary = df.groupby("state").agg({"views":"sum", "likes":"sum", "lat":"mean", "lon":"mean"}).reset_index()
            st.plotly_chart(px.scatter_mapbox(summary, lat="lat", lon="lon", size="views", color="likes", color_continuous_scale="plasma", zoom=3, mapbox_style="carto-positron"), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Geografía del Engagement:</b> Los nodos de interacción coinciden con centros urbanos. Los estados costeros concentran el capital cultural.</div>', unsafe_allow_html=True)

    elif "8." in opcion:
        with cg: st.plotly_chart(px.bar(df.sort_values("comment_count", ascending=False).head(10), x="comment_count", y="title", orientation='h', color_discrete_sequence=["#F07050"], template="plotly_dark"), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Puntos de Inflexión:</b> El comentario es la métrica de interacción más "costosa" y refleja un impacto psicológico profundo en el usuario.</div>', unsafe_allow_html=True)

    elif "9." in opcion:
        with cg: st.plotly_chart(px.imshow(df[["views","likes","dislikes","comment_count"]].corr(), text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)
        with ct: st.markdown('<div class="insight-box"><h4>📝 Insights</h4><b>Efecto Arrastre:</b> Las vistas impulsan orgánicamente los likes, pero el rechazo (dislikes) es una variable independiente de la fama.</div>', unsafe_allow_html=True)
