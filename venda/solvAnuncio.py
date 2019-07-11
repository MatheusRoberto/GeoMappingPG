import json
import re as regex
from datetime import datetime

anuncios = {}
solving = []
prontos = []
total = []


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
    global prontos
    with open('./output/anuncios.json') as f:
        solving = json.load(f)
    with open('./output/anunciosTotais.json') as f:
        prontos = json.load(f)


def open_JSONMaior():
    global anuncios
    with open('./output/anuncios1937.json') as f:
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


def solvingRef(link):
    if 'conceitoimoveispg' in link:
        return link.split('/')[4]
    elif 'tavarnaroconsultoria' in link:
        return link.split('/')[5]
    elif 'procureimovel' in link:
        return regex.search(r"ref-\d*-\d", link)[0]


def main():
    # open_JSONMaior()
    # open_JSONMenor()
    open_JSONFinal()
    duplicadas = []

    total = 0
    no = 0
    for anuncioE in prontos:
        if 'localizacao' in anuncioE:
            total += 1
        else:
            no += 1


    print(total)
    print(no)


if __name__ == "__main__":
    main()
