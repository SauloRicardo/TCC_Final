class Cluster(object):

    def __init__(self):
        self.centroid = []
        self.esquina = []
        self.quantEsq = 0

    def setCentroid(self, lat, lon):
        self.centroid = [lat, lon]

    def getCentroid(self):
        return self.centroid

    def setEsquinas(self, esq):
        self.esquina.append(esq)
        self.quantEsq = self.quantEsq + 1

    def getEsquinas(self):
        return self.esquina

    def getQuantEsquinas(self):
        return self.quantEsq