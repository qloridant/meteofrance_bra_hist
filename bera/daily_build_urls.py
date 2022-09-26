# Ce script doit etre executé a partir de 16h (heure de publication)
from datetime import date
from bera.utils.extract import extract_url_dl
from bera.utils.github import push, init_repo
from bera.utils.common import init_logger, MASSIFS

logger = init_logger()


if __name__ == '__main__':
    print(MASSIFS)
    logger.info('Starting the extraction of urls...')
    new_urls = extract_url_dl(no_browser=True, start_date=date.today(), end_date=date.today())

    branch = 'master'
    repo = init_repo()

    for massif in MASSIFS:
        file_path = f'data/{massif}/urls_list.txt'
        logger.info(f'Exporting the URL to Github for massif : {massif}   ...')
        push(repo, file_path, "Daily automatic file update", new_urls[massif], branch, update=True)
