import finders.findImConceito as findImConceito
import finders.findTavarnaro as findTavarnaro
import finders.findProcureImovel as findProcureImovel

import json

anuncios = []
def write_JSON():
    with open('./output/anuncios.json', 'w') as f:
        json.dump(anuncios, f, indent=4, ensure_ascii=False)

def main():
    anunciosConceito = findImConceito.main(9)
    for anuncio in anunciosConceito:
        anuncios.append(anuncio)
    write_JSON()    

    anunciosTavarnaro = findTavarnaro.main(98)
    for anuncio in anunciosTavarnaro:
        anuncios.append(anuncio)
    write_JSON()

    anunciosProcureImovel = findProcureImovel.main(220)
    for anuncio in anunciosProcureImovel:
        anuncios.append(anuncio)
    write_JSON()

if __name__ == '__main__':
    main()