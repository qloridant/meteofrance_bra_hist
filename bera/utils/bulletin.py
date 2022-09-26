import logging
import sys
import requests
import xml.etree.ElementTree as ET

from bera.utils.common import MASSIFS

logger = logging.getLogger(__name__)

RISQUE_ATTRIBUTES = ['ALTITUDE', 'COMMENTAIRE', 'EVOLURISQUE1', 'EVOLURISQUE2',
                     'LOC1', 'LOC2', 'RISQUE1', 'RISQUE2', 'RISQUEMAXI']


class MassifInexistantException(Exception):
    pass


class Bulletin:
    "Défintion d'un bulletin risque avalanche"

    def __init__(self, massif, jour):
        self.cartouche_risque = ''
        self.risques = ''
        if massif in MASSIFS:
            self.massif = massif
        else:
            raise MassifInexistantException
        self.jour = jour

    @property
    def url(self):
        return "https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA"

    @property
    def path_file(self):
        return 'bera/tmp_bera.xml'

    @property
    def jour_key(self):
        return self.jour[0:4] + '-' + self.jour[4:6] + '-' + self.jour[6:8]

    def download(self):
        r = requests.get(f'{self.url}.{self.massif}.{self.jour}.xml')
        logger.debug(f'{self.url}.{self.massif}.{self.jour}.xml')
        with open(self.path_file, 'bw+') as f:
            f.write(r.content)

    def parse(self):
        root = ET.parse(self.path_file).getroot()
        self.cartouche_risque = root[0].find('CARTOUCHERISQUE')
        self.risques = self.cartouche_risque[0].attrib

        risques_attr = list(self.risques.keys())
        risques_attr.sort()
        if len(self.risques) != 9 or (risques_attr != RISQUE_ATTRIBUTES):
            raise ET.ParseError
        else:
            return self.risques

    def append_csv(self):
        # Removing comma as we will save the file as a csv
        risques = list(
            map(lambda x: x.replace(',', '-'), self.risques.values()))
        return [self.jour_key, self.massif, *risques]


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
