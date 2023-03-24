import logging

MASSIFS = ['CHABLAIS', 'MONT-BLANC', 'ARAVIS', 'CHARTREUSE', 'BELLEDONNE',
           'GRANDES-ROUSSES', 'VERCORS', 'OISANS', 'HAUTE-TARENTAISE',
           'BEAUFORTAIN', 'BAUGES', 'VANOISE', 'HAUTE-MAURIENNE', 'MAURIENNE',
           'UBAYE', 'HAUT-VAR_HAUT-VERDON', 'THABOR', 'PELVOUX', 'QUEYRAS',
           'CHAMPSAUR', 'DEVOLUY', 'EMBRUNAIS-PARPAILLON', 'MERCANTOUR',
           'CINTO-ROTONDO', 'RENOSO-INCUDINE', 'ANDORRE',
           'ORLU__ST_BARTHELEMY', 'HAUTE-ARIEGE', 'COUSERANS', 'LUCHONNAIS',
           'AURE-LOURON', 'HAUTE-BIGORRE', 'ASPE-OSSAU', 'PAYS-BASQUE',
           'CERDAGNE-CANIGOU', 'CAPCIR-PUYMORENS']

# http://www.meteo.fr/guide/guide_pictos.html
# https://meteofrance.com/ > Légende au pied de la page
PICTO_METEO = {
    "-1": "Absence de données",
    "1": "Beau temps",
    "2": "Brume",
    "3": "Eclaircies",
    "4": "Peu nuageux",
    "5": "Variable",
    "6": "Très nuageux",
    "7": "Pluies éparses",
    "8": "Pluie faible / grésille",  # ???
    "9": "Averses de pluie",
    "10": "Neige faible",
    "11": "Averses de neige",
    "12": "Neige modérée",
    "13": "Risque d'orages",
    "14": "Orages violents",
    "15": "Brouillard",
    "16": "Brouillard givrant",
    "17": "Pictogramme non identifié",
    "18": "Beau temps avec mer de nuage"
}


# Create a custom logger
def init_logger(log_level=logging.INFO):
    logger = logging.getLogger(__name__)
    c_handler = logging.StreamHandler()
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    logger.setLevel(log_level)

    return logger


def format_hist_meteo(unformatted_meteo: dict, altitude1: str, altitude2: str) -> dict:
    """
    From an input dict with this format sample
    {'DATE': '2023-02-01T12:00:00', 'TEMPSSENSIBLE': '1', 'TEMPSSENSIBLEJ': '-1', 'MERNUAGES': '-1', 'PLUIENEIGE': '-1',
    'ISO0': '1500', 'ISO-10': '3200', 'DD1': 'W', 'FF1': '20', 'DD2': 'NW', 'FF2': '40'},

    create a new dict in this format:
    {'DATE': '2023-02-01T12:00:00', 'METEO': 'Beau temps', 'MER_DE_NUAGES': 'Non', 'LIMITE_PLUIE_NEIGE': 'Sans objet',
    'ISO-0': '1500', 'ISO-10': '3200', 'DIRECTION_VENT_ALTITUDE_1': 'W', 'VITESSE_VENT_ALTITUDE_1': '20',
    'DIRECTION_VENT_ALTITUDE_2': 'NW', 'VITESSE_VENT_ALTITUDE_2': '40'}
    and return this new dict

    params:
    unformatted_meteo: dict: unformatted dict representing meteo prevision
    altitude1: str: altidude 1 used in meteo prevision
    altitude2: str: altidude 2 used in meteo prevision

    return:
    formatted_meteo: dict: formatted dict representing meteo prevision


    """
    formatted_meteo = {
        f"METEO A {unformatted_meteo['DATE']}": {
            'TEMPS': PICTO_METEO[unformatted_meteo['TEMPSSENSIBLE']],
            'MER DE NUAGES': 'Non' if unformatted_meteo['MERNUAGES'] == '-1' else unformatted_meteo['MERNUAGES'],
            'LIMITE PLUIE NEIGE': 'Sans objet' if unformatted_meteo['PLUIENEIGE'] == '-1' else unformatted_meteo[
                'PLUIENEIGE'],
            'ISOTHERME 0°C': unformatted_meteo['ISO0'],
            'ISOTHERME -10°C': unformatted_meteo['ISO-10'],
            'ALTITUDE VENT 1': altitude1,
            'ALTITUDE VENT 2': altitude2,
            'DIRECTION VENT ALTITUDE_1': unformatted_meteo['DD1'],
            'VITESSE VENT ALTITUDE 1': unformatted_meteo['FF1'],
            'DIRECTION VENT ALTITUDE 2': unformatted_meteo['DD2'],
            'VITESSE VENT ALTITUDE 2': unformatted_meteo['FF2']
        }
    }
    return formatted_meteo
