import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

file_paths = {
    "EE.UU": "data/EE.UU/USvideos_cc50_202101.csv",
    "Canadá": "data/Canadá/CAvideos_cc50_202101.csv",
    "Alemania": "data/Alemania/DEvideos_cc50_202101.csv",
    "México": "data/México/MXvideos_cc50_202101.csv",
    "Corea del Sur": "data/Korea del Surr/KRvideos_cc50_202101.csv"
}
json_paths = {
    "EE.UU": "data/EE.UU/US_category_id.json",
    "Canadá": "data/Canadá/CA_category_id.json",
    "Alemania": "data/Alemania/DE_category_id.json",
    "México": "data/México/MX_category_id.json",
    "Corea del Sur": "data/Korea del Surr/KR_category_id.json"
}

# Análisis por país
for pais in file_paths:
    print(f"\n\n📊 === {pais.upper()} ===")
    df = pd.read_csv(file_paths[pais])

    with open(json_paths[pais], "r", encoding="utf-8") as f:
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

    # VISUALIZACIÓN
    df["log_views"] = np.log1p(df["views"])
    df["publish_hour"] = pd.to_datetime(df["publish_time"], errors='coerce').dt.hour

    # 1. Histograma log(views)
    plt.figure(figsize=(10, 6))
    sns.histplot(df["log_views"], bins=50, kde=True)
    plt.title(f"Distribución logarítmica de vistas - {pais}")
    plt.xlabel("Views + 1)")
    plt.ylabel("Frecuencia")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 2. Categorías más frecuentes
    plt.figure(figsize=(10, 6))
    sns.barplot(x=freq_cat.values, y=freq_cat.index, palette="viridis")
    plt.title(f"Top 10 categorías por cantidad de videos - {pais}")
    plt.xlabel("Cantidad de videos")
    plt.ylabel("Categoría")
    plt.tight_layout()
    plt.show()

    # 3. Publicación por hora
    plt.figure(figsize=(10, 6))
    sns.countplot(x="publish_hour", data=df, palette="coolwarm")
    plt.title(f"Frecuencia de publicación por hora - {pais}")
    plt.xlabel("Hora del día")
    plt.ylabel("Cantidad de videos")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
