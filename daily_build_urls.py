# Ce script doit etre executé a partir de 16h.
import sys
from utils.extract import extract_url_dl
from utils.github import push, init_repo, get_remote_file
from datetime import date, timedelta

if __name__ == '__main__':
    new_urls = extract_url_dl(no_browser=True, start_date=date.today() + timedelta(days=-1), end_date=date.today() + timedelta(days=-1))

    file_path = 'data/urls_list.txt'
    branch = 'master'
    repo = init_repo()
    hist_urls = get_remote_file(repo, file_path, branch)
    push(repo, file_path, "Daily automatic file update", hist_urls + new_urls, branch, update=True)
