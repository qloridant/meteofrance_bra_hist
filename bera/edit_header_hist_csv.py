# Ce script a pour but d'être exécuter une seule fois, pour modifier tous les en-têtes des fichers hist. csv pour chacun
# des massifs pour rajouter un champs relatif à l'url de téléchargement pdf des BERAS dnas l'en-tête
from datetime import date

import pandas as pd

from bera.utils.bulletin import Bulletin
from bera.utils.github import init_repo, get_remote_file
from bera.utils.common import init_logger, MASSIFS

logger = init_logger()


if __name__ == '__main__':
    print(MASSIFS)
    logger.info('Starting the extraction of urls...')

    branch = 'master'
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

        df[' url_telechargement_pdf_bera'] = ''

        logger.info(f'Add url of download pdf bera into hist.csv file for massif : {massif}   ...')
        with open(f"data/{massif}/urls_list.txt", 'r') as urls_list:
            # read all lines using readline()
            lines = urls_list.readlines()
            for row in lines:
                date = row.strip('\n')
                bulletin = Bulletin(massif, date)
                if len(df.query(f'date == "{bulletin.jour_key}"')) == 0:
                    continue
                else:
                    download_url_pdf_bera = f"{bulletin.url}.{bulletin.massif}.{bulletin.jour}.pdf"
                    df_date = df.query(f'date == "{bulletin.jour_key}"')

                    df.loc[df.date == f"{bulletin.jour_key}", ' url_telechargement_pdf_bera'] = download_url_pdf_bera

        # Export content
        df.to_csv(file_path, sep=',', index=False)
        with open(file_path, 'r') as f:
            full_content = f.read()

    logger.info(f'Job succeeded   ...')
