import os
import subprocess

from bera.utils.bulletin import Bulletin
from bera.utils.common import init_logger, MASSIFS
from bera.utils.github import init_repo, commit_many_files_and_push, \
    update_and_add_file_to_commit

logger = init_logger()

branch = os.getenv('GIT_BRANCH_NAME')
if not branch:
    raise Exception('Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

repo = init_repo()
files_to_commit = []

logger.info('Starting the daily extract...')

for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    jour = subprocess.run(["tail", "-n", "1", f"data/{massif}/urls_list.txt"],
                          capture_output=True).stdout.decode('utf-8')

    # Traitement du fichier
    bulletin = Bulletin(massif, jour)
    bulletin.download()
    bulletin.parse_risques()
    new_data = bulletin.append_csv()

    file_path = f'data/{massif}/hist.csv'
    logger.info(f'Exporting the BERA to Github for massif : {massif}   ...')

    # Update and add files to commit
    files_to_commit = update_and_add_file_to_commit(repo, file_path, branch,
                                                    [new_data], 'bera',
                                                    files_to_commit)

logger.info('Compile all modified files in one commit  ...')
commit_many_files_and_push(repo, branch, "Daily automatic csv files update",
                           files_to_commit)
logger.info('Job succeeded  ...')
