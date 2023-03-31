"""
This script aims to get the last datetime of BERA publication for all mountain chains, and save it into all the
data/<massif>/urls_list.txt files in the 'master' branch of the GitHub repository
https://github.com/qloridant/meteofrance_bra_hist.

This script is executed daily at 17h UTC by the GitHub main action defined in the
.github/workflows/main.yml file of this project.

This scripts:

- gets the last datetime of the BERAs' publication which is normally the same datetime for all chain
  mountains ("massif" in French).

- for each chain mountain:

    - gets the file data/<massif>/urls_list.txt in the GitHub repository
      https://github.com/qloridant/meteofrance_bra_hist,

    - updates the data/<massif>/urls_list.txt file content by adding the new datetime of the last BERA publication at
      the end of the actual content,

- creates a git commit including all updated files,

- pushes the git commit in the 'master' branch of the GitHub repository https://github.com/qloridant/meteofrance_bra_hist

This script could be launched in a development context, independently of the GitHub action, but it should be executed
after 16h (time of BERAs publication) to get the new BERA datetime publication.
Cf README.md in section 'Developpement' to launch this script in a development context.
"""

import os
from datetime import date

from bera.utils.common import init_logger, MASSIFS
from bera.utils.extract import extract_url_dl
from bera.utils.github_utils import init_repo, commit_many_files_and_push, \
    update_and_add_file_to_commit

logger = init_logger()

if __name__ == '__main__':

    branch = os.getenv('GIT_BRANCH_NAME')
    if not branch:
        raise Exception('Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

    logger.info('Starting the extraction of urls...')
    new_urls = extract_url_dl(no_browser=True, start_date=date.today(),
                              end_date=date.today())

    repo = init_repo()
    files_to_commit = []

    for massif in MASSIFS:
        file_path = f'data/{massif}/urls_list.txt'
        logger.info(f'Exporting the URL to Github for massif : {massif}   ...')

        files_to_commit = update_and_add_file_to_commit(repo, file_path,
                                                        branch,
                                                        new_urls[massif],
                                                        'url', files_to_commit)

    logger.info('Compile all modified files in one commit  ...')
    commit_many_files_and_push(repo, branch,
                               "Daily automatic url files update",
                               files_to_commit)
    logger.info('Job succeeded  ...')
