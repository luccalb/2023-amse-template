import os
import sys
import json
from data_extractor import DataExtractor

abs_path = os.path.dirname(__file__)

EXAMPLE_CSV_URL = "https://www.w3schools.com/python/pandas/data.csv"
EXPECTED_LOCATION = os.path.join(abs_path, "raw/test_data.csv")
CONFIG_FILE = os.path.join(abs_path, "pipeline_config.json")

with open(CONFIG_FILE, encoding='UTF-8') as config_json:
        config = json.load(config_json)

ex = DataExtractor(config)

ex.save_url(EXAMPLE_CSV_URL, EXPECTED_LOCATION)

file_exists = os.path.exists(EXPECTED_LOCATION)

print("[UNIT TESTS] Example file was written as expected:", os.path.exists(EXPECTED_LOCATION))
print("[UNIT TESTS] Cleanup..")

if file_exists:
    os.remove(EXPECTED_LOCATION)
    sys.exit(0)

sys.exit(1)
