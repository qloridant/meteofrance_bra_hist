# Ce script doit etre executé a partir de 16h (heure de publication)
import os
from datetime import datetime

from utils.common import init_logger, MASSIFS
from utils.extract import extract_url_dl
from utils.github_utils import init_repo, commit_many_files_and_push, \
    update_and_add_file_to_commit

logger = init_logger()

if __name__ == '__main__':
    branch = os.getenv('GIT_BRANCH_NAME')
    if not branch:
        raise Exception(
            'Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

    logger.info('Starting the extraction of urls...')
    new_urls = extract_url_dl(no_browser=True,
                              start_date=datetime(2023, 1, 10),
                              end_date=datetime(2023, 1, 25))

    repo = init_repo()
    files_to_commit = []

    for massif in MASSIFS:
        file_path = f'data/{massif}/urls_list.txt'
        logger.info(f'Exporting the URL to Github for massif : {massif}   ...')

        # Update and add files to commit
        files_to_commit = update_and_add_file_to_commit(repo, file_path,
                                                        branch,
                                                        new_urls[massif],
                                                        'url', files_to_commit)

    logger.info('Compile all modified files in one commit  ...')
    commit_many_files_and_push(repo, branch,
                               "Historical automatic url files update",
                               files_to_commit)
    logger.info('Job succeeded  ...')
