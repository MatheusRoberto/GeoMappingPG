# Algoritmos para extração e posicionamento geografico de anúncios de imoveis na cidade de Ponta Grossa - PR
___
## Descrição

Todos os algoritmos foram elaborados em Python e algumas bibliotecas:
* [request](http://docs.python-requests.org/pt_BR/latest/)
* [regex](https://docs.python.org/3/library/re.html)
* [fuzzywuzzy](https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/)
* [JSON](http://json.org)
* [GeoPy](https://geopy.readthedocs.io/en/stable/)
* [BS4] (https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
___
API:
* [Geocoding API](https://developers.google.com/maps/documentation/geocoding/start)
### BuscaImoveis.py
O primeiro algoritmo foi elaborado para extração de anuncios de alguns sites de algumas imobiliárias de Ponta Grossa/PR:
* [Conceito Imóveis](https://www.conceitoimoveispg.com.br) 
* [Procure Imóvel](https://procureimovel.com.br/) 
* [Tavarnaro](https://www.tavarnaroconsultoria.com.br/) 

Utilizando [request](http://docs.python-requests.org/pt_BR/latest/) para acesso á página principal com todos anúncios, onde para cada anúncio é realizado um acesso á pagina, encontra tags no HTML para extração da localidade e valor do anúncio do imovél. 
Após está extração utilizando de [regex](https://docs.python.org/3/library/re.html), é extraido valor e informações da localidade do anúncio, como:
* Logradouro
* Número
* Bairro
* Cidade

Com essas informações, é feito o uso de outra biblioteca [fuzzywuzzy](https://chairnerd.seatgeek.com/fuzzywuzzy-fuzzy-string-matching-in-python/) para comparar o logradouro encontrado no anúncio do site com uma lista logradouros da cidade de Ponta Grossa/PR, se no anúncio encontrado não tiver compatilidade com os logradouros da cidade, o mesmo é descartado.
Após o processamento de todas ás paginas do site da imobiliária, é gerado um objeto Anuncio com as informações: 
* Endereço encontrado no anúncio,
* Rua¹,
* Número¹, 
* Bairro¹,
* Cidade¹,
* Preço do anúncio,
* Endereço de *match* com a lista de logradouros

**¹** Todas estas informações foram retirada do endereço extraído do site do anúncio, utilizando o [regex](https://docs.python.org/3/library/re.html).

O endereço *match* é utlizado para conferênia que o endereço do anúncio é o mesmo da lista de logradouros da cidade

Após está estruturação é salva num arquivo [JSON](http://json.org) com nome de [anunciosGeo.json](./anunciosGeo.json) para utilização em outro algoritmo [mapAnuncio.py](./mapAnuncio.py)

___

### mapAnuncio.py

O segundo algoritmo foi elaborado para ler o arquivo [JSON](http://json.org) resultado do [buscaImoveis.py](./buscaImoveis.py), utilizando a biblioteca [GeoPy](https://geopy.readthedocs.io/en/stable/) ele pega o endereço encontrado de cada anúncio, utiliza API [Geocoding API](https://developers.google.com/maps/documentation/geocoding/start) para encontrar a **latitude e longitude**
do endereço encontrado no anúncio. Após processar todos os anuncios ele salva em um arquivo [JSON](http://json.org) com nome de [anunciosGeo.json](./anunciosGeo.json) para processamento de um terceiro algoritmo [mapppingAnuncio.py](./mappingAnuncio.py)

___

### MappingAnuncio.py
O terceiro algoritmo também elaborado para leitura de arquivo [JSON](http://json.org) resultado do [mapAnuncio.py](./mapAnuncio.py), utilizando a biblioteca [folium](https://python-visualization.github.io/folium/docs-v0.6.0/) utilizando o mapa da cidade de  Ponta Grossa/PR, com a leitura do arquivo, ocorre uma ordenação dos anúncios conforme os valores do anúncio, divide em grupos em uma faixa de valor e verifica as coordenadas geográficas e adiciona ao mapa de Ponta Grossa/PR, após a inserção de todos os anúncios é gerado um [index.html](./index.html) com o mapa de Ponta Grossa/PR com todos os anúncios e cores referente aos seus grupos e valores

____

## Requisitos instalação

Instale o [pip](https://pip.pypa.io/en/stable/installing/) para adicionar as bibliotecas:

```bash
pip install fuzzywuzzy
```
```bash
pip install requests-html
```
```bash
pip install geopy
```
```bash
pip install folium
```
```bash
pip install bs4
```
____

## Utilizando os programas

O arquivo geoMapping.py tem script para rodar algoritmo de Scraping e Georreferenciação **Neste algortimo é necessário uma key para utilizar API do Google [Geocoding API](https://developers.google.com/maps/documentation/geocoding/start):
```bash
cd venda
```
```bash
python geoMapping.py
```

E por fim utilizamos o ultimo algoritmo para criar um mapa com todos os anuncios georreferenciados da cidade de Ponta Grossa - Paraná:
```bash
python mappingAnuncio.py
```
____

## Autores
* [Matheus Roberto](https://github.com/MatheusRoberto) <matheroberto@gmail.com>
* [Pedro Magnus](https://github.com/magnuspedro) <pedmagnus@gmail.com>

