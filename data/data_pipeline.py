"""
An automated data pipeline, analysing the correlation between per capita gdp and share of EVs
among all newly registered vehicles in german states.
"""

import os
import json
import argparse
import requests
import pandas as pd
from sqlalchemy.types import Integer, Text, Float

abs_path = os.path.dirname(__file__)


CONFIG_FILE = os.path.join(abs_path, "pipeline_config.json")
RAW_FILES_FOLDER = os.path.join(abs_path, "raw")
CLEANED_FILES_FOLDER = os.path.join(abs_path, "clean")
HTTP_TIMEOUT = 10000

def save_url(url, out):
    '''Takes a url and saves the contents to out'''
    file_stream = requests.get(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
    open(out, 'wb').write(file_stream.content)

if __name__ == '__main__':

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

    vr_download_location = os.path.join(
        abs_path, config['download_locations']['vehicle_registrations'])
    gdp_download_location = os.path.join(abs_path, config['download_locations']['gdp_per_capita'])

    if args.refresh or not os.path.isfile(vr_download_location):
        # download the dataset for new vehicle registrations
        vr_url = config['dataset_urls']['vehicle_registrations']
        save_url(vr_url, vr_download_location)

    if args.refresh or not os.path.isfile(gdp_download_location):

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

    # calculate the share of electric vehicles among all new registrations
    vr_df['share_electric'] = (vr_df['Elektro (BEV)'] + vr_df['Hybrid']) / vr_df['Insgesamt']
    # round percentages to 4 decimal points
    # vr_df['share_electric'] = vr_df['share_electric'].round(4)

    # clean data, remove any NA cells
    vr_df = vr_df.dropna()

    vr_df['gdp_per_capita'] = gdp_df
    print(vr_df.index)

    # 3.3 Rename the columns
    vr_df = vr_df.rename({
        'Elektro (BEV)': 'electric_total',
        'Hybrid': 'hybrid_total',
        'Insgesamt': 'total'
    }, axis='columns')

    vr_df.index = vr_df.index.rename('federal_state')

    # Step 4 - save to local sqlite instance
    vr_df.to_sql('evs_per_capita',
                'sqlite:///' + CLEANED_FILES_FOLDER + '/evs_per_capita.sqlite',
                if_exists='replace',
                index=True,
                dtype={
        'federal_state': Text,
        'total': Integer,
        'electric_total': Integer,
        'hybrid_total': Integer,
        'share_electric': Float,
        'gdp_per_capita': Integer
    })
