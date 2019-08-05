import json
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime
import threading

anuncios = []
geoAnuncio = []
notGeoAnuncio = []
final = []
anunciosToday = []

geocoder = Nominatim(user_agent="GeomappingPontaGrossa")
localizador = RateLimiter(geocoder.geocode, min_delay_seconds=3)

class Localizacao:
    def __init__(self, latitude, longitude):
        self.type = "Point"
        self.coordinates = []
        self.coordinates.append(latitude)
        self.coordinates.append(longitude)


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
    def __init__(self, anuncio, latitude, longitude):
        self.ref = anuncio["ref"]
        self.enderecoAnuncio = anuncio["enderecoAnuncio"]
        self.valor = anuncio["valor"]
        self.data = anuncio["data"]
        self.enderecoMatch = anuncio["enderecoMatch"]
        self.endereco = Endereco(anuncio["endereco"])
        self.link = anuncio["link"]
        self.localizacao = Localizacao(latitude, longitude)

    def toJSON(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def write_JSON():
    with open('./output/anunciosGeo.json', 'w') as f:
        json.dump(geoAnuncio, f, indent=4, ensure_ascii=False)

    with open('./output/anunciosGeoNot.json', 'w') as f:
        json.dump(notGeoAnuncio, f, indent=4, ensure_ascii=False)

    with open('./output/anuncios.json', 'w') as f:
        json.dump(anuncios, f, indent=4, ensure_ascii=False)

    with open(f'./output/dates/geolocator/anuncios_{time.time()}.json', 'w') as f:
        json.dump(anunciosToday, f, indent=4, ensure_ascii=False)

def open_JSON():
    global anuncios
    with open('./output/anuncios.json') as f:
        anuncios = json.load(f)

def finder(i, j):
    global final
    for k in range(i, j):
        if 'localizacao' in anuncios[k]:
            final.append(anuncios[k])
            geoAnuncio.append(anuncios[k])
            continue

        enderecoFinder = ""

        enderecoAnuncio = anuncios[k]["enderecoAnuncio"]
        enderecoMatch = anuncios[k]["enderecoMatch"]
        logradouro = anuncios[k]['endereco']['logradouro']
        bairro = anuncios[k]['endereco']['bairro']
        cidade = anuncios[k]['endereco']['cidade']
        numero = None
        vila = None
        if 'numero' in anuncios[k]['endereco']:
            numero = anuncios[k]['endereco']['numero']

        if 'vila' in anuncios[k]['endereco']:
            vila = anuncios[k]['endereco']['vila']

        enderecoFinder = enderecoAnuncio
        tries = 0
        coordinate = []
        while not coordinate:
            if tries > 3:
                break
            if tries == 1:
                if numero is not None:
                    enderecoFinder = (
                        u"{}, {} - {} - {}".format(logradouro, numero, bairro, cidade))
                else:
                    enderecoFinder = (
                        u"{} - {} - {}".format(logradouro, bairro, cidade))
            elif tries == 2:
                if vila is not None:
                    if numero is not None:
                        enderecoFinder = (
                            u"{}, {} - {} - {}".format(logradouro, numero, vila, cidade))
                    else:
                        enderecoFinder = (
                            u"{} - {} - {}".format(logradouro, vila, cidade))
            elif tries == 3:
                if numero is not None:
                    enderecoFinder = (
                        u"{}, {} - {} - {}".format(enderecoMatch, numero, bairro, cidade))
                else:
                    enderecoFinder = (
                        u"{} - {} - {}".format(enderecoMatch, bairro, cidade))

            finder = localizador(enderecoFinder)
                
            if finder is not None:
                coordinate.append(finder.latitude)
                coordinate.append(finder.longitude)

            tries += 1  # adiciono mais um no número de tentativas para controle

        if coordinate:
            anuncioGeolocalizado = Anuncio(
                anuncios[k], coordinate[0], coordinate[1])
            geoAnuncio.append(json.loads(anuncioGeolocalizado.toJSON()))
            anunciosToday.append(json.loads(anuncioGeolocalizado.toJSON()))
            print(f'{k} de {len(anuncios)} - Codigo: {anuncioGeolocalizado.ref} encontrado')
        else:
            notGeoAnuncio.append(anuncios[k])
            print(f'{k} de {len(anuncios)} - Codigo: {anuncios[k]["ref"]} não encontrado')


def main():
    inicio = time.time()
    open_JSON()

    # n = int(len(anuncios) / 6)

    thread1 = threading.Thread(target=finder, args=(0, len(anuncios)))

    threads = []
    threads.append(thread1)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    global final
    final += geoAnuncio + notGeoAnuncio
    write_JSON()

    print('Fim da busca')
    fim = time.time()
    total = fim - inicio
    total = datetime.utcfromtimestamp(total).strftime('%H:%M:%S')
    print(f'Tempo total da Georreferenciamento: {total}')
    print(f'Numero total de registros georreferenciados: {len(anunciosToday)}')

