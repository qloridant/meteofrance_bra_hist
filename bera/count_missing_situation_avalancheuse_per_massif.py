"""
This script aims to calculate the percentage of data filled for situation_avalancheuse_typique paramater per
mountain chain in the data file hist.csv.
It logs this information per mountain chain and for all mountain chains.
"""

import logging
import os
import time

import pandas as pd

from bera.utils.common import init_logger, MASSIFS, PARAMS
from bera.utils.github_utils import init_repo, get_remote_file

logger = init_logger(logging.DEBUG)
start_time = time.time()

branch = os.getenv('GIT_BRANCH_NAME')
if not branch:
    raise Exception('Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

repo = init_repo()
files_to_commit = []

logger.info('Calcule les pourcentage de données complétées pour le paramètre situation_avalancheuse_typique '
            'par massif...')

percentage_filled_values_per_massif = {}

for massif in MASSIFS:
    file_path = f'data/{massif}/hist.csv'

    # Get the actual content of hist.csv file for this massif
    actual_content = get_remote_file(repo, file_path, branch)
    actual_content = actual_content.replace('\r', '')

    # Transform actual content in an exploitable Dataframe
    df = pd.DataFrame([x.split(',') for x in actual_content.split('\n')])
    df.columns = df.iloc[0]

    # Add missing columns
    for param in PARAMS:
        if param not in df.columns:
            df[param] = ''

    filled_values = (df.situation_avalancheuse_typique != '').sum()

    total_row_count = df.date.count()
    pourcentage_filled_value = int(filled_values / total_row_count * 100)
    percentage_filled_values_per_massif[massif] = pourcentage_filled_value
    logger.info(f"Massif {massif} = {pourcentage_filled_value} % ")

pourcentage_filled_value_global = \
    int(sum(percentage_filled_values_per_massif.values())/len(percentage_filled_values_per_massif))
logger.info(f"Tous massifs confondus = {pourcentage_filled_value_global} %")
logger.info("Job succeeded  ...")
