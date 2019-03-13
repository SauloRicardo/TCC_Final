class Central(object):

    def __init__(self):
        self.cOfficeLat = []
        self.cOfficeLon = []
        self.cOfficeID = 0

    def setcOfficeLat(self, lat):
        self.cOfficeLat = lat

    def getcOfficeLat(self):
        return self.cOfficeLat

    def setcOfficeLon(self, lon):
        self.cOfficeLon = lon

    def getcOfficeLon(self):
        return self.cOfficeLon

    def setcOfficeID(self, id):
        self.cOfficeID = id

    def getcOfficeID(self):
        return self.cOfficeID