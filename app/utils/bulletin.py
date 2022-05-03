from datetime import datetime, timedelta
import pandas as pd
import requests
from csv import writer
import json
import xml.etree.ElementTree as ET
import sys


class Bulletin():
    "Défintion d'un bulletin risque avalanche"
    def __init__(self, massif, jour):
        self.massif = massif
        self.jour = jour
        self.url = "https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA"

    @property
    def jour_key(self):
        return self.jour[0:4] + '-' + self.jour[4:6] + '-' + self.jour[6:8]

    def download(self):
        r = requests.get(f'{self.url}.{self.massif}.{self.jour}.xml')
        # print(f'{self.url}.{self.massif}.{self.jour}.xml')
        with open('app/tmp/bera.xml', 'wb') as f:
            f.write(r.content)

    def parse(self):
        root = ET.parse('app/tmp/bera.xml').getroot()
        self.cartouche_risque = root[0].find('CARTOUCHERISQUE')
        self.risques = self.cartouche_risque[0].attrib

    def append_csv(self):
        return [self.jour_key, self.massif, *self.risques.values()]


if __name__ == '__main__':
    if len(sys.argv) == 3:
        massif = sys.argv[1]
        jour = sys.argv[2]
        bul = Bulletin(massif, jour)
        bul.download()
        bul.parse()
        new_content = bul.append_csv()
    else:
        print("Please enter massif and datetime of publication")
