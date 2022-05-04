import subprocess
import logging
from utils.bulletin import Bulletin
from utils.github import push, init_repo, get_remote_file

MASSIFS = ['CHABLAIS', 'MONT-BLANC', 'ARAVIS', 'CHARTREUSE', 'BELLEDONNE', 'GRANDES-ROUSSES', 'VERCORS', 'OISANS', 'HAUTE-TARENTAISE', 'BEAUFORTAIN', 'BAUGES', 'VANOISE', 'HAUTE-MAURIENNE', 'MAURIENNE', 'UBAYE', 'HAUT-VAR_HAUT-VERDON', 'THABOR', 'PELVOUX', 'QUEYRAS', 'CHAMPSAUR', 'DEVOLUY', 'EMBRUNAIS-PARPAILLON', 'MERCANTOUR', 'CINTO-ROTONDO', 'RENOSO-INCUDINE', 'ANDORRE', 'ORLU__ST_BARTHELEMY', 'HAUTE-ARIEGE', 'COUSERANS', 'LUCHONNAIS', 'AURE-LOURON', 'HAUTE-BIGORRE', 'ASPE-OSSAU', 'PAYS-BASQUE', 'CERDAGNE-CANIGOU','CAPCIR-PUYMORENS']

branch = 'master'
repo = init_repo()

for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    # Utilisation de bash... Efficace ou pythonesque ? Mon choix est fait
    jour = subprocess.run(["tail", "-n", "1", f"app/data/{massif}/urls_list.txt"], capture_output=True).stdout.decode('utf-8')

    # Traitement du fichier
    bulletin = Bulletin(massif, jour)
    bulletin.download()
    bulletin.parse()
    new_data = bulletin.append_csv()

    file_path = f'app/data/{massif}/hist.csv'
    logging.debug(f'Exporting the BERA to Github for massif : {massif}   ...')
    push(repo, file_path, "Daily automatic file update", [new_data], branch, update=True, type_data='bera')
