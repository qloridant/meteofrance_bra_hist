"""
This script aims to add new BERA information from the last BERA published for each mountain chain, and save it into all
the data/<massif>/hist.csv files in the 'master' branch of the GitHub repository
https://github.com/qloridant/meteofrance_bra_hist.

This script is executed daily after the execution of the script daily_build_url.py by the GitHub main action defined in
the .github/workflows/main.yml file of this project.

This scripts:

- for each chain mountain:

    - reads the file data/<massif>/urls_list.txt in the GitHub repository
      https://github.com/qloridant/meteofrance_bra_hist to get the last datetime written in it. This datetime
      corresponds to the last datetime of BERA publication for this chain mountain,

    - downloads the last BERA available in xml format thanks to the th last datetime of BERA publication get previously,

    - parses the xml content into a list of datas (as date, chain mountain, avalanche risk, evolution of the risk with
    altitude, eventuals comments, url to download the BERA in pdf format), for example
      ['2023-03-29', 'CHABLAIS', '2', '', '<2500', '2500', '3', '', '>2500', '3',
       'Au-dessus de 2500 m : Risque marqué. En-dessous : Risque limité.',
       'https://donneespubliques.meteofrance.fr/donnees_libres/Pdf/BRA/BRA.CHABLAIS.20230329140534.pdf']

    - gets the file data/<massif>/hist.csv in the GitHub repository
      https://github.com/qloridant/meteofrance_bra_hist,

    - updates the data/<massif>/hist.csv file content by adding this list of new datas at the beginning of the
      actual content,

- creates a git commit including all updated files,

- pushes the git commit in the 'master' branch of the GitHub repository
https://github.com/qloridant/meteofrance_bra_hist

This script could be launched in a development context, independently of the GitHub action, but it should be executed
after the execution of the script daily_build_urls.py to get the new BERA datetime publication.
Cf README.md in section 'Developpement' to launch this script in a development context.
"""

import os
import subprocess

from bera.utils.bulletin import Bulletin
from bera.utils.common import init_logger, MASSIFS
from bera.utils.github_utils import init_repo, commit_many_files_and_push, \
    update_and_add_file_to_commit

logger = init_logger()

branch = os.getenv('GIT_BRANCH_NAME')
if not branch:
    raise Exception('Unknown environment variable GIT_BRANCH_NAME - Stopping here  ...')

repo = init_repo()
files_to_commit = []

logger.info('Starting the daily extract...')

for massif in MASSIFS:
    # Lecture de la date de publication de notre fichier
    jour = subprocess.run(["tail", "-n", "1", f"data/{massif}/urls_list.txt"],
                          capture_output=True).stdout.decode('utf-8')

    # Traitement du fichier
    bulletin = Bulletin(massif, jour)
    bulletin.download()
    bulletin.parse_donnees_risques()
    bulletin.parse_donnees_meteo()
    bulletin.parse_situation_avalancheuse()
    new_data = bulletin.append_csv()

    file_path = f'data/{massif}/hist.csv'
    logger.info(f'Exporting the BERA to Github for massif : {massif}   ...')

    # Update and add files to commit
    files_to_commit = update_and_add_file_to_commit(repo, file_path, branch,
                                                    [new_data], 'bera',
                                                    files_to_commit)

logger.info('Compile all modified files in one commit  ...')
commit_many_files_and_push(repo, branch, "Daily automatic csv files update",
                           files_to_commit)
logger.info('Job succeeded  ...')
