import subprocess
import logging
from utils.bulletin import Bulletin
from utils.github import push, init_repo, get_remote_file
from utils.common import init_logger, MASSIFS

logger = init_logger()

branch = 'master'
repo = init_repo()

logger.info('Starting the daily extract...')

for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    jour = subprocess.run(["tail", "-n", "1", f"data/{massif}/urls_list.txt"], capture_output=True).stdout.decode('utf-8')
    # Traitement du fichier
    bulletin = Bulletin(massif, jour)
    bulletin.download()
    bulletin.parse()
    new_data = bulletin.append_csv()

    file_path = f'data/{massif}/hist.csv'
    logger.info(f'Exporting the BERA to Github for massif : {massif}   ...')
    push(repo, file_path, "Daily automatic file update", [new_data], branch, update=True, type_data='bera')

logger.info('Daily extract finished')
