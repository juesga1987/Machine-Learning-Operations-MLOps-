import pandas as pd
import numpy as np
from datetime import date, datetime as dt
from fastapi import FastAPI



app = FastAPI()

#http://127.0.0.1:8000 url
#http://127.0.0.1:8000/docs


@app.get('/userdata/{User_id}')
def userdata(User_id:str):
    # Importamos las Dataframes con que se trabajara
    df_usu_games = pd.read_csv(r'df_games_userid.csv')
    items_usu_games = pd.read_csv(r'df_items_user_sample.csv')
    reviews_usu_games = pd.read_csv(r'df_reviews_userid.csv')
    #Definimos el fildto de la funcion con la variable de entrada
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


    juegos_totales = items_usu_games.loc[items_usu_games['user_id'] == User_id, 'items_count'].tolist()[0] # Ubicamos por User_id y llevamos a una lista
    recomendaciones_f = reviews_usu_games[reviews_usu_games['user_id'] == User_id]['recommend'].tolist() # Hacemos lo mismo con recomendaciones
    recomendations = sum(recomendaciones_f) # Sumamos la cantidad de recomendados por usuario

    recomend = round((recomendations/juegos_totales)*100,2) #Sacamos el % que nos pide la funcion

    diccionario = { 'Gasto': suma,
                   'Recomendacion' : f"{recomend:.2f}%"}

    return diccionario
        
@app.get('/countreviews/{fecha_inicial},{fecha_final}')
def countreviews(fecha_inicial:str,fecha_final:str):
    reviews_countreviews = pd.read_csv(r'df_reviews_countreviews.csv') #Importamos dataframe
    lista_fechas = [] 
    lista_usuarios_unico = []
    inicial = dt.strptime(fecha_inicial, '%Y-%m-%d').date() #Cambiamos formado de dato de entrada 
    final = dt.strptime(fecha_final, '%Y-%m-%d').date() #Cambiamos formado de dato de entrada 

    # Sacamos las fechas de posteo a traves de un loop y las ingestamos en lista. Ademas sacamos la lista de user_id garantizando la no duplicidad
    for ind, elemento in enumerate(reviews_countreviews['posted']):
        elemento_fecha = dt.strptime(elemento, '%Y-%m-%d').date() 
        if inicial <= elemento_fecha <= final:
            lista_fechas.append(elemento_fecha)
            a = reviews_countreviews['user_id'][ind]
            if a not in lista_usuarios_unico:
                lista_usuarios_unico.append(a)

    cuenta_usuarios = len(lista_usuarios_unico) #Contamos el numero de usuarios

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
    merged = pd.read_csv(r'merged_genres.csv') #Abro el dataframe
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


    diccionario = { 'Genero': condicion,
                   'Ranking': ranking
    }
    return diccionario

@app.get('/userforgenre/{genero}')
def userforgenre(genero:str):
    games_gen2 = pd.read_csv(r'df_games_userforgente.csv') #Importamos DataFrame
    items = pd.read_csv(r'df_items_userforgenre.csv') #Importamos DataFrame
    #games_gen2['id'] = games_gen2['id'].astype(str)
    generos = items.merge(games_gen2, left_on='item_id', right_on='id') #Hacemos merge basado en item_id y id
    generos = generos[generos['genres'] == genero] #filtramos por la variable de entrada
    user_time = generos.groupby('user_id')['playtime_forever'].sum() #hacemos un groupby por user y playtime forever que nos sirve como acumulador por usuario
    usuarios_top = user_time.sort_values(ascending=False).head(5) #Organizamos los usuarios por tiempo jugado
    ranking = []
    # Recorremos, identificamos indice de usuario y luego agrupamos
    for user_id, horas in usuarios_top.items():
        usuario = items[items['user_id'] == user_id].iloc[0]
        ranking.append([usuario['user_id'], f"http://steamcommunity.com/id/{usuario['user_id']}",horas/60])
    return {'Resulado': ranking}

@app.get('/developer/{desarrollador}')
def developer(desarrollador: str ):
    games_dev = pd.read_csv(r'df_games_developer.csv') #Importamos DataFrame
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
    merged = pd.read_csv(r'merged_recomendacion.csv') # Abrimos dataframe preparado para la funcion
    merged['release_date_anio'] = merged['release_date_anio'].astype(int) #Cambiamos el datatipo del anio a int


    year = int(year)
    df_sa = merged.copy() #Creamos copia de dataframe merge
    df_sa['anio'] = df_sa['release_date_anio'] #cambiamos el nombre de la columna a anio creando una nueva
    anio_data = df_sa[df_sa['anio'] == year] # filtramos por variable de entrada
    mapeo = {0: 'Negative', 1: 'Neutral', 2: 'Positive'} #Mapeamos los sentimientos
    sentiment = anio_data['sentiment'].map(mapeo).value_counts().to_dict() #Realizamos la suma por mapeo y llevamos a diccionario
    return sentiment


# Modelo de recomendacion

# Funcion
@app.get('/recomendacion_juego/{id}')
def recomendacion_juego(id:int):
    from modelo_recomendacion import cosine_sim, modelo     
    #modelo = pd.read_csv(r'df_modelo_recomendacion.csv') # leemos dataframe del archivo
    item_indice = modelo[modelo["id"] == id].index[0] # Obtenemos el índice del item input en nuestro DataFrame
    items_similares = list(enumerate(cosine_sim[item_indice])) # Generamos lista con los items similares que devolvió el modelo
    similar_items_organizados = sorted(items_similares, key=lambda x: x[1], reverse=True) # Organizamos los items del punto anterior
    indices = [index for index, _ in similar_items_organizados[1:10]] # Recorremos los ítems para traer las 5 recomendaciones

    items_recomendados = modelo.iloc[indices]["id"].tolist()

    # Obtengo los nombres de los ítems recomendados para el retorno de la función, no permito repetidos y limito a 5 el tamaño de la lista
    lista_nombres = [modelo[modelo['id'] == elemento]['app_name'].iloc[0] for elemento in items_recomendados if elemento != id]
    lista_nombres = lista_nombres[:5]

    diccionario = {f'Juego {i+1}': nombre for i, nombre in enumerate(lista_nombres)}

    return diccionario



