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

def carregaLogradouros():
    with open('./files/logradouros.txt', 'r', encoding="ISO-8859-1") as f:
        for line in f:
            logradouros.append(line)

def carregaBairros():
    with open('./files/bairros.txt', 'r', encoding="UTF-8") as f:
        for line in f:
            bairros.append(line)

def imovel(i, j):
    while (i <= j):

        r = session.get(f"https://procureimovel.com.br/venda/ponta-grossa-pr?fin=venda&t=&st=&cidade=ponta-grossa-pr&vMin=&vMax=&dts=&vagas=&ad=&o=0&page={i}")

        data = r.html.absolute_links

        # print(data)
        bairro = rua = numero = ''
        for d in data:
            try:
                re = session.get(d)
                end = re.html.find('.listing-address', first=True)
                preco = re.html.find('.property-price', first=True)
                ref = re.html.find('#sidebar > div > div.widget.margin-bottom-30 > mark', first=True)
                soup = BeautifulSoup(re.text, 'html.parser')
                select = '#wrapper > div:nth-child(8) > div > div.col-lg-8.col-md-7 > div > ul.property-features.margin-top-0 > li'
                element = soup.select(select)
                result = next((el for el in element if 'Bairro' in str(el)), None)
                if result is not None:
                    bairro = cleanhtml(str(result))
                    bairro = extractBairro(bairro)

                result = next((el for el in element if 'Endereço' in str(el)), None)
                if result is not None:
                    endereco = cleanhtml(str(result))
                    (rua, numero) = extractEndereco(endereco)

            except Exception as e:
                print(f"Link: {d}\n Error: {e}")

            if end and preco and ref:
                precoAnuncio = valorAnuncio(preco.text)
                #print(r.status_code)
                if not rua:
                    (pont, endMatch) = buscaRuaPG(rua)
                else:
                    (pont, endMatch) = buscaRuaPG(end.text)
                if pont >= 40 and precoAnuncio > 0:
                    if not rua and not numero and not bairro:
                        (rua, numero, bairro, cidade) = estruturandoEndereco(end.text)
                        anuncio = Anuncio(ref.text, end.text, rua, numero,
                                      bairro, cidade, precoAnuncio, endMatch, d)
                    elif not bairro:
                        anuncio = Anuncio(ref.text, end.text, rua, numero,
                         '', 'Ponta Grosa/PR', precoAnuncio, endMatch, d)
                    else:
                        anuncio = Anuncio(ref.text, end.text, rua, numero,
                                      bairro, 'Ponta Grosa/PR', precoAnuncio, endMatch, d)
                    anuncios.append(json.loads(anuncio.toJSON()))
        if r.status_code == 200:
            i += 12
    print(i)

def cleanhtml(raw_html):
  cleanr = regex.compile('<.*?>')
  cleantext = regex.sub(cleanr, '', raw_html)
  return cleantext

def extractBairro(bairro):
    bairroExtr = bairro.replace('Bairro: ', '')
    #print(f'Bairro: Pont: {pont} Match: {bairroMatch} Bairro: {bairroExtr}')
    if matchBairro(bairroExtr) > 75:
        return bairroExtr
    return ''

def extractEndereco(endereco):
    enderecoExtr = endereco.replace('Endereço: ', '')
    result_number = regex.search(r"\d+", enderecoExtr)
    if result_number is not None:
        numero = result_number.group(0)
        rua = enderecoExtr.split(',')
        return (rua[0], numero)
    else:
        return (enderecoExtr, 0)


def matchBairro(bairro):
    pontuacao = []
    fuzz.SequenceMatcher = difflib.SequenceMatcher
    for bai in bairros:
        pontuacao.append(fuzz.ratio(bairro, str(bai)))

    n_max = max(pontuacao, key=int)

    return n_max

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
        r"([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*?)(\s?-?)([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*)(, )(Ponta Grossa, PR)", endereco)
    
    for r in result:
        print(r)
    bairro = result.group(0)
    bairro = bairro.replace(', Ponta Grossa, PR', '')
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
    return regex.sub(r"([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*?)(\s?-?)([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*)(, )(Ponta Grossa, PR)", '', endereco)



def listLogradouros():
    for rua in logradouros:
        print(rua)


def buscaRuaPG(endEncontrado):

    if "Ponta Grossa, PR" not in endEncontrado:
        return (0, "")

    ruaEncontrada = rmBairroCidade(endEncontrado)
    if not ruaEncontrada:
        return (0, "")

    pontuacao = []
    fuzz.SequenceMatcher = difflib.SequenceMatcher
    for rua in logradouros:
        pontuacao.append(fuzz.ratio(ruaEncontrada, str(rua)))

    n_max = max(pontuacao, key=int)
    n_pos = pontuacao.index(n_max)

    return (n_max, logradouros[n_pos])


def main():

    carregaLogradouros()
    carregaBairros()

    r = session.get('https://procureimovel.com.br/venda/ponta-grossa-pr?fin=venda&t=&st=&cidade=ponta-grossa-pr&vMin=&vMax=&dts=&vagas=&ad=&o=0&page=1000')
    soup = BeautifulSoup(r.text, 'html.parser')

    npag = cleanhtml(str(soup.select('#wrapper > div.container > div > div.col-md-8 > div.pagination-container.margin-top-20 > nav.pagination > ul > li:nth-child(5) > a')))
    npag = npag.replace('[', '')
    npag = npag.replace(']', '')

    n = int(int(npag) / 4)

    thread1 = threading.Thread(target=imovel, args=(1, n))
    thread2 = threading.Thread(target=imovel, args=(n + 1, 2 * n))
    thread3 = threading.Thread(target=imovel, args=(2 * n + 1, 3 * n))
    thread4 = threading.Thread(target=imovel, args=(3 * n + 1, 4 * n))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

    return anuncios
