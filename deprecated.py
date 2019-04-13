
def clusterForcaBruta(ptosOrd):
    global contaFig

    cor = random.choice(colors).get_hex_l()
    ptos = ptosOrd
    contEsq = 0
    contSp = 0
    while ptos[0].getDistCOffice() == -1:
        del ptos[0]

    for x in ptos:
        if contEsq == 0:
            try:
                desenhaCaminhoMin(ptos[contSp].getId(), cOfficeID, cor)
                contEsq += 1
            except:
                pass
        else:
            try:
                desenhaCaminhoMin(ptos[contSp].getId(), x.getId(), cor)
            except:
                pass
            # print(contEsq)
            contEsq += 1
            if contEsq == esqMax:
                contEsq = 0
                contSp += 1
                fig3.savefig("ClusterImg/temp" + str(contaFig) + ".png", dpi=fig3.dpi)
                aCmin.cla()
                contaFig += 1
                cor = random.choice(colors).get_hex_l()


def clusterForcaBrutaV2(ptosOrd):
    global contaFig
    contaFig = 0
    ptos = ptosOrd

    while ptos[0].getDistCOffice() == -1:
        del ptos[0]

    while len(ptos) > 0:
        nx.draw_networkx(G, node_size = 0.5, node_color = 'grey', alpha = 0.5, with_labels = False, pos = posPontos)
        contEsq = 0
        ptoIni = ptos.pop(0)
        desenhaCaminhoMin(ptoIni.getId(), cOfficeID, Color.get_rgb(colors[0]), 0)

        for x in ptos:
            x.setDistAnt(caminhoMinimo(x.getId(), ptoIni.getId()))

        ptos = sorted(ptos, key = Pontos.getDistAnt)

        ptosRemover = []

        print(contaFig)
        for x in ptos:
            tamCabo = ptoIni.getDistCOffice() + caminhoMinimo(ptoIni.getId(), x.getId())
            atenuacao = calculaAtenua(tamCabo/1000, mono_1310, 2, conector, 6, emendaFusao, (divisor1_16 + divisor1_4))
            if x.getDistAnt() != -1 and tamCabo < 20000 \
                    and atenuacao < potsaida: #TODO verificar saturação
                print("Distancia da esquina " + str(contEsq) + " eh : " +
                      str(tamCabo) + "e a atenuacao eh : " + str(atenuacao))

                desenhaCaminhoMin(ptoIni.getId(), x.getId(), Color.get_rgb(colors[contEsq]), contEsq + 1)
                contEsq += 1
                ptosRemover.append(x)

            if contEsq > esqMax:
                break

        '''while ptosRemover > 0:
            ptosAgrupar = []
            ptoRemoverAnt = ptosRemover[0]

            for x in ptosRemover:
                x.setDistAnt(caminhoMinimo(x.getId(), ptoRemoverAnt.getId()))

            ptosRemover = sorted(ptosRemover, key=Pontos.getDistAnt)

            for x in ptosRemover:
                if x == ptosRemover[0]:
                    pass
                else:
                    if caminhoMinimo(x.getId(), ptoRemoverAnt.getId()) < 50:
                        ptosAgrupar.append(x)

            if len(ptosAgrupar) == 1:
                ptosRemover.remove(ptoRemoverAnt)
            elif len(ptosAgrupar) >= 2 and len(ptosAgrupar) < 4:
                while len(ptosAgrupar != 2):
                    ptosAgrupar.remove(ptosAgrupar[len(ptosAgrupar-1)])'''


        for x in ptosRemover:
            ptos.remove(x)

        for x in ptos:
            x.setDistAnt(-1)

        fig3.savefig("ClustersImg/temp" + str(contaFig) + ".png", dpi=1000)
        #fig3.savefig("temp" + str(contaFig) + ".eps", format='eps', dpi=1000)
        #gmap.draw('map' + str(contaFig) + '.html')
        aCmin.cla()
        contaFig += 1
