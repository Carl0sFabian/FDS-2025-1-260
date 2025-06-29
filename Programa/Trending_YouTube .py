import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import plotly.express as px

csv_path = "Programa/data/USvideos_cc50_202101.csv"
json_path = "Programa/data/US_category_id.json"
pais = "EE.UU"

print(f"\n\n📊 === {pais.upper()} ===")
df = pd.read_csv(csv_path)

with open(json_path, "r", encoding="utf-8") as f:
    items = json.load(f)["items"]
    cat_map = {int(i["id"]): i["snippet"]["title"] for i in items}
df["category_name"] = df["category_id"].map(cat_map)

# -------------------------------
# INSPECCIÓN INICIAL
# -------------------------------
print("✔️ Estructura:", df.shape)
print("\n✔️ Tipos de columnas:\n", df.dtypes)
print("\n✔️ Nulos por columna:\n", df.isnull().sum())
print("\n✔️ Valores únicos por columna:\n", df.nunique())

freq_cat = df["category_name"].value_counts().head(10)
print("\n✔️ Tabla de frecuencia (categorías top 10):\n", freq_cat)

print("\n🔍 VERIFICACIÓN DE CALIDAD")
for col in ["views", "likes", "dislikes", "comment_count"]:
    if (df[col] < 0).any():
        print(f"⚠️ {col} contiene valores negativos")
    else:
        print(f"✔️ {col} no contiene valores negativos")

incons_com = df[(df["comments_disabled"] == True) & (df["comment_count"] > 0)]
print(f"🔗 Inconsistencias comments_disabled: {len(incons_com)} registros")

incons_rat = df[(df["ratings_disabled"] == True) & ((df["likes"] > 0) | (df["dislikes"] > 0))]
print(f"🔗 Inconsistencias ratings_disabled: {len(incons_rat)} registros")

for col in ["views", "likes", "dislikes", "comment_count"]:
    q999 = df[col].quantile(0.999)
    out = df[df[col] > q999]
    print(f"📈 {col}: {len(out)} registros sobre el p99.9")

# -------------------------------
# PREPARACIÓN DE LOS DATOS
# -------------------------------
print("\n🛠️ PREPARACIÓN DE LOS DATOS")
df["description"] = df["description"].fillna("Sin descripción")
df["state"]       = df["state"].fillna("Desconocido")
df["lat"]         = df["lat"].fillna(0.0)
df["lon"]         = df["lon"].fillna(0.0)

for col in ["views","likes","dislikes","comment_count"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    lim = df[col].quantile(0.999)
    df[col] = np.where(df[col] > lim, lim, df[col])

df["log_views"]       = np.log1p(df["views"])
df["title_length"]    = df["title"].astype(str).apply(len)
df["desc_length"]     = df["description"].astype(str).apply(len)
df["tag_count"]       = df["tags"].astype(str)\
                             .apply(lambda x: len(x.split("|")) if x!="[None]" else 0)
df["publish_hour"]    = pd.to_datetime(df["publish_time"], errors="coerce").dt.hour
df["trending_date_dt"]= pd.to_datetime(df["trending_date"],
                                       format="%y.%d.%m", errors="coerce")

clean_path = "Programa/data_limpios/EEUU_limpio.csv"
df.to_csv(clean_path, index=False)
print(f"✅ Datos limpios guardados en: {clean_path}")

# ----------------------------------
# GRÁFICOS RESPUESTAS P1 - P9
# ----------------------------------

# 1. Categorías más frecuentes
cat_counts = df["category_name"].value_counts().head(10)
plt.figure(figsize=(10,6))
sns.barplot(x=cat_counts.values, y=cat_counts.index, palette="viridis")
plt.title("1. Categorías con mayor número de videos en tendencia")
plt.xlabel("Cantidad de videos"); plt.ylabel("Categoría")
plt.tight_layout(); plt.show()

# 2. Más y menos gustadas
likes_cat = df.groupby("category_name")["likes"].mean().sort_values()
plt.figure(figsize=(10,6))
sns.barplot(x=likes_cat.values[-10:], y=likes_cat.index[-10:], palette="Blues_r")
plt.title("2a. Top 10 categorías con más likes promedio")
plt.xlabel("Likes promedio"); plt.tight_layout(); plt.show()

plt.figure(figsize=(10,6))
sns.barplot(x=likes_cat.values[:10], y=likes_cat.index[:10], palette="Reds_r")
plt.title("2b. Top 10 categorías con menos likes promedio")
plt.xlabel("Likes promedio"); plt.tight_layout(); plt.show()

# 3. Ratio Likes/Dislikes
df["ratio_likes_dislikes"] = df["likes"] / (df["dislikes"] + 1)
ratio_ld = df.groupby("category_name")["ratio_likes_dislikes"]\
             .mean().dropna().sort_values(ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(x=ratio_ld.values, y=ratio_ld.index, palette="magma")
plt.title("3. Top 10 categorías con mejor ratio Likes/Dislikes")
plt.xlabel("Ratio promedio"); plt.tight_layout(); plt.show()

# 4. Ratio Views/Comments
df["ratio_views_comments"] = df["views"] / (df["comment_count"] + 1)
ratio_vc = df.groupby("category_name")["ratio_views_comments"]\
             .mean().dropna().sort_values(ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(x=ratio_vc.values, y=ratio_vc.index, palette="cividis")
plt.title("4. Top 10 categorías con mejor ratio Views/Comments")
plt.xlabel("Ratio promedio"); plt.tight_layout(); plt.show()

# 5. Volumen de videos por fecha
trend_counts = df["trending_date_dt"].value_counts().sort_index()
plt.figure(figsize=(12,6))
trend_counts.plot()
plt.title("5. Evolución de videos en tendencia por fecha")
plt.xlabel("Fecha"); plt.ylabel("Cantidad de videos")
plt.grid(True); plt.tight_layout(); plt.show()

# 6. Canales más y menos frecuentes
chan_counts = df["channel_title"].value_counts()
plt.figure(figsize=(10,6))
sns.barplot(x=chan_counts.values[:10], y=chan_counts.index[:10], palette="crest")
plt.title("6a. Top 10 canales con más tendencias")
plt.xlabel("Cantidad"); plt.tight_layout(); plt.show()

plt.figure(figsize=(10,6))
sns.barplot(x=chan_counts.values[-10:], y=chan_counts.index[-10:], palette="flare")
plt.title("6b. Top 10 canales con menos tendencias")
plt.xlabel("Cantidad"); plt.tight_layout(); plt.show()

# 7. Mapa de Vistas, Likes y Dislikes por Estado
state_summary = df.groupby("state").agg({
    "views":    "sum",
    "likes":    "sum",
    "dislikes": "sum",
    "lat":      "mean",
    "lon":      "mean"
}).reset_index()

fig = px.scatter_mapbox(
    state_summary,
    lat="lat", lon="lon",
    size="likes", color="likes",
    color_continuous_scale="plasma",
    size_max=25, zoom=3,
    hover_name="state",
    hover_data={"views":True,"likes":True,"dislikes":True},
    title="7. USA - Vistas, Me gusta y No me gusta por Estado"
)
fig.update_layout(mapbox_style="carto-positron",
                  margin={"r":0,"t":50,"l":0,"b":0})
fig.show()

# 8. Top 10 videos con más comentarios
top_com = df.sort_values("comment_count", ascending=False).head(10)
plt.figure(figsize=(10,6))
sns.barplot(y="title", x="comment_count", data=top_com, palette="rocket")
plt.title("8. Top 10 Videos con más comentarios")
plt.xlabel("Número de comentarios"); plt.ylabel("Título del Video")
plt.tight_layout(); plt.show()

# 9. Correlación entre métricas
corr = df[["views","likes","dislikes","comment_count"]].corr()
plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm")
plt.title("9. Matriz de correlación entre Views, Likes, Dislikes y Comments")
plt.tight_layout(); plt.show()
