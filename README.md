<div style="width: 100%; clear: both;">
<div style="float: left; width: 50%;">
<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ45DITH77up1n8tb7Bx2n7TO8tBq4I65ZIuw&s", align="left">
</div>
<div style="float: right; width: 50%;">
<p style="margin: 0; padding-top: 22px; text-align:right;">1ACC0216-2510-260 - Fundamentos de Data Science · Trabajo Final</p>
<p style="margin: 0; text-align:right;">2025 · Proyecto de Ciencia de Datos: Trending YouTube Video Statistics</p> 
<p style="margin: 0; text-align:right;">Prof: <b>Fernandez Vasquez Richard Fernando</b></p>
<p style="margin: 0; text-align:right; padding-button: 100px;">Integrante 1: <b>Carlos Fabian Mendoza Quispe </b> - <a href="">U20231C416@upc.edu.pe</a></p>
<p style="margin: 0; text-align:right; padding-button: 100px;">Integrante 2: <b>Elias David Moncada Olivares </b> - <a href="">U202315959@upc.edu.pe</a></p>
</div>
</div>
<div style="width:100%;">&nbsp;</div>
<center><h1>📙 Introducción</h1></center>
En la era digital actual, el volumen de información generado a través de plataformas en línea como YouTube ha crecido de manera exponencial, convirtiéndose en una fuente rica y valiosa de datos. Las organizaciones buscan aprovechar este flujo constante de información para entender mejor el comportamiento de los usuarios, identificar patrones de consumo y tomar decisiones estratégicas basadas en evidencia. En este contexto, la Ciencia de Datos se posiciona como una disciplina clave para transformar datos en conocimiento útil y accesible.
El presente proyecto de Ciencia de Datos tiene como objetivo analizar las tendencias de videos de YouTube en diferentes países con el propósito de generar insights que ayuden a una empresa de marketing digital a comprender qué tipos de contenidos captan mayor atención, cuáles son mejor valorados por los usuarios, y cómo varían estas tendencias en el tiempo y en el espacio geográfico.
El alcance del proyecto abarca el tratamiento, exploración, modelado y análisis de un conjunto de datos compuesto por estadísticas diarias de videos en tendencia en YouTube, segmentados por país, categoría y otras variables relevantes. A través de la aplicación de la metodología CRISP-DM, se pretende extraer conocimiento significativo que permita, entre otras cosas, identificar las categorías más populares, evaluar el desempeño de los canales, analizar el comportamiento de los usuarios según la ubicación geográfica, y explorar la posibilidad de predecir métricas clave como vistas, likes y dislikes.
En suma, este proyecto busca demostrar cómo un enfoque estructurado y metodológico puede convertir grandes volúmenes de datos en una fuente poderosa de información estratégica, permitiendo a las organizaciones adaptarse y responder con mayor eficacia a las dinámicas del entorno digital.

<div style="width:100%;">&nbsp;</div>
<center><h1>👥 Integrantes y Roles</h1></center>
Los roles que participan para el desarrollo del proyecto son los siguientes:

<table>
  <thead>
    <tr>
      <th scope="col">Rol</th>
      <th scope="col">Responsabilidad Clave</th>
      <th scope="col">Fase CRISP-DM</th>
      <th scope="col">Integrante</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Business Project Sponsor</td>
      <td>Define el valor de negocio, criterios de éxito y prioriza requerimientos</td>
      <td>Comprensión del negocio y Evaluación</td>
      <td>Elías Moncada Olivares</td>
    </tr>
    <tr>
      <td>Data Engineer</td>
      <td>Ingesta, limpieza y orquestación de los datos; crea pipelines reproducibles</td>
      <td>Comprensión / Preparación de datos</td>
      <td>Carlos Mendoza Quispe</td>
    </tr>
    <tr>
      <td>Data Scientist</td>
      <td>Feature engineering, selección de modelos, entrenamiento y validación</td>
      <td>Modelado y Evaluación</td>
      <td>Carlos Mendoza Quispe</td>
    </tr>
    <tr>
      <td>Data Analyst</td>
      <td>Análisis exploratorio, visualizaciones y comunicación de insights</td>
      <td>Comprensión / Preparación de datos y Conclusiones</td>
      <td>Elías Moncada Olivares</td>
    </tr>
  </tbody>
</table>

<center><h1>📁 Descripción del Conjunto de Datos</h1></center>
El dataset utilizado proviene de una versión modificada del conocido conjunto de datos Trending YouTube Video Statistics de Kaggle. Para este trabajo se utilizaron específicamente los archivos correspondientes a Estados Unidos:

- `USvideos_cc50_202101.csv`: contiene registros diarios de videos en tendencia. Incluye campos como ID, título, canal, categoría, vistas, likes, dislikes, comentarios, fecha, entre otros. Se añadieron columnas como estado, latitud, longitud y geometría.
- `US_category_id.json`: mapea los ID de categorías con sus respectivos nombres (ej. "Music", "Gaming", etc.).

A continuación se detallan las columnas del archivo CSV:

| Columna               | Tipo de Dato | Descripción                                                   |
|------------------------|--------------|---------------------------------------------------------------|
| video_id              | Categórico   | Identificador único del video                                 |
| trending_date         | Fecha        | Fecha en que el video estuvo en tendencia                     |
| title                 | Categórico   | Título del video                                              |
| channel_title         | Categórico   | Nombre del canal                                              |
| category_id           | Categórico   | ID de la categoría del video                                  |
| publish_time          | Fecha        | Fecha y hora de publicación del video                         |
| tags                  | Categórico   | Etiquetas asociadas al video                                  |
| views                 | Entero       | Número de visualizaciones                                     |
| likes                 | Entero       | Número de "me gusta"                                          |
| dislikes              | Entero       | Número de "no me gusta"                                       |
| comment_count         | Entero       | Número de comentarios                                         |
| thumbnail_link        | Categórico   | URL de la miniatura                                           |
| comments_disabled     | Booleano     | Si los comentarios están deshabilitados                      |
| ratings_disabled      | Booleano     | Si los ratings están deshabilitados                          |
| video_error_or_removed| Booleano     | Si el video tiene errores o ha sido eliminado                 |
| description           | Categórico   | Descripción textual del video                                 |
| state                 | Categórico   | Estado/región asignado aleatoriamente                         |
| lat                   | Numérico     | Latitud geográfica                                            |
| lon                   | Numérico     | Longitud geográfica                                           |
| geometry              | Geoespacial  | Coordenadas geográficas en formato WKT                        |

El dataset incluye 20 columnas, algunas de las cuales fueron limpiadas, transformadas (logarítmicamente) y enriquecidas para mejorar la calidad del análisis. Se aplicaron técnicas como imputación de datos nulos, detección y creación de nuevas variables.

<center><h1>✅ Conclusiones </h1></center
Durante el desarrollo del análisis se extrajeron hallazgos clave para el negocio:
- Predominio de categorías como "Entertainment", "Music" y "Howto & Style", lo que evidencia una clara orientación de los usuarios hacia contenidos emocionales, virales o visualmente atractivos.
- Los altos niveles de "likes" promedio y ratios de aprobación muestran qué temáticas conectan más con la audiencia y cómo se genera engagement positivo.
- Canales como ESPN dominan en número de apariciones en tendencia, lo que refleja buenas prácticas de publicación, fidelidad de la audiencia y timing estratégico.
- Picos temporales en febrero 2018 revelan eventos virales o lanzamientos de alto impacto, lo cual refuerza la necesidad de monitoreo continuo del entorno.
- Mapas de calor y correlaciones permitieron observar concentraciones geográficas y relaciones fuertes entre métricas (likes, comentarios, vistas), esenciales para campañas segmentadas.
                                  
<center><h1>📄 Licencia de Uso</h1></center>
Este trabajo se ha realizado de manera estrictamente académica para el curso Fundamentos de Data Science de la Universidad Peruana de Ciencias Aplicadas (UPC).

- La fuente de datos original es un conjunto descargado de Kaggle, modificado únicamente con fines didácticos.
- Queda terminantemente prohibido su uso con objetivos comerciales.
- Todas las visualizaciones, análisis y modelos aquí presentados constituyen un ejercicio formativo y no deben interpretarse como un producto de mercado.
