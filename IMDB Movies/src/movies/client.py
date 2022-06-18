import movie_fetcher

# PRINCIPIO POO: Abstracción - Con crear una interfaz usuario, nos aseguramos
# de mostrar o servir lo más importante para el mismo. Es decir, el usuario
# no tiene por qué preocuparse con conocer métodos como el scrapeo de las
# películas o la creación de un CSV para el guardado de datos.

# DESIGN PATTERN: Repository - Al tener a Client como una clase, podemos
# tener varias instancias del mismo en el servidor.
class Client:

    # Instancia de un Cliente User por sesión
    def __init__(self):
        self.admin = False
        movie_fetcher.init(self)

    def start(self):
        if(self.admin):
            movie_fetcher.updateMovies()

    # PRINCIPIO POO: Encapsulamiento - Por tener a Client como instancia de objeto,
    # podemos proteger sus variables manteniéndolas privadas.
    def register(self, name = None, p1 = None, p2 = None, p3 = None):
        if(name == None):
            return "Error, no registrar un nulo a la Base de Datos"
        else:
            self.name = name
            self.categoria1 = p1
            self.categoria2 = p2
            self.categoria3 = p3
            self.preference_key = self.calculate_preferenceKey(self)

    def calculate_preferenceKey(self):
        return (self.categoria1 * self.categoria2 * self.categoria3) % 5 + 1

def main():
    app = Client()

    
