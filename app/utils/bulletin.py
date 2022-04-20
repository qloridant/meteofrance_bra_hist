from datetime import datetime, timedelta
import pandas as pd
import requests
from csv import writer
import json
import xml.etree.ElementTree as ET


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
        print(f'{self.url}.{self.massif}.{self.jour}.xml')
        with open('app/data/bera.xml', 'wb') as f:
            f.write(r.content)

    def parse(self):
        root = ET.parse('app/data/bera.xml').getroot()
        self.cartouche_risque = root[0].find('CARTOUCHERISQUE')
        self.risques = self.cartouche_risque[0].attrib

    def append_csv(self):
        # Testing that we do not violate primary key constraint error
        with open("app/data/hist_synthetise_bera.csv") as f:
            primary_keys = [(row.split(',')[0], row.split(',')[1]) for row in f]
            f.close()
        print(primary_keys)
        if (self.jour_key, self.massif) in primary_keys:
            print('Violation of primary key')
            return Exception('Violation of primary key')
        # If no violation of the primary key unicity constraint, we add the line
        with open('app/data/hist_synthetise_bera.csv', 'a') as f:
            writer_object = writer(f)
            writer_object.writerow([self.jour_key, self.massif, *self.risques.values()])
            f.close()



if __name__ == '__main__':
    with open('app/data/urls_list.txt','r') as f:
        pdfs = f.read().splitlines()
    for pdf in pdfs:
        massif, jour = pdf.split('.')
        bul = Bulletin(massif, jour)
        bul.download()
        bul.parse()
        bul.append_csv()
