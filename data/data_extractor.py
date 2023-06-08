"""
DataLoader which is responsible for finding the most recent datasets and loading them,
so that they can later be processed in the "transform" step of the pipeline.
"""

import os
import json
from datetime import datetime
import requests

ABS_PATH = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(ABS_PATH, "pipeline_config.json")
HTTP_TIMEOUT = 10000


class DataExtractor:
    """
    DataLoader which is responsible for finding the most recent datasets and loading them,
    so that they can later be processed in the "transform" step of the pipeline.
    """

    def __init__(self, config):
        self.config = config

    def download_all(self, force_refresh=False):
        "Download all relevant datasets"
        current_year = datetime.now().year
        self.download_vr_data(current_year, force_refresh)
        self.download_gdp_data(force_refresh)


    def download_gdp_data(self, force_refresh=False):
        "Downloads the dataset containing GDP per capita for german federal states."
        out_file = os.path.join(ABS_PATH, self.config['download_locations']['gdp_per_capita'])
        gdp_url = self.config['dataset_urls']['gdp_per_capita']

        if force_refresh or not os.path.isfile(out_file):
            self.save_url(gdp_url, out_file)


    def get_recent_vr_month(self, year, base_url):
        """Get the most recent month of a year, up until which a monthly VR report is available.

        Args:
            year (integer): The year for which the most recent VR report should be searched.
            base_url (string): The base URL used for downloading a months report
            by appending the year and month.

        Returns:
            integer: The most recent month of the year, for which a VR report was found.
        """
        base_url = "https://www.kba.de/SharedDocs/Downloads/DE/Statistik/Fahrzeuge/FZ8/"
        for x in range(12):
            month = x+1
            suffix = f"fz8_{year}{month:02}.xlsx?__blob=publicationFile"
            data_url = base_url + suffix
            try:
                response = requests.get(data_url, timeout=HTTP_TIMEOUT, allow_redirects=True)
                response.raise_for_status()
            except requests.HTTPError:
                return x
        return x+1

    def download_vr_data(self, year, force_refresh=False, first_month=0, last_month=0):
        """Downloads all monthly published VR reports for a given range of month in a given year.
        Files are saved in a given directory.

        Args:
            year (_type_): Year to download reports for. All months will be downloaded if
            nothing else is specified
            out_dir (_type_): Directory where to save the reports.
            File names will be of format `vr_{year}_{month}.xlsx`
            force_refresh (boolean, optional): Forcing the re-download of existing reports. Defaults to False.
            first_month (int, optional): First month to get a report for. Defaults to 0.
            last_month (int, optional): Last month to get a report for. Defaults to 0.
        """
        if first_month == 0:
            first_month = 1

        if last_month == 0:
            last_month = self.get_recent_vr_month(year, "")

        out_dir = os.path.join(ABS_PATH, self.config["download_locations"]["vehicle_registrations"])

        # make sure the out dir exists
        os.makedirs(out_dir, exist_ok=True)

        for month in range(first_month, last_month+1):
            out_file = out_dir + f"vr_{year}_{month}.xlsx"
            if force_refresh or not os.path.isfile(out_file):
                self.get_vr_month(out_dir, year, month)

    def get_vr_month(self, out_dir, year, month):
        """Downloads the VR report for a single month to out_dir."""

        base_url = self.config['dataset_urls']['vehicle_registrations']
        suffix = f"fz8_{year}{month:02}.xlsx?__blob=publicationFile"
        data_url = base_url + suffix
        out_file = out_dir + f"vr_{year}_{month}.xlsx"
        self.save_url(data_url, out_file)

    def save_url(self, url, out):
        '''Takes a url and saves the contents to out'''
        file_stream = requests.get(url, timeout=HTTP_TIMEOUT, allow_redirects=True)
        open(out, 'wb').write(file_stream.content)


if __name__ == "__main__":
    with open(CONFIG_FILE, encoding='UTF-8') as config_json:
        config = json.load(config_json)

    ex = DataExtractor(config)
    ex.download_all()
