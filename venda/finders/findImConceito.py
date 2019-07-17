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
    def __init__(self, logradouro, bairro, vila, cidade, numero):
        self.logradouro = logradouro
        if(numero != 0):
            self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
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
        print(f'{i} de {j}')
        r = session.get(
            f"https://www.conceitoimoveispg.com.br/busca/venda/cidade_ponta-grossa/pag_{i}")

        data = r.html.absolute_links

        for d in data:
            if d == 'tel:+554230251818':
                continue

            try:
                re = session.get(d)

                bairro = vila = cidade = ''
                end = re.html.find('.imovelTitle .fa',
                                   first=True, _encoding="ISO-8859-1")
                preco = re.html.find('.price', first=True,
                                     _encoding="ISO-8859-1")
                fichaTecnica = re.html.find(
                    'body > div:nth-child(9) > div.imovelv2.imovelToSell > div > div.imovelInfoMain > div.p60.imobInfoBox.correctAlign > div:nth-child(1) > h5 > i', first=True,  _encoding="ISO-8859-1")
                if fichaTecnica is not None:
                    soup = BeautifulSoup(re.text, 'html.parser')
                    select = 'body > div:nth-child(9) > div.imovelv2.imovelToSell > div > div.imovelInfoMain > div.p60.imobInfoBox.correctAlign > div:nth-child(1) > div > ul > li'
                    element = soup.select(select)
                    result = next(
                        (el for el in element if 'Bairro' in str(el)), None)
                    if result is not None:
                        bairro = cleanhtml(str(result))
                        bairro = extractBairro(bairro)

                    result = next(
                        (el for el in element if 'Vila' in str(el)), None)
                    if result is not None:
                        vila = cleanhtml(str(result))
                        vila = extractVila(vila)

                    result = next(
                        (el for el in element if 'Cidade' in str(el)), None)
                    if result is not None:
                        cidade = cleanhtml(str(result))
                        cidade = extractCidade(cidade)
            except Exception as e:
                print(f"Link: {d}\n Error: {e}")

            if end and preco:
                precoAnuncio = valorAnuncio(preco.text)
                (pont, endMatch) = buscaRuaPG(end.text)
                if precoAnuncio > 0 and pont >= 40:
                    print(r.status_code)
                    if not bairro and not vila and not cidade:
                        (rua, numero, bairro, vila,
                         cidade) = estruturandoEndereco(end.text)
                    else:
                        (rua, numero) = reconheceEndereco(end.text)

                    anuncio = Anuncio(d.split('/')[4], end.text, rua, numero,
                                      bairro, vila, cidade, precoAnuncio, endMatch, d)
                    anuncios.append(json.loads(anuncio.toJSON()))
        if r.status_code == 200:
            i += 1
    # print(r.status_code)
    # print(i)


def cleanhtml(raw_html):
    cleanr = regex.compile('<.*?>')
    cleantext = regex.sub(cleanr, '', raw_html)
    return cleantext


def extractBairro(bairro):
    bairroExtr = bairro.replace('Bairro', '')
    #print(f'Bairro: Pont: {pont} Match: {bairroMatch} Bairro: {bairroExtr}')
    if matchBairro(bairroExtr) > 75:
        return bairroExtr
    return ''


def extractVila(vila):
    vilaExtr = vila.replace('Vila', '')
    #print(f'Vila: Pont: {pont} Match: {bairroMatch} Bairro: {vilaExtr}')
    if matchBairro(vilaExtr) > 75:
        return vilaExtr
    return ''


def extractCidade(cidade):
    return cidade.replace('Cidade', '')


def matchBairro(bairro):
    pontuacao = []
    fuzz.SequenceMatcher = difflib.SequenceMatcher
    for bai in bairros:
        pontuacao.append(fuzz.ratio(bairro, str(bai)))

    n_max = max(pontuacao, key=int)

    return n_max


def reconheceEndereco(endereco):
    if "s/n" or "S/N" or "s/c" in endereco:
        rua = endereco.split(',')
        return (rua[0], 0)
    else:
        rua = numero = ''
        try:
            result_number = regex.search(r"(\d+)", endereco)
            numero = result_number.group(0)
            numero = numero.replace(', ', '')
            rua = endereco.split(',')
        except Exception as e:
            print(f"Endereco: {endereco}\n Error: {e}")
    return (rua[0], numero)


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

    (rua, numero) = reconheceEndereco(endereco)

    return (rua, numero, bairro, bairro, "Ponta Grossa/PR")


def rmBairroCidade(endereco):
    return regex.sub(r"([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*?)(\s?-?)([A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ ]*)( - )", '', endereco)


def buscaRuaPG(endEncontrado):

    if "Ponta Grossa/PR" not in endEncontrado:
        return (0, "")

    endSemCidade = endEncontrado.replace('Ponta Grossa/PR', '')

    if not endSemCidade:
        return(0, "")

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

    r = session.get(
        'https://www.conceitoimoveispg.com.br/busca/venda/cidade_ponta-grossa')
    soup = BeautifulSoup(r.text, 'html.parser')

    npag = cleanhtml(str(soup.select(
        'body > div.section.toSell > div > div.searchResults.searchResults3Col > div.paginacao > ul > li:nth-child(6) > a')))
    npag = npag.replace('[', '')
    npag = npag.replace(']', '')
    n = int(int(npag) / 4)

    thread1 = threading.Thread(target=imovel, args=(1, n))
    thread2 = threading.Thread(target=imovel, args=(n + 1, 2 * n))
    thread3 = threading.Thread(target=imovel, args=(2 * n + 1, 3 * n))
    thread4 = threading.Thread(target=imovel, args=(3 * n + 1, int(npag)))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

    return anuncios
