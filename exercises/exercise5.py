import urllib.request
import zipfile
import re
import pandas as pd
from sqlalchemy.types import Integer, Text, Float


DATA_URL = "https://gtfs.rhoenenergie-bus.de/GTFS.zip"
DATA_FILE_NAME = "stops.txt"
COLUMNS = ["stop_id", "stop_name", "stop_lat", "stop_lon", "zone_id"]
UMLAUTE = ["ä", "ü", "ö"]
SQL_PATH = "/gtfs.sqlite"


filehandle, _ = urllib.request.urlretrieve(DATA_URL, "./tmp/GTFS.zip")

zip_obj = zipfile.ZipFile(filehandle, "r")

stops_file = zip_obj.open(DATA_FILE_NAME)

stops_df = pd.read_csv(stops_file)

# whitelist columns
stops_df = stops_df[COLUMNS]

# cleaning
# 1) only keep columns where stop_name contains an umlaut
stops_df = stops_df[stops_df["stop_name"].str.contains("|".join(UMLAUTE), regex=True, flags=re.IGNORECASE)]

# 2) validate lat/long range
stops_df = stops_df[stops_df["stop_lat"] <= 90]
stops_df = stops_df[stops_df["stop_lat"] >= -90]
stops_df = stops_df[stops_df["stop_lon"] <= 90]
stops_df = stops_df[stops_df["stop_lon"] >= -90]




print(stops_df.info())
print(stops_df.head())
print(stops_df.shape)
    
# save data to sqlite db, setting the correct types
stops_df.to_sql("stops","sqlite://" + SQL_PATH, if_exists='replace', dtype={
    "stop_id": Integer,
    "stop_name": Text,
    "stop_lat": Float,
    "stop_lon": Float,
    "zone_id": Integer}, index=False)
