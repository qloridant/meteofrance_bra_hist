import logging
import os

import pandas as pd
from github import Github, InputGitTreeElement

from bera.utils.common import PARAMS

logger = logging.getLogger(__name__)


def merge_url_content(actual_content: str, new_content: []):
    # Merge the text from the github file and the newly generated one
    # Sort and veriify constraint unicity
    full_content = actual_content.split('\n') + new_content

    full_content = list(set(full_content))
    full_content = sorted(full_content)
    full_content = '\n'.join(map(lambda x: str(x), full_content))

    return full_content


def merge_bera_content(actual_content: str, new_content: [[]]):
    # Merge the text from the github file and the newly generated one
    # Convert to dataframe to sort and check unicity constraints
    actual_content = actual_content.replace('\r', '')
    df = pd.DataFrame([x.split(',') for x in actual_content.split('\n')])

    # Define header
    df.columns = df.iloc[0]
    # Remove useless spaces in column names that were historically in remote files hist.csv data
    # TODO: delete this code line when all the column names will be cleaned
    df.columns = df.columns.str.replace(' ', '')

    # Add nonexistent columns in remote file
    # Useful for adding new params in hist.csv data files
    for param in PARAMS:
        if param not in df.columns:
            df[param] = ''

    df = df[1:]

     # Add new content
    df_length = len(df)
    for i, line in enumerate(new_content):
        df.loc[df_length + i] = line

    df = df.sort_values('date', ascending=False)
    df = df.drop_duplicates()

    # Export content
    df.to_csv('bera/tmp_dataframe.csv', sep=',', index=False)
    with open('bera/tmp_dataframe.csv', 'r') as f:
        full_content = f.read()
    return full_content


def init_repo():
    g = Github(os.getenv('TOKEN'))

    # Login is specified when running locally
    login = os.getenv('GIT_LOGIN')
    if login:
        user = g.get_user(login=login)
    else:
        user = g.get_user()
    return user.get_repo('meteofrance_bra_hist')


def get_remote_file(repo, file_path, branch):
    file = repo.get_contents(file_path, ref=branch)  # Get file from branch
    return file.decoded_content.decode("utf-8")  # Get raw string data


def update_file_content(repo, path, branch, new_content, type_data) -> str:
    """
    Update file content with adding new content
    """
    actual_content = get_remote_file(repo, path, branch)
    if type_data == 'url':
        full_content = merge_url_content(actual_content, new_content)
    else:  # type_data == "bera"
        full_content = merge_bera_content(actual_content, new_content)
    return full_content


def update_and_add_file_to_commit(repo, file_path, branch, new_content,
                                  type_data, files_to_commit) -> []:
    """
    The function aims to update and add files to a new git commit
     :params:
     repo: GitHub Repository object used
     file_path: str: the path of the file to add in the commit
     branch: str: Repository branch used to fetch and push updated files
     new_content: str: content which will be added to the new file
     type_data: str: {url, bera} Type of files updated
     files_to_commit: list: list of files to commit

     :return:
     file: InputGitTreeElement object: file to add in the commit
    """
    full_content = update_file_content(repo, file_path, branch, new_content,
                                       type_data)
    blob = repo.create_git_blob(full_content, "utf-8")
    file = InputGitTreeElement(path=file_path, mode='100644', type='blob',
                               sha=blob.sha)
    files_to_commit.append(file)
    return files_to_commit


def commit_many_files_and_push(repo, branch, commit_message, files):
    """
    The function commits and pushes all the modification related to a list of files on a branch
    cf doc : https://github.com/Nautilus-Cyberneering/pygithub/blob/main/docs/how_to_create_a_single_commit_with_multiple_files_using_github_api.md
    :params:
    repo: GitHub repository to push new files
    branch: GitHub branch concerned
    commit_message: git commit message
    files: list of InputGitTreeElement objects related to the files to commit
    """

    # Get  parent info
    branch_sha = repo.get_branch(branch).commit.sha
    parent = repo.get_git_commit(sha=branch_sha)

    # Create the tree with the two files. Every file is another tree.
    base_tree = repo.get_git_tree(sha=branch_sha)
    tree = repo.create_git_tree(files, base_tree)

    # Create the commit
    commit = repo.create_git_commit(commit_message, tree, [parent])

    # Get the reference for the branch we are working on
    branch_refs = repo.get_git_ref(f'heads/{branch}')

    # Update the reference to the new commit
    branch_refs.edit(sha=commit.sha)
