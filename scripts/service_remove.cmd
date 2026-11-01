@ECHO OFF
echo ======================================================
echo    EXELANS DISCORD FIX - HIZMETI KALDIR
echo ======================================================
echo Sag tiklayip 'Yonetici Olarak Calistir' dediginizden emin olun.
pause

sc stop "GoodbyeDPI" >nul 2>&1
sc delete "GoodbyeDPI" >nul 2>&1
sc stop "WinDivert" >nul 2>&1
sc delete "WinDivert" >nul 2>&1
sc stop "WinDivert14" >nul 2>&1
sc delete "WinDivert14" >nul 2>&1

ipconfig /flushdns

echo.
echo ======================================================
echo [TAMAMLANDI] GoodbyeDPI servisi ve suruculeri kaldirildi.
echo ======================================================
pause
