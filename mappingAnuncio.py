import folium
import json
import locale

anuncios = {}
anunciosGeo = []
color = ['#00a7ff',
         '#1F78B4',
         '#B2DF8A',
         '#063A03',
         '#FB9A99',
         '#E31A1C',
         '#FDBF6F',
         '#FF7F00',
         '#CAB2D6',
         '#6A3D9A',
         '#7C5843',
         '#742900']


def open_JSON():
    global anuncios
    with open('./output/anunciosGeo.json') as f:
        anuncios = json.load(f)


def addPoint(anuncio, m):
    ltdlng = anuncio['geoLocation']
    folium.Circle(
        location=ltdlng,
        radius=25,
        popup=anuncio['endereco'],
        tooltip=anuncio['valor'],
        color=anuncio['cor']
    ).add_to(m)

def addPointGroup(anuncio, m, group):
    ltdlng = anuncio['geoLocation']
    folium.CircleMarker(
        location=ltdlng,
        radius=25,
        popup=anuncio['link'],
        tooltip=anuncio['endereco'],
        color=anuncio['cor']
    ).add_to(group)

def entreNumbers(li, ls, n):
    return (n >= li and n <= ls)

def colorAnuncio():
    valores = []

    n = int(len(anunciosGeo) / 12)

    valores.append(0)
    inc = n
    for i in range(0, 12):
        valores.append(inc)
        if(inc < len(anunciosGeo)):
            valores.append(inc + 1)
        else:
            break
        inc += n

    for i in range(0, len(anunciosGeo)):
        if(entreNumbers(valores[0], valores[1], i)):
            anunciosGeo[i]['cor'] = color[0]

        if(entreNumbers(valores[2], valores[3], i)):
            anunciosGeo[i]['cor'] = color[1]

        if(entreNumbers(valores[4], valores[5], i)):
            anunciosGeo[i]['cor'] = color[2]

        if(entreNumbers(valores[6], valores[7], i)):
            anunciosGeo[i]['cor'] = color[3]

        if(entreNumbers(valores[8], valores[9], i)):
            anunciosGeo[i]['cor'] = color[4]

        if(entreNumbers(valores[10], valores[11], i)):
            anunciosGeo[i]['cor'] = color[5]

        if(entreNumbers(valores[12], valores[13], i)):
            anunciosGeo[i]['cor'] = color[6]

        if(entreNumbers(valores[14], valores[15], i)):
            anunciosGeo[i]['cor'] = color[7]

        if(entreNumbers(valores[16], valores[17], i)):
            anunciosGeo[i]['cor'] = color[8]

        if(entreNumbers(valores[18], valores[19], i)):
            anunciosGeo[i]['cor'] = color[9]

        if(entreNumbers(valores[20], valores[21], i)):
            anunciosGeo[i]['cor'] = color[10]

        if(entreNumbers(valores[22], valores[23], i)):
            anunciosGeo[i]['cor'] = color[11]

def matchValor(x):
    return x['valor']

def minValor(x):
    valor = []
    for anuncio in x:
        valor.append(anuncio['valor'])
    
    return min(valor, key=float)

def maxValor(x):
    valor = []
    for anuncio in x:
        valor.append(anuncio['valor'])
    
    return max(valor, key=float)

def moeda(valor):
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    valor = locale.currency(valor, grouping=True, symbol=None)
    return valor

def main():
    open_JSON()

    m = folium.Map(location=[-25.0945, -50.1633], zoom_start=12)

    folium.TileLayer('cartodbpositron').add_to(m)
    folium.TileLayer('stamentoner').add_to(m)
    folium.TileLayer('openstreetmap').add_to(m)

    for anuncio in anuncios:
        an = {'endereco': anuncio['endereco'], 'valor': (float(anuncio['valor'])),
              'geoLocation': anuncio['geoLocation'], 'cor': '', 'link': anuncio['link']}
        anunciosGeo.append(an)

    anunciosGeo.sort(key=matchValor)

    colorAnuncio()

    valor = []

    azulClaro  = list(filter(lambda x: x['cor'] == '#00a7ff', anunciosGeo))
    #print(minValor(azulClaro), maxValor(azulClaro))
    group0 = folium.FeatureGroup(
        name='<span style=\\"color: #00a7ff;\\"> De: R$'+
            moeda(minValor(azulClaro))+' a R$'+moeda(maxValor(azulClaro))+'</span>')
    for anuncio in azulClaro:
        addPointGroup(anuncio, m, group0)
        valor.append(float(anuncio['valor']))

    azulEscuro  = list(filter(lambda x: x['cor'] == '#1F78B4', anunciosGeo))
    group1 = folium.FeatureGroup(
        name='<span style=\\"color: #1F78B4;\\"> De: R$'+
            moeda(minValor(azulEscuro))+' a R$'+moeda(maxValor(azulEscuro))+'</span>')
    for anuncio in azulEscuro:
        addPointGroup(anuncio, m, group1)
        valor.append(float(anuncio['valor']))

    verdeClaro  = list(filter(lambda x: x['cor'] == '#B2DF8A', anunciosGeo))
    group2 = folium.FeatureGroup(
        name='<span style=\\"color: #B2DF8A;\\"> De: R$'+
            moeda(minValor(verdeClaro))+' a R$'+moeda(maxValor(verdeClaro))+'</span>')
    for anuncio in verdeClaro:
        addPointGroup(anuncio, m, group2)
        valor.append(float(anuncio['valor']))

    verdeEscuro  = list(filter(lambda x: x['cor'] == '#063A03', anunciosGeo))
    group3 = folium.FeatureGroup(
        name='<span style=\\"color: #063A03;\\"> De: R$'+
            moeda(minValor(verdeEscuro))+' a R$'+moeda(maxValor(verdeEscuro))+'</span>')
    for anuncio in verdeEscuro:
        addPointGroup(anuncio, m, group3)
        valor.append(float(anuncio['valor']))

    vermelhoClaro  = list(filter(lambda x: x['cor'] == '#FB9A99', anunciosGeo))
    group4 = folium.FeatureGroup(
        name='<span style=\\"color: #FB9A99;\\"> De: R$'+
            moeda(minValor(vermelhoClaro))+' a R$'+moeda(maxValor(vermelhoClaro))+'</span>')
    for anuncio in vermelhoClaro:
        addPointGroup(anuncio, m, group4)
        valor.append(float(anuncio['valor']))

    vermelhoEscuro  = list(filter(lambda x: x['cor'] == '#E31A1C', anunciosGeo))
    group5 = folium.FeatureGroup(
        name='<span style=\\"color: #E31A1C;\\"> De: R$'+
            moeda(minValor(vermelhoEscuro))+' a R$'+moeda(maxValor(vermelhoEscuro))+'</span>')
    for anuncio in vermelhoEscuro:
        addPointGroup(anuncio, m, group5)
        valor.append(float(anuncio['valor']))

    laranjaClaro  = list(filter(lambda x: x['cor'] == '#FDBF6F', anunciosGeo))
    group6 = folium.FeatureGroup(
        name='<span style=\\"color: #FDBF6F;\\"> De: R$'+
            moeda(minValor(laranjaClaro))+' a R$'+moeda(maxValor(laranjaClaro))+'</span>')
    for anuncio in laranjaClaro:
        addPointGroup(anuncio, m, group6)
        valor.append(float(anuncio['valor']))

    laranjaEscuro  = list(filter(lambda x: x['cor'] == '#FF7F00', anunciosGeo))
    group7 = folium.FeatureGroup(
        name='<span style=\\"color: #FF7F00;\\"> De: R$'+
            moeda(minValor(laranjaEscuro))+' a R$'+moeda(maxValor(laranjaEscuro))+'</span>')
    for anuncio in laranjaEscuro:
        addPointGroup(anuncio, m, group7)
        valor.append(float(anuncio['valor']))
    
    roxoClaro  = list(filter(lambda x: x['cor'] == '#CAB2D6', anunciosGeo))
    group8 = folium.FeatureGroup(
        name='<span style=\\"color: #CAB2D6;\\"> De: R$'+
            moeda(minValor(roxoClaro))+' a R$'+moeda(maxValor(roxoClaro))+'</span>')
    for anuncio in roxoClaro:
        addPointGroup(anuncio, m, group8)
        valor.append(float(anuncio['valor']))

    roxoEscuro  = list(filter(lambda x: x['cor'] == '#6A3D9A', anunciosGeo))
    group9 = folium.FeatureGroup(
        name='<span style=\\"color: #6A3D9A;\\"> De: R$'+
            moeda(minValor(roxoEscuro))+' a R$'+moeda(maxValor(roxoEscuro))+'</span>')
    for anuncio in roxoEscuro:
        addPointGroup(anuncio, m, group9)
        valor.append(float(anuncio['valor']))
    
    marromClaro  = list(filter(lambda x: x['cor'] == '#7C5843', anunciosGeo))
    group10 = folium.FeatureGroup(
        name='<span style=\\"color: #7C5843;\\"> De: R$'+
            moeda(minValor(marromClaro))+' a R$'+moeda(maxValor(marromClaro))+'</span>')
    for anuncio in marromClaro:
        addPointGroup(anuncio, m, group10)
        valor.append(float(anuncio['valor']))
    
    marromEscuro  = list(filter(lambda x: x['cor'] == '#742900', anunciosGeo))
    group11 = folium.FeatureGroup(
        name='<span style=\\"color: #742900;\\"> De: R$'+
            moeda(minValor(marromEscuro))+' a R$'+moeda(maxValor(marromEscuro))+'</span>')
    for anuncio in marromEscuro:
        addPointGroup(anuncio, m, group11)
        valor.append(float(anuncio['valor']))

    #print(len(valor))
    #print('Min: '+str(min(valor, key=float)))
    #print('Max: '+str(max(valor, key=float)))
    # m = folium.Map(location=[-25.0945, -50.1633], zoom_start=14)

    group0.add_to(m)
    group1.add_to(m)
    group2.add_to(m)
    group3.add_to(m)
    group4.add_to(m)
    group5.add_to(m)
    group6.add_to(m)
    group7.add_to(m)
    group8.add_to(m)
    group9.add_to(m)
    group10.add_to(m)
    group11.add_to(m)

    folium.map.LayerControl('topright', collapsed=False).add_to(m)

    m.save('./output/index.html')


if __name__ == '__main__':
    main()
