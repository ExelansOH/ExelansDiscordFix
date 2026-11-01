@ECHO OFF
echo [1/2] Bagimliliklar kontrol ediliyor...
pip install -r requirements.txt

echo [2/2] PyInstaller ile tek parca .exe derleniyor...
pyinstaller --noconfirm --onefile --windowed --uac-admin --icon "discord_fix.ico" --add-data "bin;bin" --add-data "discord_domains.txt;." --add-data "discord_fix.ico;." --collect-all customtkinter --name "ExelansDiscordFix" gui.py

echo.
echo Derleme tamamlandi! Dosya: dist\ExelansDiscordFix.exe
pause
