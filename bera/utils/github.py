import os
import pandas as pd
import logging
from github import Github

logger = logging.getLogger(__name__)


def merge_url_content(actual_content: str, new_content: []):
    # Merge the text from the github file and the newly generated one
    # Sort and veriify constraint unicity
    full_content = actual_content.split('\n') + new_content

    full_content = list(set(full_content))
    full_content = sorted(full_content)
    full_content = '\n'.join(map(lambda x:str(x), full_content))

    return full_content


def merge_bera_content(actual_content: str, new_content: [[]]):
    # Merge the text from the github file and the newly generated one
    # Convert to dataframe to sort and check unicity constraints
    actual_content = actual_content.replace('\r', '')
    df = pd.DataFrame([x.split(',') for x in actual_content.split('\n')])

    # Define header
    df.columns = df.iloc[0]
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
    # TODO catch error if no data yet availble
    g = Github(os.getenv('TOKEN'))
    return g.get_user().get_repo('meteofrance_bra_hist')


def get_remote_file(repo, file_path, branch):
    file = repo.get_contents(file_path, ref=branch)  # Get file from branch
    return file.decoded_content.decode("utf-8")  # Get raw string data


def push(repo, path, message, new_content, branch, update=False, type_data='url'):
    source = repo.get_branch(branch)
    if update:  # If file already exists, update it
        contents = repo.get_contents(path, ref=branch)  # Retrieve old file to get its SHA and path
        actual_content = get_remote_file(repo, path, branch)
        if type_data == 'url':
            full_content = merge_url_content(actual_content, new_content)
        else:
            full_content = merge_bera_content(actual_content, new_content)
        repo.update_file(contents.path, message, full_content, contents.sha, branch=branch)  # Add, commit and push branch
    else:  # If file doesn't exist, create it
        repo.create_file(path, message, new_content, branch=branch)  # Add, commit and push branch
