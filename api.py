import datetime
from csv import DictReader

from fastapi import FastAPI

from bera.utils.bulletin import Bulletin

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Bienvenue dans l'API de récupération de l'historique des données des bulletins d'estimations "
                       "des risques d'avalanche"}


@app.get("/BERAS/{massif}/{date}")
async def get_bera_massif_date(massif: str, date: str):
    # TODO : gérer les différentes format de la date
    # TODO : Rajouter message erreur si données du BERA pas dispo pour cette date

    bera = {}
    # Get BERA data from hist.csv files
    with open(f"data/{massif}/hist.csv", newline='') as csvfile:
        csv_dict_reader = DictReader(csvfile)
        for row in csv_dict_reader:
            if row['date'].replace('-', '') == date:
                bera = row
            else:
                continue

    results = {
        "massif": massif,
        "beras": [
            bera
        ]
    }

    return results


@app.get("/BERAS/{massif}/")
async def get_bera_massif_date(massif: str, start_date: str = '20100101', end_date: str = '22000103'):
    # TODO : gérer les différentes format des start_date et end_date

    beras = []

    # Get BERA data from hist.csv files
    with open(f"data/{massif}/hist.csv", newline='') as csvfile:
        csv_dict_reader = DictReader(csvfile)
        for row in csv_dict_reader:
            date = row['date']  # Au format str YYYY-mm-dd
            try:
                if is_date_between_start_date_and_end_date(date, start_date, end_date):
                    beras.append(row)
                else:
                    continue
            except Exception as e:
                print(e)

    results = {
        "massif": massif,
        "beras": beras
    }
    return results


def is_date_between_start_date_and_end_date(date: str, start_date: str, end_date: str) -> bool:
    """
    params:
    date: str : at format YYYY-mm-dd
    start_date: str : at format YYYYmmdd
    end_date: str : at format YYYYmmdd
    return:
    boolean : true if a date is included in the dates' interval [start_date ; end_date], false either
    """
    date_dt = datetime.datetime.strptime(date, '%Y-%m-%d')
    start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d')
    return start_date_dt <= date_dt <= end_date_dt
