import geocoder
import json

anuncios = {}
geoAnuncio = []
notGeoAnuncio = []

class Localizacao:
    def __init__(self, latitude, longitude):
        self.type = "Point"
        self.coordenadas = []
        self.coordenadas.append(latitude)
        self.coordenadas.append(longitude)

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
    def __init__(self, anuncio, latitude, longitude ):
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

def write_JSONNot():
    with open('./output/anunciosGeoNot.json', 'w') as f:
        json.dump(geoAnuncio, f, indent=4, ensure_ascii=False)

def open_JSON():
    global anuncios
    with open('./output/anuncios.json') as f:
        anuncios = json.load(f)

def main():
    open_JSON()
    for anuncio in anuncios:

        if 'localizacao' in anuncio:
            continue

        enderecoFinder = ""

        enderecoAnuncio = anuncio["enderecoAnuncio"]
        enderecoMatch = anuncio["enderecoMatch"]
        logradouro = anuncio['endereco']['logradouro']
        bairro = anuncio['endereco']['bairro']
        cidade = anuncio['endereco']['cidade']
        numero = None
        vila = None
        if 'numero' in anuncio['endereco']:
            numero = anuncio['endereco']['numero']

        if 'vila' in anuncio['endereco']:
            vila = anuncio['endereco']['vila']

        enderecoFinder = enderecoAnuncio
        tries = 0
        coordinate = []
        while not coordinate:
            if tries > 3:
                break
            if tries == 1:
                if numero is not None:
                    enderecoFinder = (u"{}, {} - {} - {}".format(logradouro, numero, bairro, cidade))
                else:
                    enderecoFinder = (u"{} - {} - {}".format(logradouro, bairro, cidade))
            elif tries == 2:
                if vila is not None:
                    if numero is not None:
                        enderecoFinder = (u"{}, {} - {} - {}".format(logradouro, numero, vila, cidade))
                    else:
                        enderecoFinder = (u"{} - {} - {}".format(logradouro, vila, cidade))
            elif tries == 3:
                if numero is not None:
                    enderecoFinder = (u"{}, {} - {} - {}".format(enderecoMatch, numero, bairro, cidade))
                else:
                    enderecoFinder = (u"{} - {} - {}".format(enderecoMatch, bairro, cidade))
            
            g = geocoder.osm(enderecoFinder)
            if g is not None:
                coordinate = g.latlng
                if g.status is not 'OK' and g.status is None:
                    print(g.json)

            tries += 1 # adiciono mais um no número de tentativas para controle
        
        if coordinate is not None:
            anuncioGeolocalizado = Anuncio(anuncio, coordinate[0], coordinate[1])
            geoAnuncio.append(json.loads(anuncioGeolocalizado.toJSON()))
        else:
            anuncioGeolocalizado = Anuncio(anuncio, 0.0, 0.0)
            notGeoAnuncio.append(json.loads(anuncioGeolocalizado.toJSON()))

    write_JSON()
    write_JSONNot()

if __name__ == "__main__":
    main()