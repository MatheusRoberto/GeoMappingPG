import json
from geopy.geocoders import OpenCage
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
from datetime import datetime

anuncios = {}
geoAnuncio = []


class Endereco:
    def __init__(self, logradouro, bairro, vila, cidade, numero):
        self.logradouro = logradouro
        if(numero != 0):
            self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        if vila is not None:
            self.vila = vila


class Anuncio:
    def __init__(self, ref, end, rua, numero, bairro, vila, cidade, valor, endMath, link):
        self.ref = ref
        self.enderecoAnuncio = end
        self.valor = valor
        now = datetime.now()
        self.data = '{:%d/%m/%Y}'.format(now)
        self.enderecoMatch = endMath
        self.endereco = Endereco(rua, bairro, vila, cidade, numero)
        self.link = link

    def toJSON(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def write_JSON():
    with open('./output/anunciosGeo.json', 'w') as f:
        json.dump(geoAnuncio, f, indent=4, ensure_ascii=False)


def open_JSON():
    global anuncios
    with open('./output/anuncios.json') as f:
        anuncios = json.load(f)


def main():
    open_JSON()
    geolocator = Nominatim()
    for anuncio in anuncios:
        print(anuncio["enderecoAnuncio"])
        # if location is not None:
        #print('Acesso a API')
        # print(anuncio["endereco"])
        try:
            location = geolocator.geocode(anuncio["enderecoAnuncio"])
            # print(location)
            if location is not None:
                ang = Anuncio(anuncio["endereco"], anuncio["valor"], location.latitude, location.longitude, anuncio['link'])
                geoAnuncio.append(json.loads(ang.toJSON()))
                write_JSON()
        except GeocoderTimedOut as e:
            print("Error: geocode failed on input %s with message %s" % (anuncio["endereco"], e))
        #print('Saiu da API')
        # if location is not None:
         #   ang = Anuncio(anuncio["endereco"], anuncio["valor"], location.latitude, location.longitude)
         #   geoAnuncio.append(json.loads(ang.toJSON()))
         #   write_JSON()
    #print((location.latitude, location.longitude))
    write_JSON()


if __name__ == '__main__':
    main()
