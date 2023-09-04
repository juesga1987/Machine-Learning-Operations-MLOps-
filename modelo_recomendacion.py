import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

modelo = pd.read_csv(r'df_modelo_recomendacion.csv') #Importamos Dataframe

tfidf_vectorizer = TfidfVectorizer() #Instanciamos metodo
tfidf_matrix = tfidf_vectorizer.fit_transform(modelo["publisher"] + " " + modelo["genres"] + " " + modelo["app_name"]) #Corremos el modelo seleccionando las variables relevantes

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix) # Ejecutamos la similitud de cosenos

