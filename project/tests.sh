# get path of test script, relative to execution path
MY_PATH="$(dirname $0)"
EXPECTED_OUT_FILE="$MY_PATH/../data/clean/evs_per_capita.sqlite"

# [STEP 1]
# activate the virtual environment with all dependencies
source "$MY_PATH/../../.venv/Scripts/activate"
echo 'Activated AMSE virtual environment'
python --version

# [STEP 2]
# clean the environment, removing all old files
echo 'Cleaning the test environment..'

rm -f ./$MY_PATH/../data/clean/*.sqlite
rm -f ./$MY_PATH/../data/raw/*.xlsx

# [STEP 3]
# Run the pipeline with the -r flag, forcing it to load fresh data
echo 'Running automated data pipeline..'

cd ./$MY_PATH/../data
python ./data_pipeline.py -r


# [STEP 4]
# Check if the pipeline was successful in creating the output file
cd ..
echo 'Checking results..'

if test -f "$EXPECTED_OUT_FILE"; then
    echo "[SUCCESS] $EXPECTED_OUT_FILE exists."
    exit 0
fi
echo "[ERROR] $EXPECTED_OUT_FILE doesn't exist!"
exit 2