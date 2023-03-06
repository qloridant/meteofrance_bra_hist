import subprocess

from github import InputGitTreeElement

from bera.utils.bulletin import Bulletin
from bera.utils.github import init_repo, update_file_content, commit_many_files_and_push
from bera.utils.common import init_logger, MASSIFS

logger = init_logger()

branch = 'master'
repo = init_repo()
elements = []

logger.info('Starting the daily extract...')

for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    jour = subprocess.run(["tail", "-n", "1", f"data/{massif}/urls_list.txt"], capture_output=True).stdout.decode(
        'utf-8')

    # Traitement du fichier
    bulletin = Bulletin(massif, jour)
    bulletin.download()
    bulletin.parse()
    new_data = bulletin.append_csv()

    file_path = f'data/{massif}/hist.csv'
    logger.info(f'Exporting the BERA to Github for massif : {massif}   ...')

    # Update file already existing
    full_content = update_file_content(repo, file_path, branch, [new_data], type_data='bera')

    # Add file in the tree to commit
    blob = repo.create_git_blob(full_content, "utf-8")
    element = InputGitTreeElement(path=file_path, mode='100644', type='blob', sha=blob.sha)
    elements.append(element)

logger.info('Compile all modified files in one commit  ...')
commit_many_files_and_push(repo, branch, "Daily automatic csv files update", elements)
logger.info('Job succeeded  ...')
