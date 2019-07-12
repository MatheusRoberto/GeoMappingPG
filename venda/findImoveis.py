import finders.findImConceito as findImConceito
import finders.findTavarnaro as findTavarnaro
import finders.findProcureImovel as findProcureImovel

import json
import time
import copy
import re as regex
from datetime import datetime

anuncios = []
anunciosToday = []


def write_JSON():
    with open('./output/anuncios.json', 'w') as f:
        json.dump(anuncios, f, indent=4, ensure_ascii=False)


def write_JSONToday():
    with open(f'./output/dates/anuncios_{time.time()}.json', 'w') as f:
        json.dump(anunciosToday, f, indent=4, ensure_ascii=False)


def open_JSON():
    global anuncios
    with open('./output/anuncios.json') as f:
        anuncios = json.load(f)


def compareAnuncio(anuncioA, anuncioB):
    if((anuncioA['endereco'] is anuncioB['endereco']
        or anuncioA['enderecoAnuncio'] == anuncioB['enderecoAnuncio'])
       and (anuncioA['valor'] != anuncioB['valor'])):
        return True
    return False


def main():
    inicio = time.time()
    open_JSON()
    
    print('Imobiliaria Conceito')
    anunciosConceito = findImConceito.main()
    for anuncioE in anunciosConceito:
        anunciosToday.append(anuncioE)
        findAnuncio = next(
            (anuncio for anuncio in anuncios if anuncio['ref'] == anuncioE['ref']), None)
        if(findAnuncio is None):
            anuncios.append(anuncioE)
        else:
            if(compareAnuncio(findAnuncio, anuncioE)):
                #anuncios.remove(findAnuncio)
                anuncios.append(anuncioE)
    write_JSON()
    #write_JSONToday()

    print('----------------------------------')
    print('Imobiliaria Tavarnaro')
    anunciosTavarnaro = findTavarnaro.main()
    for anuncioE in anunciosTavarnaro:
        anunciosToday.append(anuncioE)
        findAnuncio = next(
            (anuncio for anuncio in anuncios if anuncio['ref'] == anuncioE['ref']), None)
        if(findAnuncio is None):
            anuncios.append(anuncioE)
        else:
            if(compareAnuncio(findAnuncio, anuncioE)):
                #anuncios.remove(findAnuncio)
                anuncios.append(anuncioE)
    write_JSON()
    #write_JSONToday()

    print('----------------------------------')
    print('Procure Imovel')
    anunciosProcureImovel = findProcureImovel.main()
    for anuncioE in anunciosProcureImovel:
        anunciosToday.append(anuncioE)
        findAnuncio = next(
            (anuncio for anuncio in anuncios if anuncio['ref'] == anuncioE['ref']), None)
        if(findAnuncio is None):
            anuncios.append(anuncioE)
        else:
            if(compareAnuncio(findAnuncio, anuncioE)):
                #anuncios.remove(findAnuncio)
                anuncios.append(anuncioE)
    write_JSON()
    write_JSONToday()

    print('Fim da busca')
    fim = time.time()
    total = fim - inicio
    total = datetime.utcfromtimestamp(total).strftime('%H:%M:%S')
    print(f'total da busca: {total}')
