from pyexcel_xls import get_data
import _pickle as cPickle

class Grafo(object):

    def __init__(self,nomeArquivo):
        self.listaVertices = []
        self.listaArestas = []

    def __init__(self, idVertice, lat,lon):
        self.idVertice = idVertice
        self.lat = lat
        self.lon = lon

    def __init__(self, idAresta, verticeOrigem, verticeDestino, peso):
        self.idAresta = idAresta
        self.verticeOrigem = verticeOrigem
        self.verticeDestino = verticeDestino
        self.peso = peso

    '''def carregaGrafo(self,nomeArquivo):
        idVertice = 0
        data = get_data(nomeArquivo);
        for i in range(1,len(data["Dados"])):
            for j in range(int(data["Dados"][i][3])):
                idVertice = idVertice +1
                vertice = Vertice(idVertice,data["Dados"][i][0],data["Dados"][i][1],data["Dados"][i][2])
                self.listaVertices.append(vertice)
        self.__geraArestas()'''

    def __geraArestas(self):
        idAresta = 0
        for i in range(len(self.listaVertices)):
            turma = self.listaVertices[i].turma
            professor = self.listaVertices[i].professor
            for j in range(i, len(self.listaVertices)):
                if (turma == self.listaVertices[j].turma or professor == self.listaVertices[j].professor) and i!=j:
                    idAresta = idAresta + 1;
                    aresta = Aresta(idAresta, self.listaVertices[i], self.listaVertices[j])
                    self.listaArestas.append(aresta)


    def existeIdVertice(self,idVertice):
        for i in range(len(self.listaVertices)):
            print(self.listaVertices[i].idVertice)
            if(idVertice == self.listaVertices[i].idVertice):
                return True
        return False

    def existeIdAresta(self,idAresta):
        for i in range(len(self.listaArestas)):
            if(idAresta == self.listaArestas[i].idVertice):
                return True
        return False

    def existeAresta(self, idOrigem, idDestino):
        for i in range(len(self.listaArestas)):
            if((self.listaArestas[i].verticeOrigem.idVertice == idOrigem and self.listaArestas[i].verticeDestino.idVertice == idDestino)
            or (self.listaArestas[i].verticeOrigem.idVertice == idDestino and self.listaArestas[i].verticeDestino.idVertice == idOrigem)):
                return True
        return False

    def pegaGrauVertice(self, idVertice):
        grau = 0
        for i in range(len(self.listaArestas)):
            if(self.listaArestas[i].verticeOrigem.idVertice == idVertice):
                grau = grau +1
            if (self.listaArestas[i].verticeDestino.idVertice == idVertice):
                grau = grau + 1
        return grau

    def retornaTodosVizinhos(self, idVertice):
        listaDeVizinhos = []
        for i in range(len(self.listaArestas)):
            if(self.listaArestas[i].verticeOrigem.idVertice == idVertice):
                listaDeVizinhos.append(self.listaArestas[i].verticeDestino)
            if(self.listaArestas[i].verticeDestino.idVertice == idVertice):
                listaDeVizinhos.append(self.listaArestas[i].verticeOrigem)
        return listaDeVizinhos

    def getArestaById(self, idAresta):
        for i in range(len(self.listaArestas)):
            if self.listaArestas[i].idAresta == idAresta:
                return self.listaArestas[i]

    def getVerticeById(self, idVertice):
        for i in range(len(self.listaVertices)):
            if self.listaVertices[i].idVertice == idVertice:
                return self.listaVertices[i]


    def verificaColoracaoCorretaDosVizinhosTodosVertices(self,idVertice):
        vertice = self.getVerticeById(idVertice)
        listaVizinhos = self.retornaTodosVizinhos(idVertice)
        for i in range(len(listaVizinhos)):
            if(listaVizinhos[i].cor == vertice.cor):
                return False
        return True

    def verificaColoracaoCorretaDosVizinhos(self,idVertice,listaVizinhos):
        vertice = self.getVerticeById(idVertice)
        for i in range(len(listaVizinhos)):
            if(listaVizinhos[i].cor == vertice.cor):
                return False
        return True

    def removeArestasDoVertice(self, idVertice):
        i=0
        while i < len(self.listaArestas):
            if (self.listaArestas[i].verticeOrigem.idVertice == idVertice or self.listaArestas[i].verticeDestino.idVertice == idVertice):
                self.listaArestas.remove(self.listaArestas[i])
            else:
                i = i+1

    def removeVertice(self, idVertice):
            for i in range(len(self.listaVertices)):
                if self.listaVertices[i].idVertice == idVertice:
                    self.removeArestasDoVertice(idVertice)
                    self.listaVertices.remove(self.listaVertices[i])
                    return


    def clonarGrafo(self):
        return cPickle.loads(cPickle.dumps(self))

    def alteraCorVertice(self, idVertice, cor):
        vertice = self.getVerticeById(idVertice)
        vertice.cor = cor