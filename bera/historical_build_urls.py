"""
This script aims to get all the datetime of BERAs' publication for a given period for all mountain chains, and to save
them into all the data/<massif>/urls_list.txt files in the 'master' branch of the GitHub repository
https://github.com/qloridant/meteofrance_bra_hist.

This script was useful to get all historical datetime of all BERAs' publications anterior at the beginning of this
project.
For now, normally, all datetimes of all BERAs' publications for all mountain chains had been saved in
data/<massif>/urls_list.txt files and this script is not useful anymore.

This script does the same as the script daily_build_urls.py but for each day of the given period.
"""
import logging
import os
import time
from datetime import datetime

from utils.common import init_logger, MASSIFS
from utils.extract import extract_url_dl
from utils.github_utils import init_repo, update_file_content

logger = init_logger(logging.DEBUG)

if __name__ == '__main__':
    start_time = time.time()
    branch = os.getenv('GIT_BRANCH_NAME')
    if not branch:
        raise Exception(
            'Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

    logger.info(f'{time.time() - start_time} seconds - Starting the extraction of urls ...')
    new_urls = extract_url_dl(no_browser=True,
                              start_date=datetime(2023, 1, 25),
                              end_date=datetime(2023, 1, 27))

    repo = init_repo()

    for massif in MASSIFS:
        file_path = f'data/{massif}/urls_list.txt'
        logger.debug(f'{time.time() - start_time} seconds  - Exporting the URL for massif : {massif}   ...')

        # Update file
        full_content = update_file_content(repo, file_path, branch, new_urls[massif], 'url')

        # Save file locally
        with open(file_path, 'w') as f:
            f.write(full_content)
        logger.debug(f'{time.time() - start_time} seconds - Successfully writing the URLs to urls_list.txt file '
                     f'for massif: {massif}   ...')

    logger.info(f'{time.time() - start_time} seconds - Job succeeded  ...')
