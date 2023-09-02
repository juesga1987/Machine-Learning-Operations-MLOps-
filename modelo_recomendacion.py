import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

modelo = pd.read_csv(r'games_modelo.csv')

modelo["publisher"].fillna("", inplace=True)
modelo["genres"].fillna("", inplace=True)
modelo["app_name"].fillna("", inplace=True)

tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(modelo["publisher"] + " " + modelo["genres"] + " " + modelo["app_name"])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)