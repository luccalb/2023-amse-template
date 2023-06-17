import pandas as pd
from sqlalchemy.types import Integer, Text, String, Float


DATA_URL = "https://www-genesis.destatis.de/genesis/downloads/00/tables/46251-0021_00.csv"
SQL_PATH = "/cars.sqlite"


df = pd.read_csv(DATA_URL, delimiter=';', encoding='latin1', skiprows=6, skipfooter=4, engine='python')

df = df.iloc[:, [0,1,2,12,22,32,42,52,62,72]]
df.columns = ['date', 'CIN', 'name', 'petrol', 'diesel', 'gas', 'electro', 'hybrid', 'plugInHybrid', 'others']

# convert CIN column to string because of possible leading zero
df['CIN'] = df['CIN'].astype(str)

# drop empty cells
df.dropna(inplace=True)


# validate CIN numbers
df = df[df['CIN'].str.match(r"[0-9]{4,5}")]

print(df.info())

# save data to sqlite db, setting the correct types
df.to_sql("carrs","sqlite://" + SQL_PATH, if_exists='replace', dtype={
    "date": Text,
    "CIN": String(5),
    "name": Text,
    "petrol": Integer,
    "diesel": Integer,
    "gas": Integer,
    "electro": Integer,
    "hybrid": Integer,
    "plugInHybrid": Integer,
    "others": Integer})