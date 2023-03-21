# Ce script doit etre executé a partir de 16h (heure de publication)
from datetime import date

from bera.utils.extract import extract_url_dl
from bera.utils.github import init_repo, update_file_content, commit_many_files_and_push, add_file_to_commit
from bera.utils.common import init_logger, MASSIFS

logger = init_logger()


if __name__ == '__main__':
    print(MASSIFS)
    logger.info('Starting the extraction of urls...')
    new_urls = extract_url_dl(no_browser=True, start_date=date.today(), end_date=date.today())

    branch = 'master'
    repo = init_repo()
    files = []

    for massif in MASSIFS:
        file_path = f'data/{massif}/urls_list.txt'
        logger.info(f'Exporting the URL to Github for massif : {massif}   ...')

        # Update file already existing
        full_content = update_file_content(repo, file_path, branch, new_urls[massif], type_data='url')

        # Add file in the tree to commit
        file = add_file_to_commit(repo, full_content, file_path)
        files.append(file)

    logger.info('Compile all modified files in one commit  ...')
    commit_many_files_and_push(repo, branch, "Daily automatic url files update", files)
    logger.info('Job succeeded  ...')
