# Ce script doit etre executé a partir de 16h.
import sys
import logging
from utils.extract import extract_url_dl
from utils.github import push, init_repo, get_remote_file
from utils.bulletin import Bulletin
from datetime import date, timedelta

NOMBRE_MASSIF = 37 # Variable qui ne devrait pas trop changer

if __name__ == '__main__':

    logging.debug("Lecture des BERAS a télécharger")
    with open('app/data/urls_list.txt','r') as f:
        urls = f.read().splitlines()
    last_urls = urls[-NOMBRE_MASSIF:]

    for pdf in last_urls:
        massif, jour = pdf.split('.')
        print(jour)
        # if jour différent de aujourd'hui on fais pas
        logging.debug(f'En cours de traitement du BERA de {massif}')
        bul = Bulletin(massif, jour)
        bul.download()
        bul.parse()
        bul.append_csv()
