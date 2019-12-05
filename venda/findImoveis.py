# coding: utf-8
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

class Valor:
    def __init__(self, data, valor):
        self.data = data
        self.valor = valor
    def toJSON(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def write_JSON():
    with open('./output/anuncios.json', 'w') as f:
        json.dump(anuncios, f, indent=4, ensure_ascii=False)

    with open(f'./output/dates/finder/anuncios_{time.time()}.json', 'w') as f:
        json.dump(anunciosToday, f, indent=4, ensure_ascii=False)


def open_JSON():
    global anuncios
    with open('./output/anuncios.json') as f:
        anuncios = json.load(f)


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
            (valor for valor in valores if anuncioB['data'] == valor['data'] ), None)
        if findValor is None:
            valor = Valor(anuncioB['data'], anuncioB['valor'])
            valores.append(json.loads(valor.toJSON()))
        elif findValor['valor'] != anuncioB['valor']:
            valor = Valor(anuncioB['data'], anuncioB['valor'])
            valores.append(json.loads(valor.toJSON()))
    else:
        if(anuncioA['data'] == anuncioB['data'] and anuncioA['valor'] == anuncioB['valor']):
            valores.append(json.loads(Valor(anuncioA['data'], anuncioA['valor']).toJSON()))
        else:
            valor = Valor(anuncioA['data'], anuncioA['valor'])
            valores.append(json.loads(valor.toJSON()))
            valorb = Valor(anuncioB['data'], anuncioB['valor'])
            valores.append(json.loads(valorb.toJSON())) 
    return valores

def main():
    inicio = time.time()
    open_JSON()
    
    print('Imobiliaria Conceito')
    anunciosConceito = findImConceito.main()
    print(f'Total encontrado - Imobiliaria Conceito: {len(anunciosConceito)}')
    for anuncioE in anunciosConceito:
        anunciosToday.append(anuncioE)
        findAnuncio = next(
            (anuncio for anuncio in anuncios if anuncio['ref'] == anuncioE['ref']), None)
        if(findAnuncio is None):
            anuncios.append(anuncioE)
        else:
            if(compareAnuncio(findAnuncio, anuncioE)):
                anuncios[anuncios.index(findAnuncio)]['valor'] = criaArrayValores(findAnuncio, anuncioE)
                #anuncios.remove(findAnuncio)
                # anuncios.append(anuncioE)
    # write_JSON()

    '''
    print('----------------------------------')
    print('Imobiliaria Tavarnaro')
    anunciosTavarnaro = findTavarnaro.main()
    print(f'Total encontrado - Imobiliaria Tavarnaro: {len(anunciosTavarnaro)}')
    for anuncioE in anunciosTavarnaro:
        anunciosToday.append(anuncioE)
        findAnuncio = next(
            (anuncio for anuncio in anuncios if anuncio['ref'] == anuncioE['ref']), None)
        if(findAnuncio is None):
            anuncios.append(anuncioE)
        else:
            if(compareAnuncio(findAnuncio, anuncioE)):
                anuncios[anuncios.index(findAnuncio)]['valor'] = criaArrayValores(findAnuncio, anuncioE)
                #anuncios.remove(findAnuncio)
                #anuncios.append(anuncioE)
    # write_JSON()
    '''

    print('----------------------------------')
    print('Procure Imovel')
    anunciosProcureImovel = findProcureImovel.main()
    print(f'Total encontrado - Procure Imovel: {len(anunciosProcureImovel)}')
    for anuncioE in anunciosProcureImovel:
        anunciosToday.append(anuncioE)
        findAnuncio = next(
            (anuncio for anuncio in anuncios if anuncio['ref'] == anuncioE['ref']), None)
        if(findAnuncio is None):
            anuncios.append(anuncioE)
        else:
            if(compareAnuncio(findAnuncio, anuncioE)):
                anuncios[anuncios.index(findAnuncio)]['valor'] = criaArrayValores(findAnuncio, anuncioE)
                #anuncios.remove(findAnuncio)
                #anuncios.append(anuncioE)
    write_JSON()

    print('Fim da busca')
    fim = time.time()
    total = fim - inicio
    total = datetime.utcfromtimestamp(total).strftime('%H:%M:%S')
    print(f'Tempo total do Finder: {total}')
    print(f'Numero total de registros encontrados: {len(anunciosToday)}')
