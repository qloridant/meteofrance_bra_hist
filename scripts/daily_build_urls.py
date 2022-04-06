import lib.bulletin
import lib.extract
from datetime import today
import os

if __name__ == '__main__':
    # Adding the massif/data information in the file data/urls_list.txt
    extract_url_dl(no_browser=True, start_date=today(), end_date=today())
    # Push the modification on the file
    g = Github(os.environ['GITHUB_TOKEN'])
    g = Github(base_url="https://https://github.com/qloridant/api/v3", login_or_token="access_token")
