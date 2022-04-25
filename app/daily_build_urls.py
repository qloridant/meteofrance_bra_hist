# Ce script doit etre executé a partir de 16h.
import sys
import logging
from utils.extract import extract_url_dl
from utils.github import push, init_repo, get_remote_file
from datetime import date, timedelta, datetime


MASSIFS = ['CHABLAIS', 'MONT-BLANC', 'ARAVIS', 'CHARTREUSE', 'BELLEDONNE', 'GRANDES-ROUSSES', 'VERCORS', 'OISANS', 'HAUTE-TARENTAISE', 'BEAUFORTAIN', 'BAUGES', 'VANOISE', 'HAUTE-MAURIENNE', 'MAURIENNE', 'UBAYE', 'HAUT-VAR_HAUT-VERDON', 'THABOR', 'PELVOUX', 'QUEYRAS', 'CHAMPSAUR', 'DEVOLUY', 'EMBRUNAIS-PARPAILLON', 'MERCANTOUR', 'CINTO-ROTONDO', 'RENOSO-INCUDINE', 'ANDORRE', 'ORLU__ST_BARTHELEMY', 'HAUTE-ARIEGE', 'COUSERANS', 'LUCHONNAIS', 'AURE-LOURON', 'HAUTE-BIGORRE', 'ASPE-OSSAU', 'PAYS-BASQUE', 'CERDAGNE-CANIGOU','CAPCIR-PUYMORENS']


if __name__ == '__main__':
    logging.debug('Starting the extraction of urls...')
    new_urls = extract_url_dl(no_browser=True, start_date=date.today() + timedelta(days=-1), end_date=date.today() + timedelta(days=-1))


    branch = 'master'
    repo = init_repo()

    for massif in MASSIFS:
        file_path = f'app/data/{massif}/urls_list.txt'

        logging.debug(f'Exporting the URL to Github for massif : {massif}   ...')
        hist_urls = get_remote_file(repo, file_path, branch)
        # push(repo, file_path, "Daily automatic file update", new_urls[massif], branch)
        push(repo, file_path, "Daily automatic file update", hist_urls + new_urls[massif], branch, update=True)

    logging.debug('Complete !')
