"""
 Web Scrapping en Mercado Libre
 * saber que producto tiene mas descuento
 * el mas barato
 * etc
    _ 

"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Los urls se basan en busqueda de ' Notebook pc' en Mercado Libre
url1 = 'https://listado.mercadolibre.com.ar/notebook-pc#D[A:%20notebook%20pc]'
url2 = 'https://listado.mercadolibre.com.ar/computacion/laptops-accesorios/notebooks/notebook-pc_Desde_51_NoIndex_True'

url3 = 'https://listado.mercadolibre.com.ar/computacion/laptops-accesorios/notebooks/notebook-pc_Desde_101_NoIndex_True'
all_url = [url1, url2, url3]
lista_precio_normal = list()
lista_precio_promo = list()
lista_titulos = list()
porcentaje_descuento = list()

for url in all_url:
    page_status = requests.get(url)
    soup = BeautifulSoup(page_status.content, 'html.parser')
    # Enfocarse en el container que tiene las informaciones sobre las compu
    publicaciones = soup.find_all('li', class_='ui-search-layout__item shops__layout-item ui-search-layout__stack')
    titulos = []
    precio_con_promo = []
    precio_normal = []
    descuentos = []
    for publicacion in publicaciones:
        titulo = publicacion.find('h2', class_='ui-search-item__title')
        p_normal = publicacion.find_all('span', class_='andes-money-amount__fraction')[0]
        promo_parent = publicacion.find('span',  class_='andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript')
        p_promo = promo_parent.find_next('span', class_='andes-money-amount__fraction')
        descuento = publicacion.find('span', class_='ui-search-price__second-line__label')
        titulos.append(titulo)
        precio_normal.append(p_normal)
        precio_con_promo.append(p_promo)
        descuentos.append(descuento)

    #compu_titulo = [(f'{titulo.text}\n {precio_nor.text}\n {precio_prom.text}\n\n') for (titulo, precio_nor, precio_prom) in zip(titulos, precio_normal, precio_con_promo)]
   
    # Crear una lista para columna
    lista_titulos += [titulo.text[0:26] for titulo in titulos]
    lista_precio_normal += [precio.text for precio in precio_normal]
    lista_precio_promo += [precio.text for precio in precio_con_promo]
    porcentaje_descuento += [descuento.text for descuento in descuentos]


    # determinar la columna con el tamaño maximo en el caso de que sus valores no coinciden
    tamaño_maximo = max(len(lista_titulos), len(lista_precio_normal), len(lista_precio_promo), len(porcentaje_descuento))

    # LLenar missing data con Nan values por ahora
    lista_titulos += [float('nan')] * (tamaño_maximo - len(lista_titulos))
    lista_precio_normal += [float('nan')] * (tamaño_maximo - len(lista_precio_normal))
    lista_precio_promo += [float('nan')] * (tamaño_maximo - len(lista_precio_promo))
    #descuento_automatico = '0% OFF'
    porcentaje_descuento += [float('nan')] * (tamaño_maximo - len(porcentaje_descuento))
    


# crear el dataframe a partir de las listas
try:
            
    df = pd.DataFrame({
        'Marca': lista_titulos,
        'precio_normal': lista_precio_normal,
        'precio_promo': lista_precio_promo,
        'Descuento': porcentaje_descuento
        })
                

    #print(df.loc[7:13])
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
except AttributeError as ae:
    print("Error con el html del soup:", ae)
            
# Ya tenemos el dataframe, convertiremos cada data a su respectivo tipo de data
# Por el hecho de que los datos de los precios vienen con puntos, el programa los considera como posible float por lo cual vamos a reemplazar cada punto con =nada=  asi podamos convertir esta columna en enteros
df['precio_normal'] = df['precio_normal'].str.replace('.', '')
df['precio_normal'] = df['precio_normal'].astype(int)

df['precio_promo'] = df['precio_promo'].str.replace('.', '').astype(int)


# POV : volveremos a incluir la columna descuento cuando haya mas consistencia con estos datos, por ahora podemos inferir que si hay una diferencia de precio entre el precio normal y el pprecio promo entonces hay una promo
def main():
    articulos_con_promo = df[df['precio_normal'] > df['precio_promo']] # ya tenemos las compu con deescuento
    # obtener el iindex de compu mas baratin y mas caro
    sns.catplot(data=articulos_con_promo, kind='bar', x=df.Descuento, y=df.precio_promo, estimator='mean', errorbar=None)
    plt.title('Compus con descuento')
    plt.xlabel('Descuento')
    plt.ylabel('Precio con promo')
   
    plt.show()
    index_mas_barato = df['precio_promo'].idxmin()
    compu_mas_barato = df.loc[index_mas_barato]
    #index_mas_caro = df['precio_promo'].max() # retorna la cifra mas grande de la columna precio promo
    index_mas_caro = df['precio_promo'].idxmax()
    compu_mas_caro = df.loc[index_mas_caro]
    print(compu_mas_caro)
    


if __name__ == '__main__':
    main()