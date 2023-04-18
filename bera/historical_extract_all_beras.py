"""
This script aims to extract information from BERAs and save these datas into hist.csv files for all mountain chain,
for a given period, such as:
- risk and its evolution depending on the altitude
- weather measures (weather, isotherms, wind, snow precipitation)
- url of downloading the BERA in pdf format.

This script was useful to get historical datas from old BERAs published before the beginning of this project.

Now this script could be useful if some other information present in the BERAs (like weather, snow
precipitations, ...) are added to the data we want to save in this project, to get all historical new data.

This script:

- for each chain mountain:

    - compiles all the datetimes contained in the file data/<massif>/urls_list.txt in a list,

    - transforms the actual content of the file data/<massif>/hist.csv into a Dataframe object,

    - for each datetime (since the first BERAs published are available in xml format, the 17/12/2018):

        - check if data for parameters meteo and snow precipitation are missing or not,

        - if data for parameters meteo and snow precipitation are missing, downloads the BERA
        corresponding to the datetiem in xml format,

        - parses the xml content into a list of datas (as date, chain mountain, avalanche risk, evolution of the risk
            with altitude, eventuals comments, url to download the BERA in pdf format, meteo), for example
            ['2023-03-29', 'CHABLAIS', '2', '', '<2500', '2500', '3', '', '>2500', '3',
            'Au-dessus de 2500 m : Risque marqué. En-dessous : Risque limité.',
            'https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.CHABLAIS.20230329140534.pdf']

    - updates locally the data/<massif>/hist.csv file content with this Dataframe object updated with new contents.
"""

import logging
import os
import pandas as pd
import subprocess
import time

from utils.bulletin import Bulletin
from utils.common import init_logger, MASSIFS, PARAMS
from utils.github_utils import init_repo, get_remote_file

logger = init_logger(logging.DEBUG)
start_time = time.time()

branch = os.getenv('GIT_BRANCH_NAME')
if not branch:
    raise Exception(
        'Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

repo = init_repo()
files_to_commit = []
for massif in MASSIFS[0:1]:
    # Lecture de la date de publication de notre fichier
    dates_ = subprocess.run(["cat", f"data/{massif}/urls_list.txt"],
                            capture_output=True).stdout.decode('utf-8').split('\n')

    logger.debug(
        f"{time.time() - start_time} seconds  - Add missing data into hist.csv data file for massif {massif} ...")
    file_path = f'data/{massif}/hist.csv'

    # Get the actual content of hist.csv file for this massif
    actual_content = get_remote_file(repo, file_path, branch)
    actual_content = actual_content.replace('\r', '')

    # Transform actual content in an exploitable Dataframe
    df = pd.DataFrame([x.split(',') for x in actual_content.split('\n')])
    df.columns = df.iloc[0]

    # Add new columns names
    for param in PARAMS:
        if param not in df.columns:
            df[param] = ''

    df = df[1:]

    for date_ in dates_:
        if int(date_) >= 20181217143136:  # Datetime of the first xml files for the bera
            # Check if there are missing data in new params for this date
            date = f"{date_[0:4]}-{date_[4:6]}-{date_[6:8]}"
            missing_data = False
            for param in PARAMS[11:]:
                try:
                    if df.loc[df.date == f"{date}", f"{param}"].values[0] == '':
                        missing_data = True
                        break
                except Exception as e:
                    logger.error(
                        f'{time.time() - start_time} seconds - Error occurred for massif {massif} at this date: '
                        f'{date_} in checking missing data: {e}...',
                        exc_info=True)
                    break

            if missing_data:
                try:
                    # Create new_content for this date
                    new_data = []
                    bulletin = Bulletin(massif, date_)
                    bulletin.download()
                    bulletin.parse_donnees_risques()
                    bulletin.parse_donnees_meteo()
                    bulletin.parse_situation_avalancheuse()
                    new_data.append(bulletin.append_csv())

                    # Add new content
                    # logger.debug(f"{time.time() - start_time} seconds - Add datas for massif {massif}, "
                    #              f"date = {date_}...")
                    df.loc[df.date == f"{date}"] = new_data

                except Exception as e:
                    logger.error(
                        f'{time.time() - start_time} seconds - Error occurred for massif {massif} at this date: '
                        f'{date_}: {e}...',
                        exc_info=True)
            else:
                # Do nothing
                continue

    df = df.sort_values('date', ascending=False)
    df = df.drop_duplicates()

    # Export content to hist.csv file
    logger.debug(f"{time.time() - start_time} seconds - Successfully updated hist.csv file for massif: {massif} ...")
    df.to_csv(file_path, sep=',', index=False)

logger.info(f"{time.time() - start_time} seconds - Job succeeded  ...")
