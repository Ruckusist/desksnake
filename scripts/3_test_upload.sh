echo "[+] Uploading to Test PYPI arena.";
python -m twine upload --repository testpypi dist/*;

echo "[%] Starting Test Enviroment.";
python -m venv test;
source test/bin/activate;

echo "[%] Installing App from Test Repo";
pip install --index-url https://test.pypi.org/simple --no-deps desksnake;
pip install -r requirements.txt;

sleep 2;
desksnake;
deactivate;
rm -rf test;

echo "[$] Concluded test run. Removed Test Enviroment.";