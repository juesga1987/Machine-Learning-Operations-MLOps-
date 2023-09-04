import pandas as pd
import numpy as np
from datetime import date, datetime as dt
from pydantic import BaseModel # Garantiza que los tipo de datos coincidan con los que definimos en nuestra clase
from fastapi import FastAPI
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from fastapi.responses import HTMLResponse

app = FastAPI()

#http://127.0.0.1:8000 url
#http://127.0.0.1:8000/docs


@app.get('/userdata/{User_id}')
def userdata(User_id:str):
    df_usu_games = pd.read_csv(r'df_games_userid.csv')
    items_usu_games = pd.read_csv(r'df_items_user_sample.csv')
    reviews_usu_games = pd.read_csv(r'df_reviews_userid.csv')
    
    games_usu = items_usu_games[items_usu_games['user_id'] == User_id]['item_id'] # Se lista la cantidad de juegos por usuario
    games_usu = games_usu.tolist() # Se crea una lista para recorrer con los id de los juegos filtrados por usuario

    # funcion para sumar el gasto

    prices = []
    for elemento in games_usu:
        if df_usu_games[df_usu_games['id'] == (elemento)]['price'].to_list() == []:
            pass
        else:
            prices.append(df_usu_games[df_usu_games['id'] == (elemento)]['price'].to_list()[0])

    suma = sum(prices)


    juegos_totales = items_usu_games.loc[items_usu_games['user_id'] == User_id, 'items_count'].tolist()[0]
    recomendaciones_f = reviews_usu_games[reviews_usu_games['user_id'] == User_id]['recommend'].tolist()
    recomendations = sum(recomendaciones_f)

    recomend = round((recomendations/juegos_totales)*100,2)


    return {f'gasto : {suma}', f'% recomendacion : {recomend}'}
            
@app.get('/countreviews/{fecha_inicial},{fecha_final}')
def countreviews(fecha_inicial:str,fecha_final:str):
    reviews_countreviews = pd.read_csv(r'reviews.csv')
    lista_fechas = []
    lista_usuarios_unico = []
    inicial = dt.strptime(fecha_inicial, '%Y-%m-%d').date()
    final = dt.strptime(fecha_final, '%Y-%m-%d').date()

    for ind, elemento in enumerate(reviews_countreviews['posted']):
        elemento_fecha = dt.strptime(elemento, '%Y-%m-%d').date() 
        if inicial <= elemento_fecha <= final:
            lista_fechas.append(elemento_fecha)
            a = reviews_countreviews['user_id'][ind]
            if a not in lista_usuarios_unico:
                lista_usuarios_unico.append(a)

    cuenta_usuarios = len(lista_usuarios_unico)

# Hago nuevamente el codigo pero sin considererar si el usuario ya estaba en la lista, esto permite saber cuantas veces hizo reviews en total
    lista_usuarios = []
    lista_fila = []
    numero_fila = 0
    for ind, elemento in enumerate(reviews_countreviews['posted']):
        elemento_fecha = dt.strptime(elemento, '%Y-%m-%d').date() 
        if inicial <= elemento_fecha <= final:
            a = reviews_countreviews['user_id'][ind] # Indica el user id dentro del rango de fechas
            lista_usuarios.append(a) # Lista para guardar los Id's y posteriormente saber cuantos usuarios hay (Dado que el numero de usuarios es igual al de recomendaciones se usa como denominaror)
            numero_fila = ind
            lista_fila.append(numero_fila) # Esta lista de filas se usa posteriormente para saber cuantas recomendaciones fueron positivas
    
    b = 0
    for elemento in lista_fila:
        if reviews_countreviews['recommend'][elemento] == True:
            b += 1 # Numero de recomendaciones positivas

    recomendacion = round(b/len(lista_fila)*100,2)
    
    return {'Usuarios_rango' : cuenta_usuarios, 
            'recomendacion %' : f"{recomendacion:.2f}%"
            }

@app.get('/genre/{genero}')
def genre(genero:str):
    games_gen = pd.read_csv(r'games.csv')
    items = pd.read_csv(r'items_genre.csv')
    games_gen.drop_duplicates(subset=['id'], inplace=True) # Elimina los juegos repetidos, para al hacer match entre ambos datasets no duplicar
    #games_gen['id'] = games_gen['id'].astype(str)
    pd.set_option('display.float_format', '{:.2f}'.format) # Seteo para permitir mostrar numeros muy grandes
    df_game_time = items[['item_id','playtime_forever']] # Solo trae estas dos columnas que son las necesarias para el codigo.
    df_agrupado = df_game_time.groupby('item_id')['playtime_forever'].sum() # agrupa por juego el total jugado.
    merged = pd.merge(games_gen, df_agrupado, left_on='id', right_on='item_id', how='left') # Hago el merge
    merged.dropna(subset=['playtime_forever'], inplace=True) # Hago un drop en la columna playtime_forever
    # lista de generos
    generos = merged['genres'].unique()
    # defino funcion para calcular el total jugado por genero
    listacalc = []
    def tiempo_genero(lista):
        listacalc = []
        for elemento in lista:
            calculo = merged.loc[merged['genres'] == str(elemento), 'playtime_forever'].sum()
            listacalc.append(calculo)
        return listacalc
    a = tiempo_genero(generos)
    # creo un dataframe con las dos listas generadas
    datos = {
        'generos' : generos,
        'tiempo_juego': a
         }
    df = pd.DataFrame(datos)
    # Creo una columna con el ranking
    df['ranking'] = df['tiempo_juego'].rank(ascending=False)

    condicion = str(genero)
    ranking = df.loc[df['generos'] == str(genero), 'ranking'].values[0]
    resultado = {f'Genero : {condicion}', f'Ranking: {ranking}'}
    return resultado

@app.get('/userforgenre/{genero}')
def userforgenre(genero:str):
    games_gen2 = pd.read_csv(r'df_games_userforgente.csv')
    items = pd.read_csv(r'df_items_userforgenre.csv')
    #games_gen2['id'] = games_gen2['id'].astype(str)
    generos = items.merge(games_gen2, left_on='item_id', right_on='id')
    generos = generos[generos['genres'] == genero]
    user_time = generos.groupby('user_id')['playtime_forever'].sum()
    usuarios_top = user_time.sort_values(ascending=False).head(5)
    ranking = []
    for user_id, horas in usuarios_top.items():
        usuario = items[items['user_id'] == user_id].iloc[0]
        ranking.append([usuario['user_id'], f"http://steamcommunity.com/id/{usuario['user_id']}",horas/60])
    return f'Resultado: {ranking}'

@app.get('/developer/{desarrollador}')
def developer(desarrollador: str ):
    games_dev = pd.read_csv(r'df_games_developer.csv')
    pd.set_option('display.float_format', '{:.2f}'.format) # Seteo para permitir mostrar numeros muy grandes

# columna free not free para luego sacar el % con base en la cantidad de juegos (items) por desarrollador, no se hace con item count pues este se refiere a los items por usuario y no por desarrollador
    games_dev['free_notfree'] = np.where(games_dev['price'] == 0,  True,  False)
# Filtro para aplicar la funcion cuando se de el developer
    developerdf = games_dev.loc[games_dev['developer'] == str(desarrollador)]
# conteo de cantidades de juegos(items) y free items por desarrollados

    cantidad_juegos_anio = developerdf.groupby('release_date_anio')['id'].count().reset_index()
    cantidad_juegos_anio.rename(columns={'id': 'cantidad_items'}, inplace=True)
# Conteo de la cantidad de juegos gratuitos (items) por año
    cantidad_free_anio = developerdf[developerdf['free_notfree']].groupby('release_date_anio')['free_notfree'].count().reset_index()
    cantidad_free_anio.rename(columns={'free_notfree': 'cantidad_free'}, inplace=True)
# Combino los resultados
    resultado_final = pd.merge(cantidad_juegos_anio, cantidad_free_anio, on='release_date_anio', how='outer')
# Rellenar valores NaN con 0 en la columna 'cantidad_free'
    resultado_final['cantidad_free'].fillna(0, inplace=True)
# Calcular el porcentaje de juegos gratuitos (items) por año
    resultado_final['porcentaje_free'] = (resultado_final['cantidad_free'] / resultado_final['cantidad_items']) * 100
# Formatear la columna 'porcentaje_free' con el símbolo de porcentaje (%)
    resultado_final['porcentaje_free'] = resultado_final['porcentaje_free'].apply(lambda x: f"{x:.2f}%")
    resultado_final['release_date_anio'] = resultado_final['release_date_anio'].apply(lambda x: f"{x:.0f}")
# Dejo solo las columnas para el return
    df_final = resultado_final[['release_date_anio','porcentaje_free']]


    diccionario = {
        'Desarrollador': desarrollador,
        'Tabla': df_final[['release_date_anio','porcentaje_free']]
    }
    return diccionario


@app.get('/sentiment_analysis/{year}')
def sentiment_analysis(year: int):
    games_sa = pd.read_csv(r'games.csv')
    recomendacion_sa = pd.read_csv(r'recomendacion.csv')
    merged = pd.merge(recomendacion_sa, games_sa, left_on='item_id', right_on='id', how='left')
    merged = merged.drop(columns=['publisher','genres','app_name','title','url','reviews_url','price','early_access','id','developer'])
    merged.dropna(subset=['release_date_anio'], inplace=True)
    merged['release_date_anio'] = merged['release_date_anio'].astype(int)


    year = int(year)
    df_sa = merged.copy()
    df_sa['anio'] = df_sa['release_date_anio']
    anio_data = df_sa[df_sa['anio'] == year]
    mapeo = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    sentiment = anio_data['sentiment'].map(mapeo).value_counts().to_dict()
    return sentiment


# Modelo de recomendacion

@app.get('/recomendacion_juego/{id}')
def recomendacion_juego(id:int):
    from modelo_recomendacion import cosine_sim
    modelo = pd.read_csv(r'df_modelo_recomendacion.csv')
    item_indice = modelo[modelo["id"] == id].index[0] # Obtenemos el indice del item input en nuestro DataFrame
    items_similares = list(enumerate(cosine_sim[item_indice])) # Generamos lista con los items similares que devolvio el modelo
    similar_items_organizados = sorted(items_similares, key=lambda x: x[1], reverse=True) # Organizamos los items del punto anterior
    indices = [index for index, _ in similar_items_organizados[1:15]] # recorremos los itema para traer las 5 recomendaciones

    items_recomendados = modelo.iloc[indices]["id"].tolist()


    # obtengo los nombre de los items recomendados para el return de la funcion, ademas no permito repetido y limito a 5 el tamanio de la lista
    lista_nombres =[]
    for elemento in items_recomendados:
        if elemento != id:
            nombre = (modelo[modelo['id'] == elemento]['app_name'].iloc[0])
            if nombre not in lista_nombres:
                if len(lista_nombres) <= 4:
                    lista_nombres.append(nombre)
    
    a = lista_nombres[0]
    b = lista_nombres[1]
    c = lista_nombres[2]
    d = lista_nombres[3]
    e = lista_nombres[4]
                

    return {'a' : a, 'b': b, 'c': c, 'd': d, 'e': e}


