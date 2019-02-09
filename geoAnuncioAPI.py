import json
from geopy.geocoders import OpenCage
from geopy.geocoders import GoogleV3
from geopy.exc import GeocoderTimedOut
from datetime import datetime

anuncios = {}
geoAnuncio = []

class Anuncio:
    def __init__(self, end, valor, lat, lng):
        self.endereco = end
        self.valor = valor
        now = datetime.now()
        self.data = '{:%d/%m/%Y}'.format(now)
        self.geoLocation = [lat, lng]

    def toJSON(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__,sort_keys=True, indent=4)

def write_JSON():
    with open('./output/anunciosGeo.json', 'w') as f:
        json.dump(geoAnuncio, f, indent=4, ensure_ascii=False)

def open_JSON():
    global anuncios
    with open('./output/anuncios.json') as f:
       anuncios = json.load(f)
        


def main():
    open_JSON()
    idAPI = 000000 #Aqui vai teu ID da API do Google GeocodingAPI, existe versão gratuira vide o Docs do geolocator
    geolocator = GoogleV3(api_key=idAPI)
    for anuncio in anuncios:
        #print(anuncio["endereco"])
        #if location is not None:
        #print('Acesso a API')
        #print(anuncio["endereco"])
        try:
            location = geolocator.geocode(anuncio["endereco"])
        except GeocoderTimedOut as e:
            print("Error: geocode failed on input %s with message %s"%(anuncio["endereco"], e))
        #print('Saiu da API')
        if location is not None:
            ang = Anuncio(anuncio["endereco"], anuncio["valor"], location.latitude, location.longitude)
            geoAnuncio.append(json.loads(ang.toJSON()))
            write_JSON()
    #print((location.latitude, location.longitude)) 
    write_JSON()

if __name__ == '__main__':
    main()