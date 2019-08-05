import json
import re as regex
from datetime import datetime
import geocoder
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from pymongo import MongoClient
import threading

anuncios = {}
solving = []
prontos = []
total = []
notprontos = []
localiza = ["Rua Dezenove de março, 650, Centro, Arandu - SP",
     "Rua Ernesto Vilela, 380, Centro, Ponta Grossa - PR",
     "Rua Coronel Claudio, 279, Centro, Ponta Grosa - PR",
     "Rua Balduino Taques, 480, Centro, Ponta Grossa - PR",
     "Rua Vicente Sposito, 180, Uvaranas - Ponta Grossa - PR",
     "Rua José Batista Pereira, 160, Jardim Italia, Araundu/SP"]

class Endereco:
    def __init__(self, endereco):
        self.logradouro = endereco["logradouro"]
        if 'numero' in endereco:
            self.numero = endereco["numero"]
        self.bairro = endereco["bairro"]
        self.cidade = endereco["cidade"]
        if 'vila' in endereco:
            self.vila = endereco["vila"]


class Anuncio:
    def __init__(self, anuncio, ref):
        self.ref = ref
        self.enderecoAnuncio = anuncio["endereco"]
        self.valor = anuncio["valor"]
        self.data = anuncio["data"]
        self.enderecoMatch = anuncio["enderecoMatch"]
        self.endereco = Endereco(anuncio)
        self.link = anuncio["link"]

    def toJSON(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def open_JSONFinal():
    global solving
    global total
    with open('./output/anuncios.json') as f:
        solving = json.load(f)


def open_JSONMaior():
    global anuncios
    with open('./output/anunciosTotaisIns.json') as f:
        anuncios = json.load(f)


def open_JSONMenor():
    global solving
    with open('./output/anuncios1518.json') as f:
        solving = json.load(f)


def write_JSON(solving):
    with open('./output/anuncios.json', 'w') as f:
        json.dump(solving, f, indent=4, ensure_ascii=False)


def write_JSONTotal(total):
    with open('./output/anunciosTotais.json', 'w') as f:
        json.dump(total, f, indent=4, ensure_ascii=False)
    with open('./output/anunciosTotaisIns.json', 'w') as f:
        json.dump(total, f, ensure_ascii=False)


def write_JSONNot(notprontos):
    with open('./output/anunciosNot.json', 'w') as f:
        json.dump(notprontos, f, indent=4, ensure_ascii=False)


def solvingRef(link):
    if 'conceitoimoveispg' in link:
        return link.split('/')[4]
    elif 'tavarnaroconsultoria' in link:
        return link.split('/')[5]
    elif 'procureimovel' in link:
        return regex.search(r"ref-\d*-\d", link)[0]


class Valor:
    def __init__(self, data, valor):
        self.data = data
        self.valor = valor

    def toJSON(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def compareAnuncio(anuncioA, anuncioB):
    if((anuncioA['endereco'] is anuncioB['endereco']
            or anuncioA['enderecoAnuncio'] == anuncioB['enderecoAnuncio'])):
        return True
    return False


def criaArrayValores(anuncioA, anuncioB):
    valores = []
    if 'valor' in anuncioA and isinstance(anuncioA['valor'], list):
        valores = anuncioA['valor']
        findValor = next(
            (valor for valor in valores if anuncioB['data'] == valor['data']), None)
        if findValor is None:
            valor = Valor(anuncioB['data'], anuncioB['valor'])
            valores.append(json.loads(valor.toJSON()))
        elif findValor['valor'] != anuncioB['valor']:
            valor = Valor(anuncioB['data'], anuncioB['valor'])
            valores.append(json.loads(valor.toJSON()))
    else:
        valor = Valor(anuncioA['data'], anuncioA['valor'])
        valores.append(json.loads(valor.toJSON()))
        valorb = Valor(anuncioB['data'], anuncioB['valor'])
        valores.append(json.loads(valorb.toJSON()))
    return valores

def procura(i,j):

    geocoder = Nominatim(user_agent="GeomappingPontaGrossa")
    localizador = RateLimiter(geocoder.geocode, min_delay_seconds=2)
    for i in range(i, j):
        finder = localizador(localiza[i])
                
        if finder is not None:
            print(f"Rua {localiza[i]} Lat: {finder.latitude} Lng: {finder.longitude}")


def main():
    # open_JSONMaior()
    # open_JSONMenor()

    '''
    open_JSONFinal()
    cliente = MongoClient('localhost', 27017)
    banco = cliente.anuncios
    album = banco.anuncios
    count = 0
    
    for anuncio in solving:
        result = album.find({"ref": anuncio['ref']})
        if result.count() == 0:
            album.insert(anuncio)

    for anuncio in solving:
        result = album.find({"ref": anuncio['ref']})
        if result.count() > 1:
            count += 1
        

    print(count)
'''


    thread1 = threading.Thread(target=procura, args=(0, 1))
    thread2 = threading.Thread(target=procura, args=(2,3))
    thread3 = threading.Thread(target=procura, args=(3,4))
    thread4 = threading.Thread(target=procura, args=(5,5))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

if __name__ == "__main__":
    main()
