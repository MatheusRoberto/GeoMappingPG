import threading
import json
import re as regex
import difflib
from requests_html import HTMLSession
from datetime import datetime
from fuzzywuzzy import fuzz

session = HTMLSession()

anuncios = []
logradouros = []


class Anuncio:
    def __init__(self, end, rua, numero, bairro, cidade, valor, endMath):
        self.endereco = end
        self.logradouro = rua
        self.bairro = bairro
        self.cidade = cidade
        self.valor = valor
        now = datetime.now()
        self.data = '{:%d/%m/%Y}'.format(now)
        if numero != 0:
            self.numero = numero
        self.enderecoMatch = endMath

    def toJSON(self):
        return json.dumps(self, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def valorAnuncio(preco):
    resultado = regex.findall(
        '(?:[1-9](?:[\d]{0,2}(?:\.[\d]{3})*|[\d]+)|0)(?:,[\d]{0,2})?', preco)
    x = []
    if not resultado:
        return float(0.00)
    for r in resultado:
        value = r.replace('.', '')
        value = value.replace(',', '.')
        x.append(float(value))
    return max(x, key=float)


def estruturandoEndereco(endereco):

    result = regex.search('(\w*? )*(\w*)( - )(Ponta Grossa/PR)', endereco)
    bairro = result.group(0)
    bairro = bairro.replace(' - Ponta Grossa/PR', '')

    print('Estruturando: ' + "s/n" in endereco)

    if "s/n" in endereco:
        rua = endereco.split(',')
        return (rua[0], 0, bairro, "Ponta Grossa/PR")
    else:
        result_number = regex.search('(\d+)', endereco)
        numero = result_number.group(0)
        numero = numero.replace(', ', '')
        rua = endereco.split(',')
        return (rua[0], numero, bairro, "Ponta Grossa/PR")


def carregaLogradouros():
    with open('./files/logradouros.txt', 'r', encoding="ISO-8859-1") as f:
        for line in f:
            logradouros.append(line)


def listLogradouros():
    for rua in logradouros:
        print(rua)


def rmBairroCidade(endereco):
    return regex.sub('( - (\w*? )*(\w*)/)(\w*? )*(\w*)( - )(Ponta Grossa/PR)', '', endereco)


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
    print("Maior valor: %d" % n_max)
    print("Indice: %d" % n_pos)
    print("Rua: %s" % logradouros[n_pos])
    print("Rua encontrada: %s" % endEncontrado)

    print("-----------------------------")

    return (n_max, logradouros[n_pos])


def imovel(i, j):
    while (i <= j):
        r = session.get(
            f"https://www.conceitoimoveispg.com.br/busca/venda/cidade_ponta-grossa/pag_{i}")

        data = r.html.absolute_links

        for d in data:

            if d == 'tel:+554230251818':
                continue

            re = session.get(d)

            end = re.html.find('.imovelTitle .fa', first=True)
            preco = re.html.find('.price', first=True)
            if end is None:
                print("erro")

            print(d)
            if end and preco:
                precoAnuncio = valorAnuncio(preco.text)
                print(r.status_code)
                (pont, endMatch) = buscaRuaPG(end.text)
                if precoAnuncio > 0 and pont >= 40:
                    (rua, numero, bairro, cidade) = estruturandoEndereco(end.text)
                    anuncio = Anuncio(end.text, rua, numero,
                                      bairro, cidade, precoAnuncio, endMatch)
                    anuncios.append(json.loads(anuncio.toJSON()))
        if r.status_code == 200:
            i += 1
    # print(r.status_code)
    print(i)

def main(npag):

    carregaLogradouros()

    n = int(npag / 4)

    thread1 = threading.Thread(target=imovel, args=(1, n))
    thread2 = threading.Thread(target=imovel, args=(n+1, 2*n))
    thread3 = threading.Thread(target=imovel, args=(2*n+1, 3*n))
    thread4 = threading.Thread(target=imovel, args=(3*n+1, 4*n))

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

    return anuncios

