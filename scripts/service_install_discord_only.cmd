@ECHO OFF
PUSHD "%~dp0.."
set _arch=x86_64

echo ======================================================
echo    EXELANS DISCORD FIX - YALNIZCA DISCORD HIZMETI
echo ======================================================
echo Bu batch dosyasi Windows Hizmeti olarak kurulur.
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

sc create "GoodbyeDPI" binPath= "\"%CD%\bin\goodbyedpi.exe\" -5 --set-ttl 5 --dns-addr 77.88.8.8 --dns-port 1253 --dnsv6-addr 2a02:6b8::feed:0ff --dnsv6-port 1253 --blacklist \"%CD%\discord_domains.txt\"" start= "auto"
sc description "GoodbyeDPI" "Yalnizca Discord icin DPI engelini kaldiran servis (Exelans)."
sc start "GoodbyeDPI"

ipconfig /flushdns

echo.
echo ======================================================
echo [TAMAMLANDI] Yalnizca Discord servisi basariyla kuruldu!
echo Artik hicbir pencere acmaniza gerek yoktur.
echo Bilgisayari yeniden baslatsaniz bile arkada hep calisir.
echo Kaldirilmak istendiginde 'scripts\service_remove.cmd' calistirabilirsiniz.
echo ======================================================
pause
POPD
