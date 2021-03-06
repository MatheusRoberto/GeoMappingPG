# coding: utf-8
import threading
import json
import re as regex
import difflib
from requests_html import HTMLSession
from datetime import datetime
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup

session = HTMLSession()

anuncios = []
logradouros = []
bairros = []


class Endereco:
    def __init__(self, logradouro, bairro, cidade, numero):
        self.logradouro = logradouro
        if(numero != 0):
            self.numero = numero
        self.bairro = bairro
        self.cidade = cidade


class Anuncio:
    def __init__(self, ref, end, rua, numero, bairro, cidade, valor, endMath, link):
        self.ref = ref
        self.enderecoAnuncio = end
        self.valor = valor
        now = datetime.now()
        self.data = '{:%d/%m/%Y}'.format(now)
        self.enderecoMatch = endMath
        self.endereco = Endereco(rua, bairro, cidade, numero)
        self.link = link

    def toJSON(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def valorAnuncio(preco):
    resultado = regex.findall(
        r"(?:[1-9](?:[\d]{0,2}(?:\.[\d]{3})*|[\d]+)|0)(?:,[\d]{0,2})?", preco)
    x = []
    if not resultado:
        return float(0.00)
    for r in resultado:
        value = r.replace('.', '')
        value = value.replace(',', '.')
        x.append(float(value))
    return max(x, key=float)


def estruturandoEndereco(endereco):

    result = regex.search(
        r"([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*?)(\s?-?)([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*)( - )(Ponta Grossa/PR)", endereco)

    bairro = result.group(0)
    bairro = bairro.replace(' - Ponta Grossa/PR', '')
    bairro = bairro.replace(' - ', '')

    result_number = regex.search(r"\d+", endereco)
    if result_number is not None:
        numero = result_number.group(0)
        rua = endereco.split(',')
        return (rua[0], numero, bairro, "Ponta Grossa/PR")
    else:
        rua = endereco.split('-')
        return (rua[0], 0, bairro, "Ponta Grossa/PR")


def rmBairroCidade(endereco):
    return regex.sub(r"([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*?)(\s?-?)([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*)( - )(Ponta Grossa/PR)", '', endereco)


def carregaLogradouros():
    with open('./files/logradouros.txt', 'r', encoding="ISO-8859-1") as f:
        for line in f:
            logradouros.append(line)

def buscaRuaPG(endEncontrado):

    if "Ponta Grossa/PR" not in endEncontrado:
        return (0, "")

    ruaEncontrada = rmBairroCidade(endEncontrado)
    if not ruaEncontrada:
        return (0, "")

    pontuacao = []
    fuzz.SequenceMatcher = difflib.SequenceMatcher
    for rua in logradouros:
        pontuacao.append(fuzz.ratio(ruaEncontrada, str(rua)))

    n_max = 0
    if pontuacao:
        n_max = max(pontuacao, key=int)
        n_pos = pontuacao.index(n_max)
        return (n_max, logradouros[n_pos])
    return (0, 0)

def extractLinks(data):
    links = []
    for d in data:
        result = d.find("TAVB")
        if result != -1:
            links.append(d)
    return links

def imovel(i, j):
    while (i <= j):
        print(f'{i} de {j}')
        r = session.get(
            f"https://www.tavarnaroconsultoria.com.br/imoveis/a-venda?pagina={i}")

        data = r.html.absolute_links

        links = extractLinks(data)

        for d in links:
            try:
                re = session.get(d)
                end = re.html.find('.header-title .sub', first=True)
                preco = re.html.find('.price', first=True)
            except Exception as e:
                print(f"Link: {d}\n Error: {e}")

            try:
                if end and preco:
                    precoAnuncio = valorAnuncio(preco.text)
                    (pont, endMatch) = buscaRuaPG(end.text)
                    if pont >= 40 and precoAnuncio > 0:
                        print(r.status_code)
                        (rua, numero, bairro, cidade) = estruturandoEndereco(end.text)
                        anuncio = Anuncio(d.split(
                            '/')[5], end.text, rua, numero, bairro, cidade, precoAnuncio, endMatch, d)
                        anuncios.append(json.loads(anuncio.toJSON()))
            except Exception as e:
                print(f"Link: {d}\n Error: {e}")
        if r.status_code == 200:
            i += 1
    # print(i)

def cleanhtml(raw_html):
  cleanr = regex.compile('<.*?>')
  cleantext = regex.sub(cleanr, '', raw_html)
  return cleantext

def carregaBairros():
    with open('./files/bairros.txt', 'r', encoding="UTF-8") as f:
        for line in f:
            bairros.append(line)

def main():

    carregaLogradouros()
    carregaBairros()

    r = session.get('https://www.tavarnaroconsultoria.com.br/imoveis/a-venda')
    soup = BeautifulSoup(r.text, 'html.parser')
    
    elemeSelect = soup.select('div.pagination-cell.hidden-lg-up > p')
    npag = elemeSelect[0].text
    npag = int(regex.findall(r"\d+", npag)[1])

    n = int(npag / 4)

    thread1 = threading.Thread(target=imovel, args=(1, n))
    thread2 = threading.Thread(target=imovel, args=(n + 1, 2 * n))
    thread3 = threading.Thread(target=imovel, args=(2 * n + 1, 3 * n))
    thread4 = threading.Thread(target=imovel, args=(3 * n + 1, npag))

    threads = []
    threads.append(thread1)
    threads.append(thread2)
    threads.append(thread3)
    threads.append(thread4)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    return anuncios
