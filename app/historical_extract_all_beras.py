import subprocess
import logging
from utils.bulletin import Bulletin
from utils.github import push, init_repo, get_remote_file
from utils.common import init_logger, MASSIFS

logger = init_logger()

branch = 'master'
repo = init_repo()

for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    dates_ = subprocess.run(["cat", f"app/data/{massif}/urls_list.txt"], capture_output=True).stdout.decode('utf-8').split('\n')

    new_data = []
    for date_ in dates_:
        if int(date_) >= 20181217143136:
            # Traitement du fichier
            bulletin = Bulletin(massif, date_)
            bulletin.download()
            try:
                bulletin.parse()
                new_data.append(bulletin.append_csv())
                logging.debug(date_)
            except Exception as e:
                pass

    file_path = f'app/data/{massif}/hist.csv'
    logging.info(f'Exporting the BERA to Github for massif : {massif}   ...')
    push(repo, file_path, "Daily automatic file update", new_data, branch, update=True, type_data='bera')
