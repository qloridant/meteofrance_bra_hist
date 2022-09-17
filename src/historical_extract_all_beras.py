import subprocess
import logging
from utils.bulletin import Bulletin
from utils.github import push, init_repo, get_remote_file
from utils.common import init_logger, MASSIFS

logger = init_logger(logging.DEBUG)

branch = 'master'
repo = init_repo()
MASSIFS=[MASSIFS[0]]
for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    dates_ = subprocess.run(["cat", f"src/data/{massif}/urls_list.txt"], capture_output=True).stdout.decode('utf-8').split('\n')
    dates_ = [dates_[0]]
    logger.debug(massif)
    new_data = []
    for date_ in dates_:
        if int(date_) >= 20181217143136: ## Début des fichiers XML
            logger.debug(date_)
            bulletin = Bulletin(massif, date_)
            bulletin.download()

            try:
                bulletin.parse()
                new_data.append(bulletin.append_csv())
            except Exception as e:
                pass

    file_path = f'src/data/{massif}/hist.csv'
    logger.info(f'Exporting the BERA to Github for massif : {massif}   ...')
    # push(repo, file_path, "Daily automatic file update", new_data, branch, update=True, type_data='bera')
