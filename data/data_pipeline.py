"""
An automated data pipeline, analysing the correlation between per capita gdp and share of EVs
among all newly registered vehicles in german states.
"""

import json
import requests
import argparse
import pandas as pd

CONFIG_FILE = "./pipeline_config.json"
RAW_FILES_FOLDER = "./raw"
CLEANED_FILES_FOLDER = "./clean"
HTTP_TIMEOUT = 10000

def save_url(url, out):
    '''Takes a url and saves the contents to out'''
    file_stream = requests.get(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
    open(out, 'wb').write(file_stream.content)

with open(CONFIG_FILE, encoding='UTF-8') as config_json:
    config = json.load(config_json)

# Step 0.1 - Parse program arguments

arg_parser = argparse.ArgumentParser()

# while developing, it's not necessary to reload the files every time
arg_parser.add_argument('-r', '--refresh',
                        action='store_true',
                        help='force re-downloading the datasets')

args = arg_parser.parse_args()


#
# Step 1 - Check new file availability
#

# TODO

#
# Step 2 - Download all relevant raw datasets
#

vr_download_location = config['download_locations']['vehicle_registrations']
gdp_download_location = config['download_locations']['gdp_per_capita']

if args.refresh:
    # download the dataset for new vehicle registrations
    vr_url = config['dataset_urls']['vehicle_registrations']
    save_url(vr_url, vr_download_location)

    # downlaod the dataset for gdp per capita
    gdp_url = config['dataset_urls']['gdp_per_capita']
    save_url(gdp_url, gdp_download_location)

#
# Step 3 - Find relevant data in files and save to sqlite DB
#

# 3.1 Load and save GDP data

# find the sheet named '3.3' which contains the data we are interested in
# (gdp per capita grouped by state)

gdp_df = pd.read_excel(gdp_download_location, sheet_name='3.3', usecols='A:Q', skiprows=2)

# remove the newline characters in state names
gdp_df.columns = gdp_df.columns.str.replace('\n', '')
# manuall rename two columns
gdp_df.columns = gdp_df.columns.str.replace('Branden-burg', 'Brandenburg')
gdp_df.columns = gdp_df.columns.str.replace('Nieder-sachsen', 'Niedersachsen')



# find the correct row for the current year
gdp_df = gdp_df[gdp_df['Jahr'] == 2022].iloc[0]

print(gdp_df.head())

# 3.2 Load and save vehicle data

vr_df = pd.read_excel(vr_download_location,
                      sheet_name='FZ 8.6',
                      usecols='B:Q',
                      skiprows=7,
                      nrows=17,
                      index_col=0)
# remove the newline characters in state names
vr_df.columns = vr_df.columns.str.replace('\n', ' ')
vr_df = vr_df[['Elektro (BEV)', 'Hybrid', 'Insgesamt']]
vr_df['anteil_elektro'] = (vr_df['Elektro (BEV)'] + vr_df['Hybrid']) / vr_df['Insgesamt']
vr_df = vr_df.dropna()

vr_df['gdp_per_capita'] = gdp_df
print(vr_df.index)

# save to local sqlite instance
vr_df.to_sql('evs_per_capita', 'sqlite:///clean/evs_per_capita.sqlite', if_exists='replace', index=True)