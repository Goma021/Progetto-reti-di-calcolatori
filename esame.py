import pickle
import datetime

class Esame:
    def __init__(self, nome_esame, data_1, data_2, data_3):
        self.nome_esame = str(nome_esame)
        self.date_disponibili = [data_1, data_2, data_3]
