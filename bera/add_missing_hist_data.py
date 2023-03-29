# Ce script a pour but d'être exécuter une seule fois, pour modifier tous les en-têtes des fichers hist. csv pour chacun
# des massifs pour rajouter un champs relatif à l'url de téléchargement pdf des BERAS dnas l'en-tête
import os

import pandas as pd

from bera.utils.bulletin import Bulletin
from bera.utils.github_utils import init_repo, get_remote_file
from bera.utils.common import init_logger, MASSIFS

logger = init_logger()


if __name__ == '__main__':
    branch = os.getenv('GIT_BRANCH_NAME')
    if not branch:
        raise Exception('Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

    repo = init_repo()

    logger.info('Starting the extraction of urls...')

    for massif in MASSIFS:
        file_path = f'data/{massif}/hist.csv'
        logger.info(f'Edit header of hist.csv file for massif : {massif}   ...')
        actual_content = get_remote_file(repo, file_path, branch)

        actual_content = actual_content.replace('\r', '')
        df = pd.DataFrame([x.split(',') for x in actual_content.split('\n')])

        # Define header
        df.columns = df.iloc[0]

        if 'meteo' not in df.columns:
            df['meteo'] = ''

        df = df[1:]

        logger.info(f'Add missing data into hist.csv file for massif : {massif}   ...')
        with open(f"data/{massif}/urls_list.txt", 'r') as urls_list:
            # read all lines using readline()
            lines = urls_list.readlines()
            for row in lines:
                date = row.strip('\n')
                bulletin = Bulletin(massif, date)
                if len(df.query(f'date == "{bulletin.jour_key}"')) == 0:
                    continue
                else:
                    breakpoint()
                    if df.loc[df.date == f"{bulletin.jour_key}", 'url_telechargement'] == '' or \
                            df.loc[df.date == f"{bulletin.jour_key}", 'meteo'] == '':
                        bulletin.download()
                        bulletin.parse_données_risques()
                        bulletin.parse_hist_meteo()
                        new_content = bulletin.append_csv()
                        df.loc[df.date == f"{bulletin.jour_key}"] = new_content

        # Export content
        df.to_csv(file_path, sep=',', index=False)
        with open(file_path, 'r') as f:
            full_content = f.read()

    logger.info(f'Job succeeded   ...')
