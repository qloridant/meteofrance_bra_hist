"""
This script aims to format some wrongly formatted information such as wind and isotherms data in hist.csv file.

This script will be useless when all hist.csv files will be formatted.
TODO: delete this script when all hist.csv files are correctly formatted

This script:

- for each chain mountain:

    - compiles all the datetimes contained in the file data/<massif>/urls_list.txt in a list,

    - transforms the actual content of the file data/<massif>/hist.csv into a Dataframe object,

    - for each datetime (since the first BERAs published are available in xml format, the 17/12/2018):

        - check if data for parameters meteo and snow precipitation are correctly formatted or not,

        - if data for parameters meteo and snow precipitation are wrongly formatted, format the data,

    - updates locally the data/<massif>/hist.csv file content with this Dataframe object updated with formatted data.
"""

import logging
import os
import re

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
for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    dates_ = subprocess.run(["cat", f"data/{massif}/urls_list.txt"],
                            capture_output=True).stdout.decode('utf-8').split('\n')

    logger.debug(
        f"{time.time() - start_time} seconds  - Format data into hist.csv data file for massif {massif} ...")
    file_path = f'data/{massif}/hist.csv'

    # Get the actual content of hist.csv file for this massif
    actual_content = get_remote_file(repo, file_path, branch)
    actual_content = actual_content.replace('\r', '')

    # Transform actual content in an exploitable Dataframe
    df = pd.DataFrame([x.split(',') for x in actual_content.split('\n')])
    df.columns = df.iloc[0]
    df = df[1:]

    for date_ in dates_:
        if int(date_) >= 20181217143136:  # Datetime of the first xml files for the bera

            # Check if there are missing data in new params for this date
            date = f"{date_[0:4]}-{date_[4:6]}-{date_[6:8]}"

            try:
                for hour in ['00', '06', '12']:
                    if df.loc[df.date == f"{date}", f"{hour}_altitude_vent_2"].values[0] == '9999':
                        df.loc[df.date == f"{date}", f"{hour}_altitude_vent_2"] = 'Sans objet'
                        df.loc[df.date == f"{date}", f"{hour}_direction_vent_altitude_2"] = 'Sans objet'
                        df.loc[df.date == f"{date}", f"{hour}_vitesse_vent_altitude_2"] = 'Sans objet'

                for param in PARAMS[11:]:
                    if df.loc[df.date == f"{date}", f"{param}"].values[0] == '-1' or \
                            df.loc[df.date == f"{date}", f"{param}"].values[0] == '' or \
                            df.loc[df.date == f"{date}", f"{param}"].values[0] == ' - ':
                        df.loc[df.date == f"{date}", f"{param}"] = 'Absence de données'

            except Exception as e:
                logger.error(
                    f'{time.time() - start_time} seconds - Error occurred for massif {massif} at this date: '
                    f'{date_} in checking missing data: {e}...',
                    exc_info=True)

    df = df.sort_values('date', ascending=False)
    df = df.drop_duplicates()

    # Export content to hist.csv file
    logger.debug(f"{time.time() - start_time} seconds - Successfully updated hist.csv file for massif: {massif} ...")
    df.to_csv(file_path, sep=',', index=False)

logger.info(f"{time.time() - start_time} seconds - Job succeeded  ...")
