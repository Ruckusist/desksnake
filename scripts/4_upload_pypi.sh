# THIS IS THE UPLOAD SCRIPT!
echo "[!] Uploading to PYPI arena.";
sleep 1;
python3 -m twine upload dist/* --verbose;
echo "[$] Concluded Upload to PyPi.";

echo "[%] Starting Test Enviroment.";
python -m venv test;
source test/bin/activate;

echo "[%] Installing App from Test Repo";
pip install desksnake;

sleep 2;
desksnake;
deactivate;
rm -rf test;

echo "[$] Concluded test run. Removed Test Enviroment.";