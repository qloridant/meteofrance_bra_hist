"""
This script allows the user to see the BERA data exported in a list format for a given mountain chain and a given date.
It takes two arguments:
- massif: str representing the chain mountain concerned by the extraction of the BERA expected,
- datetieme: str at format YYYYmmddHHMMSS representing the datetime of the publication of the BERA. To find it you can
  consult the file data/{massif}/urls_list.txt listing the datetimes of all BERA publications for one given
  chain mountain ('massif' in french).

To run this script run this command:
python bera/utils/bulletin.py CHABLAIS 20230329140534
or
poetry run python bera/utils/bulletin.py CHABLAIS 20230329140534

The exececution will show by printing the BERA data exported in a list format, for example for CHABLAIS
on the 29/03/2023:
['date', 'massif', 'risque1', 'evolurisque1', 'loc1', 'altitude', 'risque2', 'evolurisque2', 'loc2', 'risque_maxi',
'commentaire', 'url_telechargement']
['2023-03-29', 'CHABLAIS', '2', '', '<2500', '2500', '3', '', '>2500', '3',
'Au-dessus de 2500 m : Risque marqué. En-dessous : Risque limité.',
'https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.CHABLAIS.20230329140534.pdf']

NB: this script is mainly useful in a development context.
"""

import logging
import os
import re
import sys

import requests
import xml.etree.ElementTree as ET

from bera.utils.common import MASSIFS, format_hist_meteo, format_neige_fraiche, construct_unavailable_meteo_dict, \
    construct_unavailable_neige_fraiche_dict
from bera.utils.github_utils import init_repo, update_file_content

logger = logging.getLogger(__name__)

RISQUE_ATTRIBUTES = ['ALTITUDE', 'COMMENTAIRE', 'EVOLURISQUE1', 'EVOLURISQUE2',
                     'LOC1', 'LOC2', 'RISQUE1', 'RISQUE2', 'RISQUEMAXI']


class MassifInexistantException(Exception):
    pass


class Bulletin:
    """
    This class is used to represent a BERA ("bulletin d'estimation du risque d'avalanche" in french)

    Attributes
    ----------
    massif: str: the mountain chaine concerned by the BERA object
    jour: str: the datetime of the BERA's publication in str format YYYYmmddHHMMSS
    risques: dict: corresponding to the risk data extracted from the BERA published, associating values
             for these keys:
             risque1, evolurisque1, loc1, altitude, risque2, evolurisque2, loc2, risque_maxi, commentaire
    meteo: dict: corresponding to the weather, wind, isothermand snow precipitations data extracted from the BERA
           published
    """

    def __init__(self, massif: str, jour: str):
        """
        Constructor of the Bulletin class

        Parameters
        ----------
        massif: str: the mountain chaine concerned by the BERA object
        jour: str: the datetime of the BERA's publication in str format YYYYmmddHHMMSS
        """
        if massif in MASSIFS:
            self.massif = massif
        else:
            raise MassifInexistantException
        self.jour = jour
        self.risques = {}
        self.meteo = {}
        self.situation_avalancheuse = {}

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
        """
        This method aims to:
        - download a BERA in xml format for its massif and its day,
        - write the content into a temporary file bera/tmp_bera.xml
        """
        r = requests.get(f'{self.url}.{self.massif}.{self.jour}.xml')
        logger.debug(f'{self.url}.{self.massif}.{self.jour}.xml')
        with open(self.path_file, 'bw+') as f:
            f.write(r.content)

    def parse_donnees_risques(self) -> []:
        """
        This method aims to extract risk information from the BERA xml content and parse it into a dict which will be
        integrated at the end in hist.csv files to store risk data.
        Risk data is available in the <CARTOUCHERISQUE> xml content balise:
        For example for the BERA of the 2023-02-28 in CHABLAIS:
        <CARTOUCHERISQUE>
            <RISQUE RISQUE1="1" EVOLURISQUE1="" LOC1="" ALTITUDE="" RISQUE2="" EVOLURISQUE2="" LOC2="" RISQUEMAXI="1" COMMENTAIRE=" "/>
            <PENTE NE="false" E="false" SE="false" S="false" SW="false" W="false" NW="false" N="false" COMMENTAIRE=""/>
            <ACCIDENTEL>rares plaques anciennes ou nouvelles</ACCIDENTEL>
            <NATUREL>peu probables</NATUREL>
            <RESUME>Départs spontanés : peu probables
                    Déclenchements skieurs : rares plaques anciennes ou nouvelles
            </RESUME>
            <AVIS/>
            <VIGILANCE/>
            <ImageCartoucheRisque Format="png" Width="345" Height="134">
                <Content>
                ...
                </Content>
            </ImageCartoucheRisque>
        </CARTOUCHERISQUE>

        This method uses this xml content to provide a formatted dict of risk data for the day of the BERA.

        Returns
        -------
        self.risk: dict: corresponding to the risk data extracted from the BERA published, associating values
             for these keys:
             risque1, evolurisque1, loc1, altitude, risque2, evolurisque2, loc2, risque_maxi, commentaire
        """
        root = ET.parse(self.path_file).getroot()
        cartouche_risque = root[0].find('CARTOUCHERISQUE')
        if cartouche_risque is None:
            cartouche_risque = root.find('CARTOUCHERISQUE')
        self.risques = cartouche_risque[0].attrib

        risques_attr = list(self.risques.keys())
        risques_attr.sort()
        if len(self.risques) != 9 or (risques_attr != RISQUE_ATTRIBUTES):
            raise ET.ParseError
        else:
            return self.risques

    def parse_donnees_meteo(self) -> dict:
        """
        Parse historical weather into a formated dict: wind, temperature, snow precipitations, isotherm from the BERA
        xml content.
        
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
        try:
            if not root[0].find('BSH') is None:
                hist_meteo_unformatted = [echeance.attrib for echeance in root[0].find('BSH').iter(tag="ECHEANCE")]
                altitude_vent_1 = root[0].find('BSH').find('METEO').get('ALTITUDEVENT1')
                altitude_vent_2 = root[0].find('BSH').find('METEO').get('ALTITUDEVENT2')
            else:
                hist_meteo_unformatted = [echeance.attrib for echeance in root.find('BSH').iter(tag="ECHEANCE")]
                altitude_vent_1 = root.find('BSH').find('METEO').get('ALTITUDEVENT1')
                altitude_vent_2 = root.find('BSH').find('METEO').get('ALTITUDEVENT2')

            # Get weather measures for the day of the BERA publication at 00:00:00, 06:00:00 and 12:00:00 meteo
            for unformatted_meteo in hist_meteo_unformatted[-3:]:
                meteo = format_hist_meteo(unformatted_meteo, altitude_vent_1, altitude_vent_2)
                self.meteo.update(meteo)

        except Exception as e:
            # Historical weather data is not available in the BERA xml content
            unavailable_meteo = construct_unavailable_meteo_dict()
            self.meteo.update(unavailable_meteo)

        try:
            # Get historical snow precipitations measures for the day before publication
            if not root[0].find('BSH') is None:
                hist_neige_fraiche_unformatted = [neige_fraiche.attrib for neige_fraiche in
                                                  root[0].find('BSH').iter(tag="NEIGE24H")]
                altitude_neige_fraiche = root[0].find('BSH').find('NEIGEFRAICHE').get('ALTITUDESS')
            else:
                hist_neige_fraiche_unformatted = [neige_fraiche.attrib for neige_fraiche in
                                                  root.find('BSH').iter(tag="NEIGE24H")]
                altitude_neige_fraiche = root.find('BSH').find('NEIGEFRAICHE').get('ALTITUDESS')
            unformatted_neige_fraiche = hist_neige_fraiche_unformatted[-1]
            neige_fraiche = format_neige_fraiche(unformatted_neige_fraiche, altitude_neige_fraiche)
            self.meteo.update(neige_fraiche)

        except Exception as e:
            # Historical snow precipitations data is not available in the BERA xml content
            unavailable_neige_fraiche = construct_unavailable_neige_fraiche_dict()
            self.meteo.update(unavailable_neige_fraiche)

        return self.meteo

    def parse_situation_avalancheuse(self) -> dict:
        """
        Parse avalanche situations information from the BERA xml content into a formated dict, and return this dict.

        Most of the BERAs described in the "Stablité du manteau neigeux" paragraph the current avalanche situations
        which can be observed like:
        "Neige humide", "Sous-couches fragiles persistentes", "Neige fraîche", "Neige ventée", "Avalanche de fond"

        Returns
        -------
        situation_avalancheuse: dict : example {situations_avalancheuses_typiques: "Neige fraiche, neige ventée"}

        """
        root = ET.parse(self.path_file).getroot()
        try:
            if not root[0].find('STABILITE') is None:
                paragraph_stabilite = root[0].find('STABILITE').find('TEXTE')
                if 'Situation avalancheuse typique' in paragraph_stabilite.text or \
                        'Situation avalancheuse' in paragraph_stabilite.text:
                    text = re.search("Situation avalancheuse[^\n]*", paragraph_stabilite.text).group()
                    result = text.replace(', ', ' - ')
                    self.situation_avalancheuse["situation_avalancheuse_typique"] = \
                        re.split("Situation avalancheuse typique : ", result)[1]
                else:
                    self.situation_avalancheuse["situation_avalancheuse_typique"] = ''
            else:
                self.situation_avalancheuse["situation_avalancheuse_typique"] = ''

        except Exception:
            self.situation_avalancheuse["situation_avalancheuse_typique"] = ''

        return self.situation_avalancheuse

    def append_csv(self) -> []:
        """
        This method aims to construct a list of all formatted data which will be integrated at the end in hist.csv files
        to store BERA data containing:
        - The date of the BERA publication in YYYY-mm-dd str format
        - The massif of the BERA publication,
        - Risk data declined into 9 columns: (risque1, evolurisque1, loc1, altitude, risque2, evolurisque2, loc2,
          risque_maxi, commentaire),
        - The url of downloading the BERA in pdf format

        Returns
        -------
        list of strings containing all BERA information expected
        """
        # Removing comma as we will save the file as a csv
        risques = list(
            map(lambda x: x.replace(',', '-'), self.risques.values()))
        return [self.jour_key, self.massif, *risques, f'{self.url}.{self.massif}.{self.jour}.pdf',
                *self.meteo.values(), *self.situation_avalancheuse.values()]


if __name__ == '__main__':
    branch = os.getenv('GIT_BRANCH_NAME')
    if not branch:
        raise Exception('Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

    repo = init_repo()

    if len(sys.argv) == 3:
        massif = sys.argv[1]
        jour = sys.argv[2]  # At format YYYYmmddHHMMSS ex: 20230119144216  or  20230411135455
        bul = Bulletin(massif, jour)
        bul.download()
        bul.parse_donnees_risques()
        bul.parse_donnees_meteo()
        new_content = bul.append_csv()
        file_path = f'data/{massif}/hist.csv'

        full_content = update_file_content(repo, file_path, branch, [new_content], 'bera')
        print('Job succeeded.')

    else:
        massif = 'CHABLAIS'
        jour = '20220130143352'  # 20230119144216   20230411135455  20230417140025  20230119144216 20220319145301 20220419141041 20220130143352
        bul = Bulletin(massif, jour)
        bul.download()
        bul.parse_donnees_risques()
        bul.parse_donnees_meteo()
        bul.parse_situation_avalancheuse()
        new_content = bul.append_csv()
        file_path = f'data/{massif}/hist.csv'
        full_content = update_file_content(repo, file_path, branch, [new_content], 'bera')
        print('Job succeeded.')
