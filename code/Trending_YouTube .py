import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

csv_path = "data/USvideos_cc50_202101.csv"
json_path = "data/US_category_id.json"
pais = "EE.UU"

os.makedirs("data_limpios", exist_ok=True)

print(f"\n\n📊 === {pais.upper()} ===")
df = pd.read_csv(csv_path)

with open(json_path, "r", encoding="utf-8") as f:
    cat_data = json.load(f)
    cat_map = {int(item['id']): item['snippet']['title'] for item in cat_data['items']}
df["category_name"] = df["category_id"].map(cat_map)

# INSPECCIÓN
print("✔️ Estructura:", df.shape)
print("\n✔️ Tipos de columnas:\n", df.dtypes)
print("\n✔️ Nulos por columna:\n", df.isnull().sum())
print("\n✔️ Valores únicos por columna:\n", df.nunique())

freq_cat = df["category_name"].value_counts().head(10)
print("\n✔️ Tabla de frecuencia (categorías top 10):\n", freq_cat)

# VERIFICACIÓN DE CALIDAD DE LOS DATOS
print("\n🔍 VERIFICACIÓN DE CALIDAD")

for col in ["views", "likes", "dislikes", "comment_count"]:
    if (df[col] < 0).any():
        print(f"⚠️ {col} contiene valores negativos")
    else:
        print(f"✔️ {col} no contiene valores negativos")

inconsistentes_com = df[(df["comments_disabled"] == True) & (df["comment_count"] > 0)]
print(f"🔗 Inconsistencias comments_disabled: {len(inconsistentes_com)} registros")

inconsistentes_rat = df[(df["ratings_disabled"] == True) & ((df["likes"] > 0) | (df["dislikes"] > 0))]
print(f"🔗 Inconsistencias ratings_disabled: {len(inconsistentes_rat)} registros")

for col in ["views", "likes", "dislikes", "comment_count"]:
    q999 = df[col].quantile(0.999)
    outliers = df[df[col] > q999]
    print(f"📈 {col}: {len(outliers)} registros sobre el p99.9")

# PREPARACIÓN DE LOS DATOS
print("\n🛠️ PREPARACIÓN DE LOS DATOS")

# Limpiar datos faltantes
df["description"] = df["description"].fillna("Sin descripción")
df["state"] = df["state"].fillna("Desconocido")
df["lat"] = df["lat"].fillna(0.0)
df["lon"] = df["lon"].fillna(0.0)

# Winsorización por p99.9
for col in ["views", "likes", "dislikes", "comment_count"]:
    limite = df[col].quantile(0.999)
    df[col] = np.where(df[col] > limite, limite, df[col])

# Construcción de nuevos datos
df["log_views"] = np.log1p(df["views"])
df["title_length"] = df["title"].astype(str).apply(len)
df["desc_length"] = df["description"].astype(str).apply(len)
df["tag_count"] = df["tags"].astype(str).apply(lambda x: len(x.split("|")) if x != "[None]" else 0)
df["publish_hour"] = pd.to_datetime(df["publish_time"], errors='coerce').dt.hour
df["trending_day"] = pd.to_datetime(df["trending_date"], errors='coerce', format="%y.%d.%m").dt.dayofweek

# Guardar CSV limpio
clean_path = "data_limpios/EEUU_limpio.csv"
df.to_csv(clean_path, index=False)
print(f"✅ Datos limpios guardados en: {clean_path}")

# VISUALIZACIONES
plt.figure(figsize=(10, 6))
sns.histplot(df["log_views"], bins=50, kde=True)
plt.title(f"Distribución logarítmica de vistas - {pais}")
plt.xlabel("log(views + 1)")
plt.ylabel("Frecuencia")
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
sns.barplot(x=freq_cat.values, y=freq_cat.index, palette="viridis")
plt.title(f"Top 10 categorías por cantidad de videos - {pais}")
plt.xlabel("Cantidad de videos")
plt.ylabel("Categoría")
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))
sns.countplot(x="publish_hour", data=df, palette="coolwarm")
plt.title(f"Frecuencia de publicación por hora - {pais}")
plt.xlabel("Hora del día")
plt.ylabel("Cantidad de videos")
plt.grid(True)
plt.tight_layout()
plt.show()
