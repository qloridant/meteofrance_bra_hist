import logging

# List of all french mountains chains concerned by a BERA
MASSIFS = ['CHABLAIS', 'MONT-BLANC', 'ARAVIS', 'CHARTREUSE', 'BELLEDONNE',
           'GRANDES-ROUSSES', 'VERCORS', 'OISANS', 'HAUTE-TARENTAISE',
           'BEAUFORTAIN', 'BAUGES', 'VANOISE', 'HAUTE-MAURIENNE', 'MAURIENNE',
           'UBAYE', 'HAUT-VAR_HAUT-VERDON', 'THABOR', 'PELVOUX', 'QUEYRAS',
           'CHAMPSAUR', 'DEVOLUY', 'EMBRUNAIS-PARPAILLON', 'MERCANTOUR',
           'CINTO-ROTONDO', 'RENOSO-INCUDINE', 'ANDORRE',
           'ORLU__ST_BARTHELEMY', 'HAUTE-ARIEGE', 'COUSERANS', 'LUCHONNAIS',
           'AURE-LOURON', 'HAUTE-BIGORRE', 'ASPE-OSSAU', 'PAYS-BASQUE',
           'CERDAGNE-CANIGOU', 'CAPCIR-PUYMORENS']

PARAMS = ['date', 'massif', 'risque1', 'evolurisque1', 'loc1', 'altitude', 'risque2', 'evolurisque2', 'loc2',
          'risque_maxi', 'commentaire', 'url_telechargement', '00_temps', '00_mer_de_nuages', '00_limite_pluie_neige',
          '00_isotherme_0', '00_isotherme_moins_10', '00_altitude_vent_1', '00_altitude_vent_2',
          '00_direction_vent_altitude_1', '00_vitesse_vent_altitude_1', '00_direction_vent_altitude_2',
          '00_vitesse_vent_altitude_2', '06_temps', '06_mer_de_nuages', '06_limite_pluie_neige', '06_isotherme_0',
          '06_isotherme_moins_10', '06_altitude_vent_1', '06_altitude_vent_2', '06_direction_vent_altitude_1',
          '06_vitesse_vent_altitude_1', '06_direction_vent_altitude_2', '06_vitesse_vent_altitude_2', '12_temps',
          '12_mer_de_nuages', '12_limite_pluie_neige', '12_isotherme_0', '12_isotherme_moins_10', '12_altitude_vent_1',
          '12_altitude_vent_2', '12_direction_vent_altitude_1', '12_vitesse_vent_altitude_1',
          '12_direction_vent_altitude_2', '12_vitesse_vent_altitude_2', 'precipitation_neige_veille_altitude', 
          'precipitation_neige_veille_epaisseur']

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


def init_logger(log_level=logging.INFO):
    """
    This function aims to create a custom logger for all this project

    Returns
    -------
    logger: logger object
    """
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
    {'DATE': '2023-02-01T12:00:00', 'METEO': 'Beau temps', 'MER DE NUAGES': 'Non', 'LIMITE PLUIE NEIGE': 'Sans objet',
    'ISO-0': '1500', 'ISO-10': '3200', 'DIRECTION VENT ALTITUDE 1': 'W', 'VITESSE VENT ALTITUDE 1': '20',
    'DIRECTION VENT ALTITUDE 2': 'NW', 'VITESSE VENT ALTITUDE 2': '40'}
    and return this new dict

    params:
    unformatted_meteo: dict: unformatted dict representing historical wheater data
    altitude1: str: altidude 1 used in wheater data for wind data
    altitude2: str: altidude 2 used in wheater data for wind data

    return:
    formatted_meteo: dict: formatted dict representing meteo historical data
    """
    hour = unformatted_meteo['DATE'][-8:-6]
    formatted_meteo = {
        f'{hour}_temps': PICTO_METEO[unformatted_meteo['TEMPSSENSIBLE']],
        f'{hour}_mer_de_nuages': 'Non' if unformatted_meteo['MERNUAGES'] == '-1' else unformatted_meteo['MERNUAGES'],
        f'{hour}_limite_pluie_neige': 'Sans objet' if unformatted_meteo['PLUIENEIGE'] == '-1' else unformatted_meteo[
            'PLUIENEIGE'],
        f'{hour}_isotherme_0': unformatted_meteo['ISO0'],
        f'{hour}_isotherme_moins_10': unformatted_meteo['ISO-10'],
        f'{hour}_altitude_vent_1': altitude1,
        f'{hour}_altitude_vent_2': altitude2,
        f'{hour}_direction_vent_altitude_1': unformatted_meteo['DD1'],
        f'{hour}_vitesse_vent_altitude_1': unformatted_meteo['FF1'],
        f'{hour}_direction_vent_altitude_2': unformatted_meteo['DD2'],
        f'{hour}_vitesse_vent_altitude_2': unformatted_meteo['FF2']
    }
    return formatted_meteo


def format_neige_fraiche(unformatted_neige_fraiche: dict, altitude_neige_fraiche: str) -> dict:
    """
    From an input dict with this format sample
    {'DATE': '2023-03-21T00:00:00', 'SS241': '0', 'SS242': '-1'},

    create a new dict in this format:
    {'DATE': '2023-02-01T12:00:00', 'NEIGE FRAICHE A ALTTITUDE {altitude_neige_fraiche} (EN CM)': '0'}
    and return this new dict

    params:
    unformatted_neige_fraiche: dict: unformatted dict representing meteo prevision
    altitude_neige_fraiche: str: altidude used in historical snow falls data

    return:
    formatted_neige_frajche: dict: formatted dict representing historical snow falls
    """
    formatted_neige_fraiche = {
        "precipitation_neige_veille_altitude": altitude_neige_fraiche,
        "precipitation_neige_veille_epaisseur": 'Pluie' if unformatted_neige_fraiche['SS241'] == '-2' else (
                ' - ' if unformatted_neige_fraiche['SS241'] == '-1' else unformatted_neige_fraiche['SS241'])
    }
    return formatted_neige_fraiche
