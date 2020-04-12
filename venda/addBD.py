# coding: utf-8
from pymongo import MongoClient
import json
import re as regex
from datetime import datetime
import threading

anuncios = []
geolocalizados = []

cliente = MongoClient('mongodb+srv://user:password@cluster0-2zsqx.mongodb.net/test?retryWrites=true&w=majority')
banco = cliente.anuncios
albumAnuncios = banco.anuncios
albumGeolocalizados = banco.anunciosGeorreferenciados

countAnuncios = 0
countGeoBDNotJSON = 0
countGeolocalizados = 0


def openJSON():
    global anuncios
    global geolocalizados
    with open('./output/anuncios.json') as f:
        anuncios = json.load(f)

    with open('./output/anunciosGeo.json') as f:
        geolocalizados = json.load(f)


def write_JSON(solving):
    with open('./output/anuncios.json', 'w') as f:
        json.dump(solving, f, indent=4, ensure_ascii=False)


def bancoGeral():
    for anuncio in anuncios:
        result = albumAnuncios.find({"ref": anuncio['ref']})
        if result.count() == 0:
            albumAnuncios.insert(anuncio)
        else:
            if 'localizacao' in result[0] and 'localizacao' not in anuncio:
                anuncio.localizacao = result[0]['localizacao']
                countGeoBDNotJSON += 1
            albumAnuncios.update({"ref": anuncio['ref']}, anuncio)

    for anuncio in anuncios:
        result = albumAnuncios.find({"ref": anuncio['ref']})
        if result.count() > 1:
            countAnuncios += 1


def bancoGeo():
    for anuncio in geolocalizados:
        result = albumGeolocalizados.find({"ref": anuncio['ref']})
        if result.count() == 0:
            albumGeolocalizados.insert(anuncio)
        else:
            albumGeolocalizados.update({"ref": anuncio['ref']}, anuncio)

    for anuncio in geolocalizados:
        result = albumGeolocalizados.find({"ref": anuncio['ref']})
        if result.count() > 1:
            countGeolocalizados += 1


def main():
    openJSON()

    thread1 = threading.Thread(target=bancoGeral)
    thread2 = threading.Thread(target=bancoGeo)

    threads = []
    threads.append(thread1)
    threads.append(thread2)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print(
        f"Duplicados em Anuncios: {countAnuncios}, Duplicadoso em Georrefenciados: {countGeolocalizados}, Georreferenciado no Banco mas nao no JSON {countGeoBDNotJSON}")


if __name__ == "__main__":
    main()
