import logging
import os
import subprocess
import time

from utils.bulletin import Bulletin
from utils.common import init_logger, MASSIFS
from utils.github import init_repo, commit_many_files_and_push, \
    update_and_add_file_to_commit

logger = init_logger(logging.DEBUG)
start_time = time.time()

branch = os.getenv('GIT_BRANCH_NAME')
if not branch:
    raise Exception(
        'Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

repo = init_repo()
files_to_commit = []

for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    dates_ = subprocess.run(["cat", f"data/{massif}/urls_list.txt"],
                            capture_output=True).stdout.decode('utf-8').split(
        '\n')
    new_data = []
    logger.debug(
        f"{time.time() - start_time} seconds  - Exporting data from BERA xml into hist.csv data file "
        f"for massif {massif} ...")
    for date_ in dates_:
        if int(date_) >= 20181217143136:  ## Début des fichiers XML
            # logger.debug(date_)
            bulletin = Bulletin(massif, date_)
            try:
                bulletin.download()
                bulletin.parse_risques()
                new_data.append(bulletin.append_csv())
            except Exception as e:
                logger.error("An error occured in downloading BERA, parsing or adding new data content for massif "
                             f"{massif} and date {date_} ...",
                             exc_info=True)
                pass

    # Update and add files to commit
    logger.info(f'Update and add updated files to commit for massif : {massif}   ...')
    file_path = f'data/{massif}/hist.csv'
    files_to_commit = update_and_add_file_to_commit(repo, file_path, branch,
                                                    new_data, 'bera',
                                                    files_to_commit)

logger.info('Compile all modified files in one commit  ...')
commit_many_files_and_push(repo, branch,
                           "Historical automatic csv files update",
                           files_to_commit)
logger.info('Job succeeded  ...')
