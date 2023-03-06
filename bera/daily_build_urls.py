# Ce script doit etre executé a partir de 16h (heure de publication)
from datetime import date

from github import InputGitTreeElement

from bera.utils.extract import extract_url_dl
from bera.utils.github import init_repo, update_file_content, commit_many_files_and_push
from bera.utils.common import init_logger, MASSIFS

logger = init_logger()


if __name__ == '__main__':
    print(MASSIFS)
    logger.info('Starting the extraction of urls...')
    new_urls = extract_url_dl(no_browser=True, start_date=date.today(), end_date=date.today())

    branch = 'master'
    repo = init_repo()
    elements = []

    for massif in MASSIFS:
        file_path = f'data/{massif}/urls_list.txt'
        logger.info(f'Exporting the URL to Github for massif : {massif}   ...')

        # Update file already existing
        full_content = update_file_content(repo, file_path, branch, new_urls[massif], type_data='url')

        # Add file in the tree to commit
        blob = repo.create_git_blob(full_content, "utf-8")
        element = InputGitTreeElement(path=file_path, mode='100644', type='blob', sha=blob.sha)
        elements.append(element)

    logger.info('Compile all modified files in one commit  ...')
    commit_many_files_and_push(repo, branch, "Daily automatic url files update", elements)
    logger.info('Job succeeded  ...')
