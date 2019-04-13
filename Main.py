try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from Ruas import *
from ClusteringFunctions import *

from copy import deepcopy
from colour import Color

import time

import gmplot
import operator
import random
import numpy as np
import geopy.distance
import scipy
import Central
import pyexcel

from matplotlib import pyplot as plt
import matplotlib.lines as mlines
import networkx as nx

import configparser # Arquivo de Configuração
#import io

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

divisor1_2 = float(ConfigSectionMap('equipamentos')['divisor1_2'])
divisor1_4 = float(ConfigSectionMap('equipamentos')['divisor1_4'])
divisor1_8 = float(ConfigSectionMap('equipamentos')['divisor1_8'])
divisor1_16 = float(ConfigSectionMap('equipamentos')['divisor1_16'])
divisor1_32 = float(ConfigSectionMap('equipamentos')['divisor1_32'])
divisor1_64 = float(ConfigSectionMap('equipamentos')['divisor1_64'])
conector = float(ConfigSectionMap('equipamentos')['conector'])
emendaFusao = float(ConfigSectionMap('equipamentos')['emendafusao'])

mono_1300 = float(ConfigSectionMap('cabo')['mono_1300'])
mono_1310 = float(ConfigSectionMap('cabo')['mono_1310'])
mono_1550 = float(ConfigSectionMap('cabo')['mono_1550'])

'''central = Central()
central.setcOfficeLat(cOfficeLat)
central.setcOfficeLon(cOfficeLon)
central.setcOfficeID(-1)'''

enableGplot = str_to_bool(ConfigSectionMap('boolean')['gplot'])
enableGrafoPlot = str_to_bool(ConfigSectionMap('boolean')['desenhagrafo'])
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

def calculaTamRua(rua):
    pont = rua.getPtos()
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

def desenhaCaminhoMin(idPto1, idPto2, cor, num):
    caminho = nx.dijkstra_path(G, source=idPto1, target=idPto2)
    anterior = 0
    if len(caminho) > 0:
        aCmin.scatter(pontos[caminho[0]].getLat(), pontos[caminho[0]].getLon(), marker='x', s=0.5, c=cor)
        #gmap.scatter(pontos[caminho[0]].getLat(), pontos[caminho[0]].getLon(), '#3B0B39', size=1, marker='x')
        for i in caminho:
            if anterior == 0:
                anterior = i
            else:
                aCmin.add_line(mlines.Line2D([pontos[i].getLat(), pontos[anterior].getLat()],
                                          [pontos[i].getLon(), pontos[anterior].getLon()], linewidth = 2, c=cor))

                #gmap.directions_layer([pontos[i].getLat(), pontos[anterior].getLat()], [pontos[i].getLon(), pontos[anterior].getLon()], 'cornflowerblue', edge_width=3)

                if i == caminho[len(caminho)-1]:
                    aCmin.scatter(pontos[i].getLat(), pontos[i].getLon(), marker='o', s=5, c=cor)
                    #aCmin.annotate(str(num), xy=(pontos[i].getLat(), pontos[i].getLon()), fontsize = 'xx-small')

                anterior = i

def calculaAtenua(compCabo, perdaCabo, numConect, perdaConect, numEmenda, perdaEmenda, perdaDivisor):

    atenuacao = compCabo*perdaCabo + numConect*perdaConect + numEmenda*perdaEmenda + perdaDivisor

    return atenuacao

def clusterForcaBrutaDemanda(ptosOrd, ruasSR, idRuasSR):
    todasRuasAtendidas = []
    global contaFig
    contaFig = 0
    ptosLocal = ptosOrd
    ruasLocal = ruasSR
    idRuasLocal = idRuasSR

    while ptosLocal[0].getDistCOffice() == -1:
        del ptosLocal[0]

    while len(ptosLocal) > 0:
        qtdAnt = len(ptosLocal)
        ruasEsquina = []
        ruasAtendidas = []
        demandaTotal = 0

        nx.draw_networkx(G, node_size = 0.5, node_color = 'grey', alpha = 0.5, with_labels = False, pos = posPontos)
        contEsq = 0
        #ptoIni = ptosLocal.pop(0)
        #desenhaCaminhoMin(ptoIni.getId(), cOfficeID, colors[0].get_hex_l(), 0)

        '''
        for x in idRuasLocal:
            if ptoIni in ruasLocal[x].getPtos():
                ruasEsquina.append(ruasLocal[x])

        for k in ruasEsquina:
            demandaTotal += k.getDemanda()
            if demandaTotal > 128:
                demandaTotal -= k.getDemanda()
            else:
                todasRuasAtendidas.append(k.getNome())
                ruasAtendidas.append(k)
        
        #print("ANTES")
        #print(len(ptos))
        for k in ruasAtendidas: # NAO É n^3
            del ruasLocal[k.getNome()]
            for ids in idRuasLocal:
                if ids == k.getNome():
                    idRuasLocal.remove(ids)
            for p in k.getPtos():
                if p.getEsq() > 1:
                    for q in ptosLocal:
                        if p.getId() == q.getId():
                            ptosLocal.remove(q)
        #print("DEPOIS")
        #print(len(ptos))

        for x in ptosLocal:
            x.setDistAnt(caminhoMinimo(x.getId(), ptoIni.getId()))

        ptosLocal = sorted(ptosLocal, key = Pontos.getDistAnt)
        '''

        while contEsq < esqMax and contEsq < len(ptosLocal):
            ptosRemover = []
            ruasEsquina = []
            ruasAtendidas = []
            demandaTotal = 0

            #tamCabo = ptoIni.getDistCOffice() + caminhoMinimo(ptoIni.getId(), ptosLocal[contEsq].getId())
            tamCabo = caminhoMinimo(cOfficeID, ptosLocal[contEsq].getId())

            atenuacao = calculaAtenua(tamCabo/1000, mono_1310, 2, conector, 6, emendaFusao, (divisor1_16 + divisor1_4))
            if tamCabo < 20000 and atenuacao < potsaida:
                #print("Distancia da esquina " + str(contEsq) + " eh : " +
                #     str(tamCabo) + "e a atenuacao eh : " + str(atenuacao))

                desenhaCaminhoMin(cOfficeID, ptosLocal[contEsq].getId(), colors[contEsq].get_hex_l(), contEsq + 1)
                ptosRemover.append(ptosLocal[contEsq])

                for x in idRuasLocal:
                    if ptosLocal[contEsq] in ruasLocal[x].getPtos():
                        ruasEsquina.append(ruasLocal[x])

                for k in ruasEsquina:
                    demandaTotal += k.getDemanda()
                    if demandaTotal > 128:
                        demandaTotal -= k.getDemanda()
                    else:
                        todasRuasAtendidas.append(k.getNome())
                        ruasAtendidas.append(k)

                for k in ruasAtendidas:  # NAO É n^3
                    if k.getNome() in idRuasLocal:
                        idRuasLocal.remove(k.getNome())
                    for ptoRua in k.getPtos():
                        for todosPtos in ptosLocal:
                            if ptoRua.getId() == todosPtos.getId():
                                if ptosLocal[contEsq] not in ptosRemover:
                                    ptosRemover.append(ptosLocal[contEsq])

                                #ptosLocal.remove(todosPtos)
                                break

                    del ruasLocal[k.getNome()]

                for k in ptosRemover:
                    ptosLocal.remove(k)
                contEsq += 1

        #for x in ptosLocal:
        #    x.setDistAnt(-1)

        fig3.savefig("ClustersImg/temp" + str(contaFig) + ".png", dpi=1000)
        #fig3.savefig("temp" + str(contaFig) + ".eps", format='eps', dpi=1000)
        #gmap.draw('map' + str(contaFig) + '.html')
        aCmin.cla()
        contaFig += 1


        #print("Iteracao : " + str(contaFig))
        #print ("quantidade de pontos removidos" + str(qtdAnt - len(ptosLocal)))


    #for x in sorted(todasRuasAtendidas):
    #    print(x)


def clusterForcaBrutaSplitVar(ptosOrd, ruasSR, idRuasSR):
    todasRuasAtendidas = []
    global contaFig
    contaFig = 0
    ptosLocal = ptosOrd
    ruasLocal = ruasSR
    idRuasLocal = idRuasSR
    splitterQtd = [('1/2', 0), ('1/4', 0), ('1/8', 0), ('1/16', 0), ('1/32', 0), ('1/64', 0)]
    splitterQtd = dict(splitterQtd)

    while ptosLocal[0].getDistCOffice() == -1:
        del ptosLocal[0]

    while len(ptosLocal) > 0:
        qtdAnt = len(ptosLocal)

        nx.draw_networkx(G, node_size = 0.5, node_color = 'grey', alpha = 0.5, with_labels = False, pos = posPontos)

        ptosRemover = []
        ruasEsquina = []
        ruasAtendidas = []
        sobra = 0
        splitterPrim = ''
        splitterSec  = ''

        tamCabo = caminhoMinimo(cOfficeID, ptosLocal[0].getId())

        if tamCabo < 20000:

            desenhaCaminhoMin(cOfficeID, ptosLocal[0].getId(), colors[0].get_hex_l(), 1)

            for x in idRuasLocal:
                if ptosLocal[0] in ruasLocal[x].getPtos():
                    ruasEsquina.append(ruasLocal[x])

            ruasEsquina = sorted(ruasEsquina, key=lambda name: ruas[name].getDemanda())

            #DEFINE O SPLITTER PRIMARIO E OS SECUNDARIOS ATENDE O PRIMEIRO CONJUNTO DE RUAS
            if ruasEsquina[0].getDemanda() > 64:
                splitterPrim = '1/2'
                splitterSec = '1/64'
                splitterQtd[splitterPrim] += 1
                splitterQtd[splitterSec] += 2
                ruasEsquina[0].setDemanda(ruasEsquina[0].getDemanda() - 64)
                ptosLocal.remove(ptosLocal[0])
                sobra = 0

            elif ruasEsquina[0].getDemanda() > 32:
                splitterPrim = '1/2'
                splitterSec = '1/64'
                splitterQtd[splitterPrim] += 1
                splitterQtd[splitterSec] += 2
                ruasAtendidas.append(ruasEsquina[0])
                if ruasEsquina[0].getDemanda() == 64:
                    sobra = 0
                else:
                    sobra = 64 - ruasEsquina[0].getDemanda()
                ruasEsquina.remove(ruasEsquina[0])

                for k in ruasEsquina:
                    if sobra <= 0:
                        break
                    else:
                        sobraAux = sobra
                        sobra -= k.getDemanda()
                        k.setDemanda(k.getDemanda()-sobraAux)
                        if k.getDemanda() <= 0:
                            ruasAtendidas.append(k)

            elif ruasEsquina[0].getDemanda() > 16:
                splitterPrim = '1/4'
                splitterSec = '1/32'
                splitterQtd[splitterPrim] += 1
                splitterQtd[splitterSec] += 4
                ruasAtendidas.append(ruasEsquina[0])
                if ruasEsquina[0].getDemanda() == 32:
                    sobra = 0
                else:
                    sobra = 32 - ruasEsquina[0].getDemanda()

                for k in ruasEsquina:
                    if sobra <= 0:
                        break
                    else:
                        sobraAux = sobra
                        sobra -= k.getDemanda()
                        k.setDemanda(k.getDemanda()-sobraAux)
                        if k.getDemanda() <= 0:
                            ruasAtendidas.append(k)

            elif ruasEsquina[0].getDemanda() > 8:
                splitterPrim = '1/8'
                splitterSec = '1/16'
                splitterQtd[splitterPrim] += 1
                splitterQtd[splitterSec] += 8
                ruasAtendidas.append(ruasEsquina[0])
                if ruasEsquina[0].getDemanda() == 16:
                    sobra = 0
                else:
                    sobra = 16 - ruasEsquina[0].getDemanda()

                for k in ruasEsquina:
                    if sobra <= 0:
                        break
                    else:
                        sobraAux = sobra
                        sobra -= k.getDemanda()
                        k.setDemanda(k.getDemanda()-sobraAux)
                        if k.getDemanda() <= 0:
                            ruasAtendidas.append(k)

            elif ruasEsquina[0].getDemanda() > 4:
                splitterPrim = '1/16'
                splitterSec = '1/8'
                splitterQtd[splitterPrim] += 1
                splitterQtd[splitterSec] += 16
                ruasAtendidas.append(ruasEsquina[0])
                if ruasEsquina[0].getDemanda() == 8:
                    sobra = 0
                else:
                    sobra = 8 - ruasEsquina[0].getDemanda()

                for k in ruasEsquina:
                    if sobra <= 0:
                        break
                    else:
                        sobraAux = sobra
                        sobra -= k.getDemanda()
                        k.setDemanda(k.getDemanda()-sobraAux)
                        if k.getDemanda() <= 0:
                            ruasAtendidas.append(k)

            elif ruasEsquina[0].getDemanda() > 2:
                splitterPrim = '1/32'
                splitterSec = '1/4'
                splitterQtd[splitterPrim] += 1
                splitterQtd[splitterSec] += 32
                ruasAtendidas.append(ruasEsquina[0])
                if ruasEsquina[0].getDemanda() == 4:
                    sobra = 0
                else:
                    sobra = 4 - ruasEsquina[0].getDemanda()

                for k in ruasEsquina:
                    if sobra <= 0:
                        break
                    else:
                        sobraAux = sobra
                        sobra -= k.getDemanda()
                        k.setDemanda(k.getDemanda()-sobraAux)
                        if k.getDemanda() <= 0:
                            ruasAtendidas.append(k)

            else:
                splitterPrim = '1/64'
                splitterSec = '1/2'
                splitterQtd[splitterPrim] += 1
                splitterQtd[splitterSec] += 64
                ruasAtendidas.append(ruasEsquina[0])
                if ruasEsquina[0].getDemanda() == 2:
                    sobra = 0
                else:
                    sobra = 1 - ruasEsquina[0].getDemanda()

                for k in ruasEsquina:
                    if sobra <= 0:
                        break
                    else:
                        sobraAux = sobra
                        sobra -= k.getDemanda()
                        k.setDemanda(k.getDemanda()-sobraAux)
                        if k.getDemanda() <= 0:
                            ruasAtendidas.append(k)

            for k in ruasAtendidas:  # NAO É n^3
                print(k.getNome())
                if k.getNome() in idRuasLocal:
                    idRuasLocal.remove(k.getNome())
                for ptoRua in k.getPtos():
                    for todosPtos in ptosLocal:
                        if ptoRua.getId() == todosPtos.getId():
                            if ptosLocal[0] not in ptosRemover:
                                ptosRemover.append(ptosLocal[0])
                            break
                del ruasLocal[k.getNome()]

            for k in ptosRemover:
                ptosLocal.remove(k)

            # COM OS SPLITTERS DEFINIDOS ATENDE AO CLUSTER DE RUAS RESPECTIVOS AO TIPO DE SPLITER

            if splitterPrim == '1/2':
                if k.getDemanda() > 64:
                    k.setDemanda(k.getDemanda()-64)

                elif k.getDemanda() > 32:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 16:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 8:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 4:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 2:
                    ruasAtendidas.append(k)

                else:
                    ruasAtendidas.append(k)

            elif splitterPrim == '1/4':
                if k.getDemanda() > 32:
                    k.setDemanda(k.getDemanda()-32)

                elif k.getDemanda() > 16:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 8:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 4:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 2:
                    ruasAtendidas.append(k)

                else:
                    ruasAtendidas.append(k)

            elif splitterPrim == '1/8':
                if k.getDemanda() > 16:
                    k.setDemanda(k.getDemanda()-16)

                elif k.getDemanda() > 8:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 4:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 2:
                    ruasAtendidas.append(k)

                else:
                    ruasAtendidas.append(k)

            elif splitterPrim == '1/16':
                if k.getDemanda() > 8:
                    k.setDemanda(k.getDemanda()-8)

                elif k.getDemanda() > 4:
                    ruasAtendidas.append(k)

                elif k.getDemanda() > 2:
                    ruasAtendidas.append(k)

                else:
                    ruasAtendidas.append(k)

            elif splitterPrim == '1/32':
                if  k.getDemanda() > 4:
                    k.setDemanda(k.getDemanda()-4)

                elif k.getDemanda() > 2:
                    ruasAtendidas.append(k)

                else:
                    ruasAtendidas.append(k)

            elif splitterPrim == '1/64':
                if k.getDemanda() > 2:
                    k.setDemanda(k.getDemanda()-2)

                else:
                    ruasAtendidas.append(k)

            for k in ruasAtendidas:  # NAO É n^3
                print(k.getNome())
                if k.getNome() in idRuasLocal:
                    idRuasLocal.remove(k.getNome())
                for ptoRua in k.getPtos():
                    for todosPtos in ptosLocal:
                        if ptoRua.getId() == todosPtos.getId():
                            if ptosLocal[0] not in ptosRemover:
                                ptosRemover.append(ptosLocal[0])
                            break
                del ruasLocal[k.getNome()]

            for k in ptosRemover:
                ptosLocal.remove(k)

        fig3.savefig("ClustersImg/temp" + str(contaFig) + ".png", dpi=1000)
        aCmin.cla()
        contaFig += 1


        print("Iteracao : " + str(contaFig))
        print ("quantidade de pontos removidos" + str(qtdAnt - len(ptosLocal)))


    for x in sorted(todasRuasAtendidas):
        print(x)

    print('Splitters 1/2 utilizados : ' + str(splitterQtd['1/2']))
    print('Splitters 1/4 utilizados : ' + str(splitterQtd['1/4']))
    print('Splitters 1/8 utilizados : ' + str(splitterQtd['1/8']))
    print('Splitters 1/16 utilizados : ' + str(splitterQtd['1/16']))
    print('Splitters 1/32 utilizados : ' + str(splitterQtd['1/32']))
    print('Splitters 1/64 utilizados : ' + str(splitterQtd['1/64']))


'''-----------------------------------------------------------------------------------'''
'''--Passo um Definir o limite da área do projeto e a (demanda potencial*. todo)-------'''
# DEMANDA : por enquanto será feito a estimativa com relação a quantidade de casas no local
'''-----------------------------------------------------------------------------------'''
#----------------------------------------------------------------------------------------
#-----------------------------REMOVE ROTÁTORIAS E SINAIS---------------------------------
#----------------------------------------------------------------------------------------

inicio = time.time()

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

#            Grafo.add_vertex(pto.getId())
  #          if auxPrim != 0:
 #               Grafo.add_edge()

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

'''-----------------------------------------------------------------------------------'''
'''----Passo 4 Dividir a área delimitada na quantidade de ‘células’ estimada----------'''
#PREPROCEÇAMENTO : Gerar um arquivo de configuração com a quantiade e/ou coordenadas dos pontos a serem atendidos (demanda)
'''-----------------------------------------------------------------------------------'''
#----------------------------------------------------------------------------------------
#-------------------CRIA AS TUPLAS DE LONGITUDE E LATITUDE-------------------------------
#----------------------------------------------------------------------------------------
if enableGplot:
    lat = []
    lon = []
    tuplasLatLon = []

    for x in pontos:
        tuplasLatLon.append((pontos[x].getLat(), pontos[x].getLon()))
        lat.append(pontos[x].getLat())
        lon.append(pontos[x].getLon())

    gmap = gmplot.GoogleMapPlotter(lat[0], lon[0], 13)

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
#------------------------CRIA A LISTA DE RUAS E AS PLOTA---------------------------------
#----------------------------------------------------------------------------------------

ruas = dict()
idRuas = []
contGrap = 0
for child_of_root in root:
    if child_of_root.tag == 'way':
        rua = Ruas()
        rua.setId(child_of_root.attrib['id'])
        tuplaRua = [] #lista de tuplas com latitude e longitude dos pontos das ruas

        """childcount = 0
        for child_child in child_of_root:
            if child_child.tag == 'nd':
                childcount+=1

        count = 0"""

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
            ruas[rua.getId()] = rua
            idRuas.append(child_of_root.attrib['id'])

        #if enableGplot and len(tuplaRua) != 0:
        #    ruaLat, ruaLon = zip(*tuplaRua)
        #    gmap.scatter(ruaLat, ruaLon, '#3B0B39', size=5, marker=False)
        #    gmap.plot(ruaLat, ruaLon, 'cornflowerblue', edge_width=3)

sheet = pyexcel.get_sheet(file_name='demanda.csv')

listaNomesRuas = []
sheetAux = iter(sheet)
next(sheetAux) #pula a primeira iteração da tabela que contém a palavra demanda
for row in sheetAux:
    ruas[str(row[1])].setDemanda(row[0])
    #print(ruas[str(row[1])].getNome() + 'Demanda ' +  str(ruas[str(row[1])].getDemanda()))
    if str(row[2]) not in listaNomesRuas:
        listaNomesRuas.append(str(row[2]))

print('Ruas Preenchidas com as demandas')

posPontos = dict()
for x in pontos:
    G.add_node(pontos[x].getId())
    for y in pontos[x].getLiga():
        distPtos = distancia(pontos[x].getLat(), pontos[x].getLon(), y.getLat(), y.getLon())
        G.add_edge(pontos[x].getId(), y.getId(), weight=distPtos*distPtos)

for x in nx.nodes(G):
    posPontos[x] = pontos[x].getPos()


for x in pontos:
    try:
        if pontos[x].getEsq() > 1 and caminhoMinimo(x, cOfficeID) < 20000:
            pontos[x].setDistCOffice(caminhoMinimo(x, cOfficeID))
    except:
        pass
    #print(caminhoMinimo(x, cOfficeID))

'''print(len(pontos))
print(nx.number_of_nodes(G))
print(nx.number_of_edges(G))
print(contGrap)'''

nx.draw_networkx(G, node_size = 0.5, node_color = 'grey', alpha = 0.5, with_labels = False, pos = posPontos)
plt.savefig("cidadeCompl.png", dpi=1000)
print("draw")
#plt.show()

#Teste caminhominimo grafo

#print(caminhoMinimo('1528579849', '3336645422'))

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
#-------------------------FAZ O PLOT COM O MATPLOLIB-------------------------------------
#----------------------------------------------------------------------------------------

if enableMatPlot:

    pontosOrd = []
    for x in sorted(pontos, key=lambda name: pontos[name].getDistCOffice()):
        pontosOrd.append(pontos[x])


    #ptosRem = []
    #for x in pontosOrd:
    #    if x.getEsq() > 2:
    #        ptosRem.append(x)

    #for x in ptosRem:
    #    pontosOrd.remove(x)

    pontosOrdRemove = []
    ptoAnt = Pontos()

    ruasSemRepetido = dict()
    idRuasSemRep = idRuas

    for x in idRuas:
        if ruas[x].getNome() not in ruasSemRepetido:
            ruasSemRepetido[ruas[x].getNome()] = ruas[x]

        else:
            ptosAux = ruas[x].getPtos()
            for y in ptosAux:
                if y not in ruasSemRepetido[ruas[x].getNome()].getPtos():
                    ruasSemRepetido[ruas[x].getNome()].setPto(y)

            tamanhoAux = ruasSemRepetido[ruas[x].getNome()].getTamRua() + ruas[x].getTamRua()
            ruasSemRepetido[ruas[x].getNome()].setTamRua(tamanhoAux)
            demandaAux = ruasSemRepetido[ruas[x].getNome()].getDemanda() + ruas[x].getDemanda()
            ruasSemRepetido[ruas[x].getNome()].setDemanda(demandaAux)

    #for x in sorted(listaNomesRuas):
    #    print("Nome da rua : " + ruasSemRepetido[x].getNome() + "Demanda da rua : " + str(ruasSemRepetido[x].getDemanda()))

    print("VAI COMECAR OS CLUSTER")
    #print(sorted(listaNomesRuas))
    #for x in ruasSemRepetido['Rua 13 de Maio'].getPtos():
    #    print(x.getId())
    clusterForcaBrutaSplitVar(pontosOrd, ruasSemRepetido, listaNomesRuas)

    fim = time.time()
    print("O tempo de execução foi = "+ str(fim - inicio))

    '''caminho = nx.dijkstra_path(G, source='1528579849', target='3336645422')
    print(caminho)
    anterior = 0
    if len(caminho) > 0:
        for i in caminho:
            if anterior == 0:
                anterior = i
            else:
                print('else')
                print(pontos[i].getLat())
                print(pontos[anterior].getLat())
                aCmin.add_line(mlines.Line2D([pontos[i].getLat(), pontos[anterior].getLat()],
                                             [pontos[i].getLon(), pontos[anterior].getLon()], c='r'))
                anterior = i'''

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------
#---------------------------FAZ O PLOT COM O GPLOT---------------------------------------
#----------------------------------------------------------------------------------------

if enableGplot:
    drawLat, drawLon = zip(*tuplasLatLon)
    gmap.scatter(drawLat, drawLon,  '#3B0B39', size=5, marker=False)
    gmap.draw('map.html')

#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------
'''-----------------------------------------------------------------------------------'''
'''-----------------------------------------------------------------------------------'''
'''-----------------------------------------------------------------------------------'''


#todo Passo 2 Definir a Razão de Divisão do projeto: 1:32 / 1:64 / 1:128.

#todo Passo 3 Definir a Topologia, quais splitters e onde serão instalados. Ver Diagrama Lógico.


#todo Passo 5 Posicionar a Caixa de Emenda (CEO) e splitters de primeiro nível.

#todo Passo 6 Desenhar as rotas da Rede Primária ( cabos ‘Feeder’) e planejar
#todo  a quantidade de fibras em cada trecho, tanto de fibras ativas quanto reserva
#todo  para expansões. Lembre de considerar o planejamento para o futuro.

#todo Passo 7 Posicionar as Caixas Terminais (CTO) e desenhar as rotas da
#todo  rede secundária ou distribuição. Esta fase ocorre sob demanda.