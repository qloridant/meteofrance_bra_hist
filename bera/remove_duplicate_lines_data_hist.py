# Ce script a pour but d'être exécuter une seule fois pour supprimer les lignes qui ont été créée en doublon lors du
# rajout de la donnée de l'url de telechargelent des BERAS dnas les fichiers hist.csv
import os
import pandas as pd

from bera.utils.github import init_repo, get_remote_file
from bera.utils.common import init_logger, MASSIFS

logger = init_logger()


if __name__ == '__main__':
    branch = os.getenv('GIT_BRANCH_NAME')
    if not branch:
        raise Exception(
            'Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

    repo = init_repo()

    for massif in MASSIFS:
        file_path = f'data/{massif}/hist.csv'
        logger.info(f'Edit header of hist.csv file for massif : {massif}   ...')
        actual_content = get_remote_file(repo, file_path, branch)

        actual_content = actual_content.replace('\r', '')
        df = pd.DataFrame([x.split(',') for x in actual_content.split('\n')])

        # Define header
        df.columns = df.iloc[0]
        df = df[1:]

        df['url_telechargement'] = df['url_telechargement'].replace('', None)
        logger.info(f'Remove duplicate lines for massif : {massif}   ...')
        df = df.dropna()

        # Export content
        df.to_csv(file_path, sep=',', index=False)
        with open(file_path, 'r') as f:
            full_content = f.read()

    logger.info(f'Job succeeded   ...')
