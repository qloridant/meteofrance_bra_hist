import glob
import os

import pandas as pd
from github import InputGitTreeElement

from bera.utils.common import init_logger
from bera.utils.github_utils import init_repo, commit_many_files_and_push

logger = init_logger()

if __name__ == '__main__':
    branch = os.getenv('GIT_BRANCH_NAME')
    if not branch:
        raise Exception('Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

    repo = init_repo()

    files_to_merge = []

    logger.info('Merge all csv files...')
    # merging the files
    files_joined = os.path.join('data/', "*/hist.csv")

    # Return a list of all joined files
    list_files = glob.glob(files_joined)

    logger.info("Merging all csv files into a single pandas dataframe ...")
    # Merge files by joining all files
    dataframe = pd.concat(map(pd.read_csv, list_files), ignore_index=True)
    dataframe.to_csv('data/tmp_hist_bera.csv', sep=',', index=False)
    with open('data/tmp_hist_bera.csv', 'r') as f:
        full_content = f.read()

    logger.info("Add the new file into a commit and push ...")
    blob = repo.create_git_blob(full_content, "utf-8")
    file = InputGitTreeElement(path='data/hist_bera.csv', mode='100644', type='blob',
                               sha=blob.sha)
    commit_many_files_and_push(repo, branch, "First try: Merge all hist.csv files in one single file hist_bera.csv", [file])
    logger.info("Job succeeded")
