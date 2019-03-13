#Classe para cadastro das ruas

from PontosRuas import *

class Ruas(object):

    def __init__(self):
        self.__id = 0
        self.__nome = ''
        self.__ptos = []
        self.__tamRua = 0

    def setId (self, id):
        self.__id = id

    def setNome (self, nome):
        self.__nome = nome

    def setPto (self, ponto):
        self.__ptos.append(ponto)

    def setTamRua (self, tamRua):
        self.__tamRua = tamRua

    def getId(self):
        return self.__id

    def getNome(self):
        return self.__nome

    def getPtos(self):
        return self.__ptos

    def getTamRua(self):
        return self.__tamRua