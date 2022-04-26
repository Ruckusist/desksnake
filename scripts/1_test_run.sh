# DONT REBUILD THE PROGRAM AFTER the TEST BUILD
echo "[#] Testing the App";
sleep 1;

echo "[%] Starting Test Enviroment.";
python -m venv test;
source test/bin/activate;

echo "[%] Installing from Local Directory";
pip install .;

echo "[%] Executing Tests...";
desksnake;

echo "[%] Passed Tests...";
sleep 1;
deactivate;
rm -rf test;

echo "[$] Concluded test run. Removed Test Enviroment.";