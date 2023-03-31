import json
import logging
import os
import sys
import xml.etree.ElementTree as ET

import requests

from bera.utils.common import MASSIFS, format_hist_meteo, format_neige_fraiche
from bera.utils.github_utils import init_repo, update_file_content

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
        self.meteo = {}
        self.neige_fraiche = {}

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

    def parse_donnees_risques(self) -> []:
        root = ET.parse(self.path_file).getroot()
        self.cartouche_risque = root[0].find('CARTOUCHERISQUE')
        self.risques = self.cartouche_risque[0].attrib

        risques_attr = list(self.risques.keys())
        risques_attr.sort()
        if len(self.risques) != 9 or (risques_attr != RISQUE_ATTRIBUTES):
            raise ET.ParseError
        else:
            return self.risques

    def parse_donnees_meteo(self) -> dict:
        """
        Parse historical weather into a formated dict: wind, temperature, snow precipitations, isotherm from the BERA xml content
        
        Historical weather data for the last 6 days are available in the <BSH><METEO><ECHEANCE> xml content balises and
        historical snow precipitations for the last 6 days are available in the <BSH><NEIGEFRAICHE><NEIGE24H> and also
        in <NEIGEFRAICHE><NEIGE24H> xml content balises.

        For example for the BERA of the 2023-02-28 in CHABLAIS:

        <BSH>
            <METEO ALTITUDEVENT1="2000" ALTITUDEVENT2="2500">
              ...
              <ECHEANCE DATE="2023-02-28T00:00:00" TEMPSSENSIBLE="18" TEMPSSENSIBLEJ="-1" MERNUAGES="1200"
              PLUIENEIGE="-1" ISO0="500" ISO-10="2900" DD1="S" FF1="10" DD2="SW" FF2="20"/>
              <ECHEANCE DATE="2023-02-28T06:00:00" TEMPSSENSIBLE="2" TEMPSSENSIBLEJ="2" MERNUAGES="-1"
              PLUIENEIGE="-1" ISO0="1000" ISO-10="2800" DD1="S" FF1="10" DD2="SW" FF2="20"/>
              <ECHEANCE DATE="2023-02-28T12:00:00" TEMPSSENSIBLE="2" TEMPSSENSIBLEJ="-1" MERNUAGES="-1"
              PLUIENEIGE="-1" ISO0="1100" ISO-10="2900" DD1="_" FF1="0" DD2="S" FF2="10"/>
            </METEO>
            ...
            <NEIGEFRAICHE SECTEURSS1="massif" SECTEURSS2="" ALTITUDESS="1800">
                ...
              <NEIGE24H DATE="2023-02-27T00:00:00" SS241="0" SS242="-1"/>   --- historical data
            ...
            </NEIGEFRAICHE>
        </BSH>


        return:
        self.meteo: dict
        """
        root = ET.parse(self.path_file).getroot()
        hist_meteo_unformatted = [echeance.attrib for echeance in root[0].find('BSH').iter(tag="ECHEANCE")]
        altitude_vent_1 = root[0].find('BSH').find('METEO').get('ALTITUDEVENT1')
        altitude_vent_2 = root[0].find('BSH').find('METEO').get('ALTITUDEVENT2')

        # Get weather measures for the day of the BERA publication at 00:00:00, 06:00:00 and 12:00:00 meteo
        for unformatted_meteo in hist_meteo_unformatted[-3:]:
            meteo = format_hist_meteo(unformatted_meteo, altitude_vent_1, altitude_vent_2)
            self.meteo.update(meteo)

        # Get historical snow precipitations measures for the day before publication 
        hist_neige_fraiche_unformatted = [neige_fraiche.attrib for neige_fraiche in
                                          root[0].find('BSH').iter(tag="NEIGE24H")]
        altitude_neige_fraiche = root[0].find('BSH').find('NEIGEFRAICHE').get('ALTITUDESS')
        unformatted_neige_fraiche = hist_neige_fraiche_unformatted[-1]
        neige_fraiche = format_neige_fraiche(unformatted_neige_fraiche, altitude_neige_fraiche)
        self.meteo.update(neige_fraiche)

        return self.meteo


    def append_csv(self):
        # Removing comma as we will save the file as a csv
        risques = list(
            map(lambda x: x.replace(',', '-'), self.risques.values()))
        return [self.jour_key, self.massif, *risques, f'{self.url}.{self.massif}.{self.jour}.pdf',
                *self.meteo.values()]


if __name__ == '__main__':
    branch = os.getenv('GIT_BRANCH_NAME')
    if not branch:
        raise Exception('Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

    repo = init_repo()

    if len(sys.argv) == 3:
        massif = sys.argv[1]
        jour = sys.argv[2]  # At format YYYYmmddHHMMSS ex: 20230322144948
        bul = Bulletin(massif, jour)
        bul.download()
        bul.parse_donnees_risques()
        bul.parse_donnees_meteo()
        new_content = bul.append_csv()
        file_path = f'data/{massif}/hist.csv'

        full_content = update_file_content(repo, file_path, branch, [new_content], 'bera')
        print('Job succeeded.')

    else:
        print("Please enter massif and datetime of publication")
