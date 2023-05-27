# get path of test script, relative to execution path
MY_PATH="$(dirname $0)"
EXPECTED_OUT_FILE="./$MY_PATH/../data/clean/evs_per_capita.sqlite"

# [STEP 1]
# activate the virtual environment with all dependencies
source "$MY_PATH/../../.venv/Scripts/activate"
echo '[STATUS] Activated AMSE virtual environment'
# python --version

# [STEP 2]
# clean the environment, removing all old files
echo '[STATUS] Cleaning the test environment..'

rm -f ./$MY_PATH/../data/clean/*.sqlite
rm -f ./$MY_PATH/../data/raw/*.xlsx

# [STEP 3]
# Run the pipeline with the -r flag, forcing it to load fresh data
echo '[STATUS] Running automated data pipeline..'

# cd ./$MY_PATH/../data
python ./$MY_PATH/../data/data_pipeline.py -r


# [STEP 4]
# Check if the pipeline was successful in creating the output file
# cd ..
echo 'Checking results..'

if ! test -f "$EXPECTED_OUT_FILE"; then
    echo "[ERROR] $EXPECTED_OUT_FILE doesn't exist!"
    exit 2
    
fi

echo "[SUCCESS] $EXPECTED_OUT_FILE exists."

echo "[STATUS] Running unit tests.."

python ./$MY_PATH/../data/unit_tests.py
