import requests
import re
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup

from models import get_postgres_uri
from models import Movie
from reporter import CSVReport

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        get_postgres_uri(),
        isolation_level="REPEATABLE READ",
    )
)
session = DEFAULT_SESSION_FACTORY()

# DESIGN PATTERN - Singleton - Al convertir movie_fetcher en una
# clase, obtenemos las ventajas de crear una sola instancia para
# el objeto de movie_fetcher, y que de esta manera se evite descargar
# y extraer la información cada vez que se una un nuevo cliente, solo si
# este objeto estuviera del server-side y ciertas funcionas las pueda controlar
# solo los administradores, como updateMovies(). Por ser un proyecto chico,
# el client realiza todo como admin. 

# La segunda ventaja es que podemos acceder al objeto en cualquier
# parte del programa sin preocupación de que sus variables sean
# sobreescritas por cualquiera. Al principio pensé que hacerlo objeto sacrificaría mucho
# espacio por tener que descargar la lista y crearla para cada cliente,
# pero no estoy seguro si sea correcto el proceso de guardar su instancia una sola vez en la DB
# y que de ella se alimenten los servicios del servidor con gets y sets.

#       Me imagino el sistema como si el objeto con la lista de las 250 peliculas estuviera
#       metido en la DB de Flix después de inicializarlo un día. Cada 6 horas un admin de
#       la empresa ejecuta el método "updateMovies()" para descargar y actualizar a la lista
#       (sus ratings más que nada). El objeto actualiza sus variables y los usuarios pueden
#       acceder a ellas sin tener que descargar o redescargar la lista de IMDB. Igualmente,
#       la usarían al momento de mandar a llamar "retrieveRecommendations(user)" que filtre
#       los filmes utilizando la preference_key del usuario para regresar una lista. Igualmente, 
#       "retrieveRecommendations(user, ascending)" (DECORATOR DESIGN PATTERN?) para regresarla 
#       en cierto orden, o crear otra función adicional "sort(list, asc/desc)"  que regrese 
#       la misma lista que recibe, pero ordenada de cierta forma.

# La CSV se usa como el registro de las variables, y la instancia como su propia
# sesión con restricciones. Existe una clase Movie en Models que realiza lo mismo.
# Tal vez mi plan fue inútil. Igual creo que no es un singleton porque no tiene métodos
# estáticos o una "lazy initiation".
class movie_fetcher:
    def scrapMovies():
        # Downloading imdb top 250 movie's data
        # Si convirtiéramos este método en su propio objeto (COMMAND PATTERN), podríamos
        # añadirles funciones extra tal vez, como guardar fechas de ejecución o filtrar
        # películas para adultos si el usuario no tuviese la edad.
        url = 'http://www.imdb.com/chart/top'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    def storeMovies(self, soup):
        # Extracting movies' details
        movies = soup.select('td.titleColumn')
        links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
        crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
        ratings = [b.attrs.get('data-value') for b in soup.select('td.posterColumn span[name=ir]')]
        votes = [b.attrs.get('data-value') for b in soup.select('td.ratingColumn strong')]

        # Create a empty list for storing
        # movie information
        list = []

        # Iterating over movies to extract
        # each movie's details
        for index in range(0, len(movies)):
            # Separating movie into: 'place',
            # 'title', 'year'
            movie_string = movies[index].get_text()
            movie = (' '.join(movie_string.split()).replace('.', ''))
            movie_title = movie[len(str(index)) + 1:-7]
            year = re.search('\((.*?)\)', movie_string).group(1)
            place = movie[:len(str(index)) - (len(movie))]

            data = {"movie_title": movie_title,
                    "year": year,
                    "place": place,
                    "star_cast": crew[index],
                    "rating": ratings[index],
                    "vote": votes[index],
                    "link": links[index],
                    "preference_key": index % 4 + 1}
            list.append(data)
        return list

    def updateMovies(self):
        # Downloading, extracting and storing imdb top 250 movie's data
        # DESIGN PATTERN: Builder Pattern - El proceso de scrapeo tiene muchos pasos seguidos, probablemente sea mejor dividirlos
        # en acciones estilo "scrapMovies(), storeMovies()" para que el desarrollador, al momento de leer el código, pueda
        # enfocarse más fácil en la acción/objetivo de cada bloque de código.
        
        # Igualmente, realizar esto nos permite utilizar servicios/funciones públicas del producto de manera individual, como 
        # descargar las peliculas donde sea con el método scrapMovies(), o construir el CSV con cualquier lista de películas
        # hecha con storeMovies(), en vez de depender que siempre descargue y construya el mismo CSV "enorme" al llamarlo. 
        
        # PRINCIPIO SOLID - Interface Segregation: El Client no debe porqué lidiar con la función enorme y corrida de movie_fetcher,
        # por lo tanto se creó la interfaz de Client. Las interfaces son clave para los principios SOLID, leí, y tienen razón, el
        # Client debería tener métodos fáciles de comprender y usar a su disposición. Lo más intuitivo posible. En cierta parte creo
        # que también se cumple el principio de Inversión de Dependencia, por ahora que todos dependen de una abstracción como la
        # interfaz Client.
        movies = self.scrapMovies()

        # Creating a list with the movies inside
        list = self.storeMovies(movies)

        # Creamos y guardamos un objeto Movie con los contenedores de metadata listas para la DataBase
        # movies = Movie(list)
        # Error, no puedo mandar list, necesito hacer una función que manipule el objeto Movie

        # Creación de CSV  
        # DESIGN PATTERN: Facade. Se "dividen" las responsabilidades 
        # de crear el CSV a otra clase, se reducen librerías.
        # PRINCIPIO SOLID - Single Responsibility: Movie_Fetcher hacía cuatro cosas seguidas: descargar, extraer, guardar y crear
        # un CSV. Si bien, las primeras tres sí son sin duda, funciones de un fetcher; crear un CSV pudo separarse a otra clase
        # responsable de funcionalidades más enfocadas a crear reportes/imprimirlos: reporter.py 
        
        # CLEAN ARCHITECTURE: Se me hizo mucha funcionalidad en un bloque, por lo tanto lo refactoricé en trozos independientes
        # y más legibles.

        # PRINCIPIO SOLID - Open/Close: Movie_Fetcher tiene un objetivo muy directo y lo cumple sin problemas desde un principio.
        # después de su refactorización, opino que esta ahora en un estado donde es posible extenderlo sin tener que modificarlo.
        # Suelo creer que el no modificar un código es casi imposible, incluso con los que son escalables, pero si el objetivo de
        # este principio es "dejarlos lo más compacto posible", creo que así sí aplica, al menos con sus funciones principales
        # como scrapMovies() y storeMovies(), no creo que necesiten modificaciones, solo extensiones (guardar nuevas variables p.e.).

        # PRINCIPIO SOLID - Dependency Inversion: Creo que estoy equivocado, peor al hacer que Movie_Fetcher dependa ahora de una 
        # abstracción (de una interfaz, en este caso, Client), se cumple a cierto grado este principio. No solo eso, pero haber 
        # separado el constructor del CSV en otra clase, redujo la cantidad de librerías y métodos que no necesita saber un movie fetcher, 
        # y por lo tanto, el código se vuelve más organizado y legible para el desarrollador encargado de su mantenimiento o documentación.
        CSVReport(list)

    # Este nuevo metodo me hizo volver a importar csv, pero vale la pena
    def retrieveRecommendations(user):
        fields = ["preference_key", "movie_title", "star_cast", "rating", "year", "place", "vote", "link"]
        with open("movie_results.csv", "r") as file:
            reader = csv.DictReader(file)
            for movie in list:
                # Imprimir peliculas preference_key == user.preference_key
                return 1

    def getInstance():
        return 1

# En caso de que mi Singleton me traicione, rescatar:
#if __name__ == '__main__':
#    updateMovies()