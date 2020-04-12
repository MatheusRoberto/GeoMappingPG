# coding: utf-8
import findImoveis
import mapAnuncio
import addBD

import time
from datetime import datetime

def main():
    inicio = time.time()


    print('BUSCANDO ANUNCIOS')

    findImoveis.main()

    print('GEORREFERENCIADO')

    mapAnuncio.main()

    fim = time.time()
    total = fim - inicio
    total = datetime.utcfromtimestamp(total).strftime('%H:%M:%S')
    print(f'Total do algoritomo Extracao and Geo{total}')

    print('ADICIONANDO AO BANCO')

    addBD.main()
    fim = time.time()
    total = fim - inicio
    total = datetime.utcfromtimestamp(total).strftime('%H:%M:%S')
    print(f'Total do algoritomo {total}')

if __name__ == "__main__":
    main()