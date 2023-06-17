import pandas as pd
from sqlalchemy.types import Integer, Text, String, Float


DATA_URL = "https://www-genesis.destatis.de/genesis/downloads/00/tables/46251-0021_00.csv"
SQL_PATH = "/cars.sqlite"


df = pd.read_csv(DATA_URL, delimiter=';', encoding='latin1', skiprows=6, skipfooter=4, engine='python')

# select only requested columns
df = df.iloc[:, [0,1,2,12,22,32,42,52,62,72]]
# rename coulmns as requested
df.columns = ['date', 'CIN', 'name', 'petrol', 'diesel', 'gas', 'electro', 'hybrid', 'plugInHybrid', 'others']

# drop empty cells
df = df.dropna(how='any', subset=df.columns)

# drop all rows with value '-'
for col in df.columns:
    df = df[df[col] != '-']
    
print(df.head())
print(df.info())

# convert CIN column to string because of possible leading zero
df = df.astype({'date': 'str',
                'CIN': 'str',
                'name': 'str',
                'petrol': 'int32',
                'diesel': 'int32',
                'gas': 'int32',
                'electro': 'int32',
                'hybrid': 'int32',
                'plugInHybrid': 'int32',
                'others': 'int32'})



# validate CIN numbers
df = df[df['CIN'].str.match(r"[0-9]{4,5}")]
# pad with leading zeros
df['CIN'] = df['CIN'].str.zfill(5)



# validate all integer columns > 0
int_cols = ['petrol', 'diesel', 'gas', 'electro', 'hybrid', 'plugInHybrid', 'others']
df[int_cols] = df[int_cols][df[int_cols] > 0]


# save data to sqlite db, setting the correct types
df.to_sql("cars","sqlite://" + SQL_PATH, if_exists='replace', dtype={
    "date": Text,
    "CIN": String(5),
    "name": Text,
    "petrol": Integer,
    "diesel": Integer,
    "gas": Integer,
    "electro": Integer,
    "hybrid": Integer,
    "plugInHybrid": Integer,
    "others": Integer}, index=False)