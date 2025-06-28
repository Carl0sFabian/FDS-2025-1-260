import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Rutas CSV y JSON 
file_paths = {
    "EE.UU": "data/EE.UU/USvideos_cc50_202101.csv",
    "Canadá": "data/Canadá/CAvideos_cc50_202101.csv",
    "Alemania": "data/Alemania/DEvideos_cc50_202101.csv",
    "México": "data/México/MXvideos_cc50_202101.csv",
    "Corea del Sur": "data/Korea del Surr/KRvideos_cc50_202101.csv"
}
category_json_paths = {
    "EE.UU": "data/EE.UU/US_category_id.json",
    "Canadá": "data/Canadá/CA_category_id.json",
    "Alemania": "data/Alemania/DE_category_id.json",
    "México": "data/México/MX_category_id.json",
    "Corea del Sur": "data/Korea del Surr/KR_category_id.json"
}

for pais, csv_path in file_paths.items():
    print(f"\n📊 Procesando datos de {pais}...")

    df = pd.read_csv(csv_path)

    with open(category_json_paths[pais], "r", encoding="utf-8") as f:
        cat_data = json.load(f)
        cat_map = {int(item['id']): item['snippet']['title'] for item in cat_data['items']}
    df['category_name'] = df['category_id'].map(cat_map)

    df["title_length"] = df["title"].astype(str).apply(len)
    df["desc_length"] = df["description"].astype(str).apply(len)
    df["log_views"] = np.log1p(df["views"])
    df["publish_hour"] = pd.to_datetime(df["publish_time"]).dt.hour

    # Gráfico 1: Distribución log(views)
    plt.figure(figsize=(10, 6))
    sns.histplot(df["log_views"], bins=40, kde=True)
    plt.title(f"Distribución logarítmica de vistas - {pais}")
    plt.xlabel("Views + 1)")
    plt.ylabel("Frecuencia")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Gráfico 2: Categorías más frecuentes
    top_cats = df["category_name"].value_counts().head(8)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_cats.values, y=top_cats.index, palette="flare")
    plt.title(f"Top 8 categorías más frecuentes - {pais}")
    plt.xlabel("Cantidad de videos")
    plt.ylabel("Categoría")
    plt.tight_layout()
    plt.show()

    # Gráfico 3: Longitud del título por categoría
    plt.figure(figsize=(12, 6))
    top_names = top_cats.index.tolist()
    subset = df[df["category_name"].isin(top_names)]
    sns.boxplot(data=subset, x="category_name", y="title_length", palette="Set3")
    plt.title(f"Distribución de longitud de títulos por categoría - {pais}")
    plt.ylabel("Longitud del título")
    plt.xlabel("Categoría")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Gráfico 4: Publicación por hora
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x="publish_hour", palette="coolwarm")
    plt.title(f"Frecuencia de publicación por hora - {pais}")
    plt.xlabel("Hora del día")
    plt.ylabel("Cantidad de videos")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Gráfico 5: Vistas vs. comentarios
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="views", y="comment_count", alpha=0.4)
    plt.title(f"Relación entre vistas y comentarios - {pais}")
    plt.xlabel("Vistas")
    plt.ylabel("Comentarios")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
