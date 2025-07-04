import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(page_title="Dashboard de Videos en Tendencia", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_csv("FDS-2025-1-260/Programa/data_limpios/EEUU_limpio.csv")
    with open("FDS-2025-1-260/Programa/data/US_category_id.json", "r", encoding="utf-8") as f:
        cat_map = {int(i["id"]): i["snippet"]["title"] for i in json.load(f)["items"]}
    df["category_name"] = df["category_id"].map(cat_map)
    df["trending_date_dt"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m", errors="coerce")
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    df["publish_year"] = df["publish_time"].dt.year
    return df

df = cargar_datos()

preguntas = [
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
    "9. Matriz de correlación",
]

opcion = st.selectbox("Elige la pregunta a graficar", preguntas)

if opcion == preguntas[0]:
    cat_counts = df["category_name"].value_counts().head(10).reset_index()
    fig = px.bar(cat_counts, x='count', y='category_name',
                 title=preguntas[0],
                 labels={'count': 'Cantidad de Videos', 'category_name': 'Categoría'},
                 orientation='h')
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[1]:
    likes_cat = df.groupby("category_name")["likes"].mean().sort_values().tail(10).reset_index()
    fig = px.bar(likes_cat, x='likes', y='category_name',
                 title=preguntas[1],
                 labels={'likes': 'Likes Promedio', 'category_name': 'Categoría'},
                 orientation='h')
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[2]:
    likes_cat = df.groupby("category_name")["likes"].mean().sort_values().head(10).reset_index()
    fig = px.bar(likes_cat, x='likes', y='category_name',
                 title=preguntas[2],
                 labels={'likes': 'Likes Promedio', 'category_name': 'Categoría'},
                 orientation='h')
    fig.update_layout(yaxis=dict(categoryorder="total descending"))
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[3]:
    df["ratio_likes_dislikes"] = df["likes"] / (df["dislikes"] + 1)
    ratio_ld = df.groupby("category_name")["ratio_likes_dislikes"].mean().dropna().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(ratio_ld, x='ratio_likes_dislikes', y='category_name',
                 title=preguntas[3],
                 labels={'ratio_likes_dislikes': 'Ratio Likes/Dislikes', 'category_name': 'Categoría'},
                 orientation='h')
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[4]:
    df["ratio_views_comments"] = df["views"] / (df["comment_count"] + 1)
    ratio_vc = df.groupby("category_name")["ratio_views_comments"].mean().dropna().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(ratio_vc, x='ratio_views_comments', y='category_name',
                 title=preguntas[4],
                 labels={'ratio_views_comments': 'Ratio Views/Comments', 'category_name': 'Categoría'},
                 orientation='h')
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[5]:
    trend_counts = df["trending_date_dt"].value_counts().sort_index().reset_index()
    fig = px.line(trend_counts, x='trending_date_dt', y='count',
                  title=preguntas[5],
                  labels={'trending_date_dt': 'Fecha', 'count': 'Cantidad de Videos'})
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[6]:
    chan_counts = df["channel_title"].value_counts().head(10).reset_index()
    fig = px.bar(chan_counts, x='channel_title', y='count',
                 title=preguntas[6],
                 labels={'count': 'Cantidad', 'channel_title': 'Canal'})
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[7]:
    chan_counts = df["channel_title"].value_counts().tail(10).reset_index()
    fig = px.bar(chan_counts, x='channel_title', y='count',
                 title=preguntas[7],
                 labels={'count': 'Cantidad', 'channel_title': 'Canal'})
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[8]:
    state_summary = df.groupby("state").agg({
        "views": "sum",
        "likes": "sum",
        "dislikes": "sum",
        "lat": "mean",
        "lon": "mean"
    }).reset_index()
    fig = px.scatter_mapbox(
        state_summary,
        lat="lat", lon="lon",
        size="likes", color="likes",
        color_continuous_scale="plasma",
        size_max=25, zoom=3,
        hover_name="state",
        hover_data={"views": True, "likes": True, "dislikes": True},
        title=preguntas[8]
    )
    fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":50,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[9]:
    top_com = df.sort_values("comment_count", ascending=False).head(10)
    fig = px.bar(top_com, x="comment_count", y="title", orientation='h',
                 title=preguntas[9],
                 labels={"comment_count": "Comentarios", "title": "Título del Video"})
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)

elif opcion == preguntas[10]:
    corr = df[["views","likes","dislikes","comment_count"]].corr()
    fig = px.imshow(corr, text_auto=True, title=preguntas[10], color_continuous_scale='RdBu_r')
    st.plotly_chart(fig, use_container_width=True)