"""
An automated data pipeline, analysing the correlation between per capita gdp and share of EVs
among all newly registered vehicles in german states.
"""

import json
import requests

CONFIG_FILE = "./pipeline_config.json"
RAW_FILES_FOLDER = "./raw"
CLEANED_FILES_FOLDER = "./clean"
HTTP_TIMEOUT = 10000

def save_url(url, out):
    '''Takes a url and saves the contents to out'''
    file_stream = requests.get(url, timeout=HTTP_TIMEOUT)
    open(out, 'wb').write(file_stream.content)

with open(CONFIG_FILE, encoding='UTF-8') as config_json:
    config = json.load(config_json)


#
# Step 1 - Check new file availabilitys
#

# TODO

#
# Step 2 - Download all relevant raw datasets
#

# download the dataset for new vehicle registrations
vr_url = config['dataset_urls']['vehicle_registrations']
save_url(vr_url, './raw/vr.xlsx')

# downlaod the dataset for gdp per capita
gdp_url = config['dataset_urls']['gdp_per_capita']
save_url(gdp_url, './raw/gdp.xlsx')
