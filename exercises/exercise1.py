# imports
import pandas as pd
from sqlalchemy.types import Integer, Text, String, Float

# define constants
HTTP_TIMEOUT = 10000
DATA_URL = "https://opendata.rhein-kreis-neuss.de/api/v2/catalog/datasets/rhein-kreis-neuss-flughafen-weltweit/exports/csv"
SQL_PATH = "/airports.sqlite"


# download the raw data
df = pd.read_csv(DATA_URL, delimiter=';', index_col='column_1')
# print(df.head())
# print(df.info())

# print(SQL_PATH)

# save data to sqlite db, setting the correct types
df.to_sql("airports","sqlite://" + SQL_PATH, if_exists='replace', dtype={
    "column_1": Integer,
    "column_2": Text,
    "column_3": Text,
    "column_4": Text,
    "column_5": String(3),
    "column_6": String(4),
    "column_7": Float,
    "column_8": Float,
    "column_9": Integer,
    "column_10": Float,
    "column_11": Text(1),
    "column_12": String,
    "geo_punkt": String})
