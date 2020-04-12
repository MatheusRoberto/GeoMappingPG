# coding: utf-8
from pymongo import MongoClient
import json
import pandas as pd
import numpy as np

anuncios = []
geolocalizados = []

cliente = MongoClient('')
banco = cliente.anuncios
albumGeolocalizados = banco.anunciosGeorreferenciados


def openJSON():
    global anuncios
    global geolocalizados
    with open('./output/anuncios.json') as f:
        anuncios = json.load(f)

    with open('./output/anunciosGeo.json') as f:
        geolocalizados = json.load(f)


def main():
    lista = []
    result = albumGeolocalizados.find()
    clist = 0
    cunique = 0
    for anuncio in result:
        a = anuncio
        endereco = a['endereco']
        localizacao = a['localizacao']
        a['latitude'] = localizacao['coordinates'][0]
        a['longitude'] = localizacao['coordinates'][1]    
        a['tipo'] = localizacao['type']    
        a['bairro'] = endereco['bairro']
        a['cidade'] = endereco['cidade']
        a['logradouro'] = endereco['logradouro']
        a['enderecoMatch'] = a['enderecoMatch'].replace("\n", "")
        if 'numero' in endereco:
            a['numero'] = endereco['numero']
            
        if 'vila' in endereco:
            a['vila'] = endereco['vila']

        a.pop('_id', None)
        a.pop('endereco', None)
        a.pop('localizacao', None)
        if 'valor' in a and isinstance(a['valor'], list):
            clist += len(a['valor'])
            for valor in a['valor']:
                an = a
                an['data'] = valor['data']
                an['valor'] = valor['valor']
                lista.append(an)
        else:
            cunique += 1
            lista.append(a)
            
    print(len(lista))
    print(clist)
    print(cunique)    
    print(len(lista) - (clist + cunique))
    
    df = pd.DataFrame(lista)
    
    df.to_csv('data.csv', index=False)
    df.to_csv('data.tsv', index=False, sep='\t')
    

if __name__ == "__main__":
    main()
