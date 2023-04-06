import logging
import os
from typing import Any

import pandas as pd
from github import Github, InputGitTreeElement, Repository, Branch

from bera.utils.common import PARAMS

logger = logging.getLogger(__name__)


def merge_url_content(actual_content: str, new_content: []) -> str:
    """
    This function aims to concatenate the actual concatenate of the urls_list.txt file with the new content
    corresponding to the new url datetime used in downloading the new bera

    Parameters
    ----------
    actual_content: str: the actuel content of the urls_list.txt data file
    new_content: list of str element (containing one single element), for example ['20230327140239']

    Returns
    -------
    full_content: str: the full content of the urls_list.txt updated file
    """
    # Merge the text from the github file and the newly generated one
    # Sort and veriify constraint unicity
    full_content = actual_content.split('\n') + new_content

    full_content = list(set(full_content))
    full_content = sorted(full_content)
    full_content = '\n'.join(map(lambda x: str(x), full_content))

    return full_content


def merge_bera_content(actual_content: str, new_content: [[]]) -> str:
    """
    This function aims to concatenate the actual contenate of an hist.csv data file with the new content extracted from
    a new BERA

    Parameters
    ----------
    actual_content: str: the actuel content of the hist.csv data file
    new_content: [[]]: list of list of str elements used in extracting beras,
                 for example [['2023-03-27', 'CHABLAIS', '2', '', '<1800', '1800', '3', '', '>1800', '3',
                         'Au-dessus de 1800 m : Risque marqué. En-dessous : Risque limité.',
                         'https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.CHABLAIS.20230327140239.pdf'
                      ]]

    Returns
    -------
    full_content: str: the full content of the hist.csv data updated file
    """
    # Merge the text from the github file and the newly generated one
    # Convert to dataframe to sort and check unicity constraints
    actual_content = actual_content.replace('\r', '')
    df = pd.DataFrame([x.split(',') for x in actual_content.split('\n')])

    # Define header
    df.columns = df.iloc[0]

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


def init_repo() -> Repository:
    """
    Get the remote GitHub repository https://github.com/qloridant/meteofrance_bra_hist

    Returns
    -------
    GitHub Repository object
    """
    g = Github(os.getenv('TOKEN'))

    # Login is specified when running locally
    login = os.getenv('GIT_LOGIN')
    if login:
        user = g.get_user(login=login)
    else:
        user = g.get_user()
    return user.get_repo('meteofrance_bra_hist')


def get_remote_file(repo: Repository, file_path: str, branch: Branch) -> str:
    """
    Get a specific file thanks to its file_path, from a branch given in parameter, into a specific GitHub repository
    given in paramater

    Parameters
    ----------
    repo: GitHub Repository object used
    file_path: str: the path of the remote file
    branch: str: Repository branch used to fetch and push updated files

    Returns
    -------
    str: decoded content of the remote file

    """
    file = repo.get_contents(file_path, ref=branch)  # Get file from branch
    return file.decoded_content.decode("utf-8")  # Get raw string data


def update_file_content(repo: Repository, file_path: str, branch: Branch, new_content: Any, type_data: str) -> str:
    """
    Update file content with adding new content to the actual content

    Parameters
    ----------
    repo: GitHub Repository object used
    file_path: str: the path of the file to add in the commit
    branch: str: Repository branch used to fetch and push updated files
    new_content: Any: content which will be added to the actual content:
        - either []: list of str element (containing one single element corresponding to the datetime of the BERA's
          publication) when used in building url (in daily_build_urls script or historical_build_urls script),
          for example ['20230327140239']
        - either [[]]: list of list of str elements when used in extracting beras (in daily_extract_all_beras script
          or hitsorical_extract_all_beras script),
          for examples [['2023-03-27', 'CHABLAIS', '2', '', '<1800', '1800', '3', '', '>1800', '3',
                         'Au-dessus de 1800 m : Risque marqué. En-dessous : Risque limité.',
                         'https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.CHABLAIS.20230327140239.pdf'
    type_data: str: {url, bera} Type of files updated

    Returns
    -------
    full_content: str: full expected content which will be stored in the file to commit
    """
    actual_content = get_remote_file(repo, file_path, branch)
    if type_data == 'url':
        full_content = merge_url_content(actual_content, new_content)
    else:  # type_data == "bera"
        full_content = merge_bera_content(actual_content, new_content)
    return full_content


def update_and_add_file_to_commit(repo: Repository, file_path: str, branch: Branch, new_content: Any, type_data: str,
                                  files_to_commit: []) -> Any:
    """
    The function aims to update and add files to a new git commit

    Parameters
    ----------
    repo: GitHub Repository object used
    file_path: str: the path of the file to add in the commit
    branch: str: Repository branch used to fetch and push updated files
    new_content: Any: content which will be added to the updated file to commit:
        - either []: list of str element (containing one single element corresponding to the datetime of the BERA's
          publication) when used in building urls,
          for example ['20230327140239']
        - either [[]]: list of list of str elements when used in extracting beras,
          for examples [['2023-03-27', 'CHABLAIS', '2', '', '<1800', '1800', '3', '', '>1800', '3',
                         'Au-dessus de 1800 m : Risque marqué. En-dessous : Risque limité.',
                         'https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.CHABLAIS.20230327140239.pdf'
                       ]]
    type_data: str: {url, bera} Type of files updated
    files_to_commit: list of InputGitTreeElement objects: list of files to commit

    Returns
    -------
    file: InputGitTreeElement object: file to add in the commit
    """
    full_content = update_file_content(repo, file_path, branch, new_content,
                                       type_data)
    blob = repo.create_git_blob(full_content, "utf-8")
    file = InputGitTreeElement(path=file_path, mode='100644', type='blob',
                               sha=blob.sha)
    files_to_commit.append(file)
    return files_to_commit


def commit_many_files_and_push(repo: Repository, branch: Branch, commit_message: str, files: []):
    """
    The function commits and pushes all the modification related to a list of files on a branch
    cf doc : https://github.com/Nautilus-Cyberneering/pygithub/blob/main/docs/how_to_create_a_single_commit_with_multiple_files_using_github_api.md

    Parameters
    ----------
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
