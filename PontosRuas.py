#Classe que guarda os IDs, latitudes e longitudes dos pontos que formam as ruas

class Pontos(object):

    def __init__(self):
        self.id = -1
        self.lat = 0
        self.lon = 0
        self.pos = [0,0]
        self.esq = 0
        self.demanda = 0
        self.distCOffice = -1
        self.distAnt = -1
        self.ptoLiga = []

    def setId (self, id):
        self.id = id

    def setLat (self, lat):
        self.lat = float(lat)
        self.pos[0] = float(lat)

    def setLon (self, lon):
        self.lon = float(lon)
        self.pos[1] = float(lon)

    def setLiga (self, pto):
        self.ptoLiga.append(pto)

    def incEsq (self):
        self.esq = self.esq + 1

    def setDemanda(self, demanda):
        self.demanda = demanda

    def getId(self):
        return self.id

    def getLat(self):
        return self.lat

    def getLon(self):
        return self.lon

    def getEsq(self):
        return self.esq

    def getLiga(self):
        return self.ptoLiga

    def getPos(self):
        return tuple(self.pos)

    def setDistCOffice(self, dist):
        self.distCOffice = dist

    def getDistCOffice(self):
        return self.distCOffice

    def setDistAnt(self, dist):
        self.distAnt = dist

    def getDistAnt(self):
        return self.distAnt

    def getDemanda(self):
        return self.demanda