"""
An automated data pipeline, analysing the correlation between per capita gdp and share of EVs
among all newly registered vehicles in german states.
"""

import os
import json
import argparse
from data_extractor import DataExtractor
from logger import ETLogger
import pandas as pd
from sqlalchemy.types import Integer, Text, Float

abs_path = os.path.dirname(__file__)

LOGGER = ETLogger("PIPELINE")


CONFIG_FILE = os.path.join(abs_path, "pipeline_config.json")
RAW_FILES_FOLDER = os.path.join(abs_path, "raw")
CLEANED_FILES_FOLDER = os.path.join(abs_path, "clean")

def save_to_db(df, table, dtypes=None):
    """Loads a pandas df into the main SQLite DB"""
    # make sure the target folder exists
    os.makedirs(CLEANED_FILES_FOLDER, exist_ok=True)
    df.to_sql(table,
                'sqlite:///' + CLEANED_FILES_FOLDER + '/evs_per_capita.sqlite',
                if_exists='replace',
                index=True,
                dtype=dtypes)

if __name__ == '__main__':
    
    LOGGER.log("Starting ETL Pipleine.")
    

    with open(CONFIG_FILE, encoding='UTF-8') as config_json:
        config = json.load(config_json)

    # Step 0.1 - Parse program arguments

    arg_parser = argparse.ArgumentParser()

    # while developing, it's not necessary to reload the files every time -> default to false
    arg_parser.add_argument('-r', '--refresh',
                            action='store_true',
                            help='force re-downloading the datasets')

    args = arg_parser.parse_args()
    
    LOGGER.log(f"Force reload: {args.refresh}")


    #
    # Step 1 (Extraction) - Download all relevant raw datasets
    #

    data_extractor = DataExtractor(config)
    LOGGER.log("Starting extraction stage")
    data_extractor.download_all(args.refresh)

    vr_download_location = os.path.join(
        abs_path, config['download_locations']['vehicle_registrations'])
    gdp_download_location = os.path.join(abs_path, config['download_locations']['gdp_per_capita'])


    LOGGER.log("Entering 'Transform' stage.")
    #
    # Step 2 (Transformation) - Find relevant data in files and transform to our wish
    #

    # 2.1 Load and transform GDP data

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

    # print(gdp_df.head())

    # 2.2 Load and transform vehicle data
    vr_joined_df = None

    vr_files = os.listdir(os.path.dirname(vr_download_location))

    for vr_file in vr_files:
        
        filename_parts = vr_file.split('_')
        year = filename_parts[1]
        month = filename_parts[2].split('.')[0]
        
        vr_df = pd.read_excel(os.path.join(vr_download_location, vr_file),
                            sheet_name='FZ 8.6',
                            usecols='B:Q',
                            skiprows=7,
                            nrows=17,
                            index_col=0)
        
        LOGGER.log(f"Processing VR dataset for month {month}")

        # remove the newline characters in state names
        vr_df.columns = vr_df.columns.str.replace('\n', ' ')
        vr_df = vr_df[['Elektro (BEV)', 'Hybrid', 'Insgesamt']]

        # calculate the share of electric vehicles among all new registrations (can be used later for time series)
        vr_df['share_electric'] = (vr_df['Elektro (BEV)'] + vr_df['Hybrid']) / vr_df['Insgesamt']
        # round percentages to 4 decimal points
        vr_df['share_electric'] = vr_df['share_electric'].astype(float).round(4)

        # clean data, remove any NA cells
        vr_df = vr_df.dropna()

        # 2.3 Rename the columns
        vr_df = vr_df.rename({
            'Elektro (BEV)': 'electric_total',
            'Hybrid': 'hybrid_total',
            'Insgesamt': 'total'
        }, axis='columns')

        vr_df.index = vr_df.index.rename('federal_state')

        # add year and month column
        
        vr_df['year'] = year
        vr_df['month'] = month
        
        # add the resulting (monthly) dataframe to the aggregated dataframe
        if vr_joined_df is None:
            vr_joined_df = vr_df
        else:
            vr_joined_df = pd.concat([vr_joined_df, vr_df])

    # save the joined monthly data in a seperate sqlite table before aggregating the data
    save_to_db(vr_joined_df, f"vr_{year}")
    
    # 2.4 Group and aggregate the data monthly by federal state
    LOGGER.log("Aggregating all monthly VR datasets.")
    aggregated_df = vr_joined_df.groupby('federal_state').aggregate({'electric_total': 'sum', 'total': 'sum', 'hybrid_total': 'sum'})
    
    # calculate the share of electric vehicles again, this time on aggregated data
    LOGGER.log("Calculating share of EV registrations in observed timespan.")
    aggregated_df['share_electric'] = (aggregated_df['electric_total'] + aggregated_df['hybrid_total']) / aggregated_df['total']
    # round percentages to 4 decimal points
    aggregated_df['share_electric'] = aggregated_df['share_electric'].astype(float).round(4)
    
    # add gdp data
    aggregated_df['gdp_per_capita'] = gdp_df

    # print(vr_df.index)
    
    LOGGER.log("Entering 'Load' stage.")

    # Step 3 (Loading) - Save to local sqlite instance
    dtypes = {
        'federal_state': Text,
        'total': Integer,
        'electric_total': Integer,
        'hybrid_total': Integer,
        'share_electric': Float,
        'gdp_per_capita': Integer
    }

    save_to_db(aggregated_df, 'evs_per_capita', dtypes)
    
    LOGGER.log("Sucessfully saved clean & aggregated data!")
