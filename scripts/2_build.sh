# DONT REBUILD THE PROGRAM AFTER the TEST BUILD
echo "[=] Build Another AlphaGriffin Project...";
echo "[!] Don't Rebuild the project again after passing tests.";
sleep 1;

echo "[-] Removing old files...";
rm -rf desksnake.egg-info;
rm -rf dist;
sleep 1;

echo "[+] Building dist files...";
python3 -m build;
sleep 2;

echo "[#] testing build files...";
twine check dist/*

echo "[$] Concluded test run. Removed Test Enviroment.";