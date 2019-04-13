try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from Ruas import *
from colour import Color

import geopy.distance
import configparser
import pyexcel
import numpy as np
from scipy.stats import dweibull


from matplotlib import pyplot as plt
import networkx as nx

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False

#-------------------------------VARIAVEIS GLOBAIS E ETC.-----------------------------------------
Config = configparser.ConfigParser()
Config.read("config.ini")
cOfficeLat = ConfigSectionMap('office')['lat']
cOfficeLon = ConfigSectionMap('office')['lon']


#fig, ax = plt.subplots()

#fig2, ab = plt.subplots()

fig3, aCmin = plt.subplots()

contaFig = 0

tree = ET.ElementTree(file='Xmls/formiga.xml')
root = tree.getroot()

potsaida = float(ConfigSectionMap('office')['potsaida'])
cOfficeID = -1

enableMatPlot = True
esqMax = int(ConfigSectionMap('constantes')['esquinamax']) - 1
colors = (list(Color('red').range_to(Color('blue'), esqMax+1)))

plt.rcParams['figure.figsize'] = (16, 9)
plt.style.use('ggplot')

distanciaTeste = 500

G = nx.Graph()

todosClusters = []

#----------------------------------------------------------------------------------------------

def isnumber(value):
    try:
         float(value)
    except ValueError:
         return False
    return True

def ordenaLista(lista):
    listAux = lista
    listaOrd = []
    for x in sorted(listAux, key=lambda name: listAux[name].getDistAnt()):
        listaOrd.append(listAux[x])
    return listaOrd

def distanciaPtos(pto1, pto2):

    coords_1 = (pto1.getLat(), pto1.getLon())
    coords_2 = (pto2.getLat(), pto2.getLon())

    return geopy.distance.geodesic(coords_1, coords_2).m

def distancia(lat1, lon1, lat2, lon2):

    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)

    return geopy.distance.geodesic(coords_1, coords_2).m

def calculaTamRua(street):
    pont = street.getPtos()
    cont = 0
    tamanhoRua = 0
    priPont = pont[0]
    for x in pont:
        if cont == 0:
            priPont = x
            cont = 1
        else:
            segPont = x
            tamanhoRua = tamanhoRua + distanciaPtos(priPont, segPont)
            priPont = segPont

    return tamanhoRua

def caminhoMinimo(idPto1, idPto2):
    caminho = nx.dijkstra_path(G, source=idPto1, target=idPto2)
    #caminho = nx.shortest_path(G, source=idPto1, target=idPto2)
    anterior = caminho[0]
    total = 0
    contCam = 0
    for a in caminho:
        if contCam != 0:
            total += distancia(pontos[a].getLat(), pontos[a].getLon(), pontos[anterior].getLat(),
                                  pontos[anterior].getLon())
            anterior = a
        else:
            contCam = 1

    return total


def removeRuasRep(ruas):
    ruas_ordenadas = sorted(ruas, key=Ruas.getNome)
    ruasRemover = dict()
    teveIgual = True

    ruaAnt = ruas_ordenadas[0]
    ruasRemover[ruaAnt.getNome()] = []
    ruasRemover[ruaAnt.getNome()].append(ruaAnt)

    ruasIter = iter(ruas_ordenadas)
    next(ruasIter)
    for x in ruasIter:
        if x.getNome() != ruaAnt.getNome():
            del(ruasRemover[x.getNome()])

        else:
            ruasRemover[x.getNome()].append(x)

    return ruasRemover

#----------------------------------------------------------------------------------------
#-----------------------------REMOVE ROTÁTORIAS E SINAIS---------------------------------
#----------------------------------------------------------------------------------------

remover = []

for child_of_root in root:
    if child_of_root.tag == 'node':
        remover.append(child_of_root)
    if child_of_root.tag == 'way':
        break

for x in remover:
    root.remove(x)

tree.write('output.xml')

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
#-------------------CRIA E PREENCHE O DICIONARIO DE PONTOS-------------------------------
#----------------------------------------------------------------------------------------

pontos = dict()
listaIdPtos = []

auxPrim = 0
menorDist = 20000

for child_of_root in root:
    if child_of_root.tag == 'node':
        ptoAux = Pontos()
        ptoAux.setId(child_of_root.attrib['id'])
        ptoAux.setLat(child_of_root.attrib['lat'])
        ptoAux.setLon(child_of_root.attrib['lon'])

        if distancia(ptoAux.getLat(), ptoAux.getLon(), cOfficeLat, cOfficeLon) <= distanciaTeste:
            pto = Pontos()
            ptoVert = Pontos()
            pto = ptoAux
            pontos[child_of_root.attrib['id']] = pto
            listaIdPtos.append(child_of_root.attrib['id'])

            if distancia(ptoAux.getLat(), ptoAux.getLon(), cOfficeLat, cOfficeLon) < menorDist:
                menorDist = distancia(ptoAux.getLat(), ptoAux.getLon(), cOfficeLat, cOfficeLon)
                cOfficeID = child_of_root.attrib['id']

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
#------------------------CRIA A LISTA DE RUAS E ESCREVE NO XML---------------------------
#----------------------------------------------------------------------------------------

ruas = []
contGrap = 0
for child_of_root in root:
    if child_of_root.tag == 'way':
        rua = Ruas()
        rua.setId(child_of_root.attrib['id'])
        tuplaRua = [] #lista de tuplas com latitude e longitude dos pontos das ruas

        ptoAtual = Pontos()
        ptoAnt = Pontos()
        for child_child in child_of_root:
            if child_child.tag == 'nd':
                try:
                    ptoAtual = pontos[child_child.attrib['ref']]
                    rua.setPto(ptoAtual)
                    pontos[child_child.attrib['ref']].incEsq()
                    tuplaRua.append((ptoAtual.getLat(), ptoAtual.getLon()))

                    if ptoAnt.getId() != -1:
                        pontos[child_child.attrib['ref']].setLiga(ptoAnt)

                    ptoAnt = ptoAtual


                except Exception:
                    continue

            if child_child.tag == 'tag':
                if child_child.attrib['k'] == 'name':
                    rua.setNome(child_child.attrib['v'])

        if len(rua.getPtos()) != 0:
            rua.setTamRua(calculaTamRua(rua))
            ruas.append(rua)

ruas_ordenadas = sorted(ruas, key = Ruas.getTamRua, reverse=True)

remove = []
nomesRuas = []
tamanhoRuas = []
demandaRuas = []
idRuas = []

for x in ruas_ordenadas:
    if (x.getTamRua() == 0) or (x.getNome() == ''):
        remove.append(x)

for x in remove:
    ruas_ordenadas.remove(x)

#ruasRetirar = removeRuasRep(ruas_ordenadas)
#for x in ruasRetirar:
#    print("Rua repetida : ")
#    for y in x:
#        print(y.getNome())

i = 0
for x in ruas_ordenadas:
    np.random.weibull(5.)
    #print('Nome :' + x.getNome() + ', Tamanho da rua : ' + str(x.getTamRua()))
    idRuas.append(x.getId())
    nomesRuas.append(x.getNome())
    #tamanhoRuas.append(str(x.getTamRua()))
    demandaRuas.append(int(np.ceil((np.random.weibull(5.)*x.getTamRua()/20))))

dicionarioExcel = {
    #"Tamanho da Rua": tamanhoRuas,
    "Demanda" : demandaRuas,
    "ID" : idRuas,
    "Nome da Rua": nomesRuas,
}

for x in dicionarioExcel:
    print(x)
    print(dicionarioExcel[x])

sheet = pyexcel.get_sheet(adict=dicionarioExcel)
sheet.save_as("demanda.csv")

#sheet = pyexcel.get_sheet(file_name='demanda.csv')
#for row in sheet:
#    print("%s: %s" % (row[0], row[1]))