@ECHO OFF
PUSHD "%~dp0.."
set _arch=x86_64

echo ======================================================
echo    EXELANS DISCORD FIX - SUPERONLINE / VODAFONE HIZMETI
echo ======================================================
echo Superonline / Vodafone baglantilari icin TTL 3 modunda kurulur.
echo SADECE Discord domainlerini hedefler (diger siteler etkilenmez).
echo Bilgisayar acildiginda otomatik baslar, kaldirana kadar aktiftir.
echo.
echo Sag tiklayip 'Yonetici Olarak Calistir' demis olmaniz gerekir.
echo Devam etmek icin herhangi bir tusa basin...
pause

sc stop "GoodbyeDPI" >nul 2>&1
sc delete "GoodbyeDPI" >nul 2>&1
sc stop "WinDivert" >nul 2>&1
sc delete "WinDivert" >nul 2>&1
sc stop "WinDivert14" >nul 2>&1
sc delete "WinDivert14" >nul 2>&1

sc create "GoodbyeDPI" binPath= "\"%CD%\bin\goodbyedpi.exe\" --set-ttl 3 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253 --blacklist \"%CD%\discord_domains.txt\"" start= "auto"
sc description "GoodbyeDPI" "Yalnizca Discord Superonline DPI servisi (Exelans)."
sc start "GoodbyeDPI"

ipconfig /flushdns

echo.
echo ======================================================
echo [TAMAMLANDI] Superonline Discord servisi basariyla kuruldu!
echo Kaldirilmak istendiginde 'scripts\service_remove.cmd' calistirabilirsiniz.
echo ======================================================
pause
POPD
