![Logo de Steam](https://prod.assets.earlygamecdn.com/images/Steam.jpg?transform=article3x_webp&x=0.5&y=0.5)

# Proyecto de MLOps Engineer aplicado a plataforma gaming Steam
## Juan Esteban García.
## Email: juanestebangarciarodriguez@gmail.com
## Usuario GitHub: juesga1987

# Introducción

### En este proyecto, asumí el rol de un MLOps Engineer en Steam, una plataforma multinacional de videojuegos, para este caso en particular analizamos la información provista por la empresa para Australia en las siguientes bases de datos:

1.	Steam Games: Base datos de los juegos que contiene información relevante como desarrolladores, nombre de los títulos, precio, genero, año de lanzamiento entre otras.
2.	Reviews: Se trata de un dataset con las recomendaciones y reviews detalladas por usuario de los juegos con los que interactuaron, en este encontramos datos como el user id, recomendación, review detallado, fecha de posteo del review, juego calificado.
3.	Items: Nos provee con gran especificidad de los usuarios, su tiempo de juego, su id en la plataforma e id del usuario.
   
### El objetivo de este proyecto en términos generales es utilizar las bases de datos provistas y realizar el respectivo proceso de extracción, transformación y carga (ETL) garantizando el despliegue de una API funcional usando la librería FastApi y Render (Sistema en la nube de construcción y ejecución de apps) donde se alojarán consultas especificas realizadas a través de funciones además de los resultados del sistema de recomendación. 
### Este es un caso donde partiendo de cero buscamos seguir el ciclo de vida de un proyecto de Machine Learning hasta el deployment final de los resultados.

# Descripción del Problema

## Contexto

### A pesar de que nuestra empresa Steam ha obtenido buenos resultados previamente aun careciendo de un análisis exhaustivo de la información que ha recopilado como resultado de la interacción de los usuarios con la plataforma, la empresa busca ahora tomar ventaja de las tecnologías actuales para entender mucho mejor las relaciones entre los juegos que ofrece, sus usuarios y las características de los mismos, además del desarrollo de un sistema de recomendación que permita que la interacción con la plataforma sea mucho más certera y de esta forma capturar un mayor número de clientes y lograr la fidelización de los actuales.
### Como especialistas en datos contamos con datos de bajo de calidad que requieren de data engineering para que sean útiles y agreguen valor. 

# Resumen del trabajo y sus etapas

## ETL

### Leer los datasets proporcionados en el formato correcto realizando las eliminaciones de columnas innecesarias para optimizar el rendimiento de la API y el entrenamiento del modelo, Esta etapa es fundamental pues era necesario interactuar con datasets que contenían columnas anidadas en listas de diccionarios, emoticones e imágenes como códigos escritos de tipo alfanumericos con caracteres especiales, espacios nulos, fechas en formatos no compatibles y columnas de % de calificación con texto. 
### Posterior a lo anterior y dado el tamaño de algunos de los DataFrames resultantes decidí crear archivos fraccionados según la necesidad de cada función y el modelo, esta es una decisión fundamental, pues, aunque sacrifica algo de veracidad asegura que el deployment se ejecute sin inconvenientes. Dado que la memoria de procesamiento de Render es únicamente de 500mb, para algunas de las funciones se prefirió seleccionar una muestra de los datasets pues a pesar de haber creado archivos con la información estrictamente necesaria para cada función algunas de ellas necesitaban menor costo computacional. En mi caso dichas funciones fueron: UserData, UserForGenre y el modelo de recomendación.
## Análisis de sentimientos
### Con base en los reviews de cada uno de los usuarios que se encontraban en el DataFrame reviews se procedió a transformar caracteres especiales que afectaban el rendimiento del modelo.
### A partir de allí se usó la librería de procesamiento de lenguaje natural NLTK para la tokenización por palabras. Hecho esto se uso la librería VaderSentiment y el método SentimentIntensityAnalyzer, aquí hay una observación importante, en lugar de tomar los resultantes en términos positivos, negativos y neutrales como lo permite el método, usamos el resultado compound que rastrea matemáticamente con base en un ponderado el tipo de sentimiento del usuario, si el resultado es mayor a 0 se considera que la calificación fue positiva y menor a 0 negativa. Se hizo de esta forma pues era necesario que los sentimientos de carácter neutral o indeterminado incluyeran únicamente aquellos reviews que estaban vacíos. De esta forma nuestro resultado final se compone de numero de sentimientos positivos, negativos y neutrales solo aquellos sin reviews.
### Posteriormente se creó una columna llamada “sentiment”.
## Desarrollo de la API
### Dadas las necidades de la organización, se desarrollo una API que disponibilizara los datos con base en funciones consideradas estrategicas para evaluar las conclusiones del trabajo realizado. Para ello se utilizo el framework FastApi y render como plataforma host para la construccion y deployment. Como se menciono anteriormente la capacidad de procesamiento limitada a 500mb de Ram fue todo un desafio.

### Las funciones creadas fueron:
•	userdata(User_id: str): Devuelve la cantidad de dinero gastado por el usuario, el porcentaje de recomendación en base a la columna recommend y la cantidad de items. Para permitir el deployment se uso una muestra del dataframe items.

•	countreviews(start_date: str, end_date: str): Cantidad de usuarios que realizaron reviews entre las fechas dadas y el porcentaje de recomendación de estos en base a recommend.

•	genre(genre: str): Puesto en el que se encuentra un género en el ranking de PlayTimeForever.

•	userforgenre(genre: str): Top 5 de usuarios con más horas de juego en el género dado, con su URL y user_id. En este caso tambien se uso una muestra de items para permitir el deployment.

•	developer(developer: str): Cantidad de items y el porcentaje de contenido gratuito por año según la empresa desarrolladora.
•	sentiment_analysis(year: int): Lista con la cantidad de registros de reseñas de usuarios categorizados con un análisis de sentimiento según el año de lanzamiento.
## Análisis Exploratorio de los Datos Modelo de recomendacion (EDA)
### Se realizo un EDA de los datos del dataframe games pues de alli se extrajeron los datos  para el desarrollo de modelo de recomendación como era solicitado por la empresa, vale la pena aclarar que el archivo usado para el modelo de recomendación es simplement un dataframe con la información justamente necesario para ejecutarlo de acuerdo a a las variables identificadas como mas relevantes.
### Se analizaron las variables mas relevantes del dataset con base en el modelo de recomendación item a item o juego a juego. Con base en el EDA se determino que el mismo debia ser realizado con el desarrollador y el genero pues determinaban en mayor medida la selección de un juego en particular.
### El EDA se realizo de forma grafica mayoritariamente pues definitivamente hace los datos mas amenos y faciles de entender para el usuario final de la informacion, se usaron:
-	Barras.
-	Barras compiladas.
-	Boxplot.
-	Tortas.
## Modelo ML de recomendacion
### Después de preparar los datos y realizar el EDA, entrenamos el modelo de recomendación basado en la similaridad del coseno que es una medida de similitud entre dos vectores que como producto arroja la relacion entre los mismos en referencia a una variable dada, como lo mencionamos anteriormente en mi caso, se determino que un juego (item) estaba intimamente ligado al genero y el desarrollador. 
### La librería Scikit-Learn proporciona los metodos para la creacion de la matriz o vectores (TfidVectorizer) y el metodo de coseno de similaridad (cosine_similarity). En este paso y dadas las limitaciones de procesamiento de nuestro host Render se tomo una muetra del 12% original del DataSet, que permite hacer el deploy y generar la matriz de resultados. Esta es la minima muestra que asegura un resultado de recomendación.
### Adicionalmente fue necesario eliminar algunos generos cuya importancia en la muestra y cantidad de juegos no era relevante, esto con fines el deployment.
### Finalmente a traves de una función que considerara no arrojar como recomendación el mismo item (Juego) introducido como variable de entrada y la no repeticion de recomendaciones se obtienen los 5 items mejor valorados recomendados.





