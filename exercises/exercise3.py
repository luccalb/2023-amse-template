import pandas as pd

DATA_URL = "https://www-genesis.destatis.de/genesis/downloads/00/tables/46251-0021_00.csv"

df = pd.read_csv(DATA_URL, delimiter=';', encoding='latin1', skiprows=6, skipfooter=4, engine='python')

df = df.iloc[:, [0,1,2,12,22,32,42,52,62,72]]
df.columns = ['date', 'CIN', 'name', 'petrol', 'diesel', 'gas', 'electro', 'hybrid', 'plugInHybrid', 'others']

print(df.head())