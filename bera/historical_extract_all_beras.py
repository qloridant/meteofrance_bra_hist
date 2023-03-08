import logging
import subprocess

from github import InputGitTreeElement

from utils.bulletin import Bulletin
from utils.common import init_logger, MASSIFS
from utils.github import init_repo, push, update_file_content, commit_many_files_and_push

logger = init_logger(logging.DEBUG)

branch = 'master'
repo = init_repo()
elements = []

for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    dates_ = subprocess.run(["cat", f"data/{massif}/urls_list.txt"],
                            capture_output=True).stdout.decode('utf-8').split(
        '\n')
    logger.debug(massif)
    new_data = []
    for date_ in dates_:
        if int(date_) >= 20181217143136:  ## Début des fichiers XML
            logger.debug(date_)
            bulletin = Bulletin(massif, date_)
            bulletin.download()

            try:
                bulletin.parse()
                new_data.append(bulletin.append_csv())
            except Exception as e:
                pass

    file_path = f'data/{massif}/hist.csv'
    logger.info(f'Exporting the BERA to Github for massif : {massif}   ...')

    # Update file already existing
    full_content = update_file_content(repo, file_path, branch, new_data, type_data='bera')

    # Add file in the tree to commit
    blob = repo.create_git_blob(full_content, "utf-8")
    element = InputGitTreeElement(path=file_path, mode='100644', type='blob', sha=blob.sha)
    elements.append(element)

logger.info('Compile all modified files in one commit  ...')
commit_many_files_and_push(repo, branch, "Daily automatic csv files update", elements)
logger.info('Job succeeded  ...')
