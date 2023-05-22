import os
import pandas as pd
import requests
from sqlalchemy.types import Integer, Text, String, DateTime, Float
from sqlalchemy import create_engine

HTTP_TIMEOUT = 10000

DATA_URL = "https://opendata.rhein-kreis-neuss.de/api/v2/catalog/datasets/rhein-kreis-neuss-flughafen-weltweit/exports/csv"
CSV_PATH = "./data/airports.csv"
SQL_PATH = "/data/airports.sqlite"

def save_url(url, out):
    '''Takes a url and saves the contents to out'''
    file_stream = requests.get(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
    open(out, 'wb').write(file_stream.content)
    
save_url(DATA_URL, CSV_PATH)

df = pd.read_csv(CSV_PATH, delimiter=';', index_col='column_1')
print(df.head())
print(df.info())

print(SQL_PATH)


df.to_sql("airports","sqlite://" + SQL_PATH, if_exists='replace', dtype={
    "column_1": Integer,
    "column_2": Text,
    "column_3": Text,
    "column_4": Text,
    "column_5": String(3),
    "column_6": String(4),
    "column_7": Text,
    "column_8": Text,
    "column_9": Integer,
    "column_10": Text,
    "column_11": Text(1),
    "column_12": String,
    "geo_punkt": String})
