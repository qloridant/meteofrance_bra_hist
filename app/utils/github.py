import os
from github import Github, NamedUser

def init_repo():
    # TODO catch error if no data yet availble
    print(os.getenv('TOKEN'))
    g = Github(os.getenv('TOKEN'))
    return g.get_user().get_repo('meteofrance_bra_hist')

def get_remote_file(repo, file_path, branch):
    file = repo.get_contents(file_path, ref=branch)  # Get file from branch
    return file.decoded_content.decode("utf-8")  # Get raw string data


def push(repo, path, message, content, branch, update=False):
    source = repo.get_branch("master")
    # repo.get_git_ref(ref=f"refs/heads/{branch}")
    # repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source.commit.sha)  # Create new branch from master
    if update:  # If file already exists, update it
        contents = repo.get_contents(path, ref=branch)  # Retrieve old file to get its SHA and path
        repo.update_file(contents.path, message, content, contents.sha, branch=branch,)  # Add, commit and push branch
    else:  # If file doesn't exist, create it
        repo.create_file(path, message, content, branch=branch, author=author)  # Add, commit and push branch
