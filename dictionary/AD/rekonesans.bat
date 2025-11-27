@echo off
setlocal enabledelayedexpansion

:: Utwórz katalog na wyniki
set OUTPUT=rekonesans_wyniki
mkdir %OUTPUT%

:: Informacje o użytkowniku
whoami /all > %OUTPUT%\1_whoami.txt

:: Informacje o konfiguracji sieci
ipconfig /all > %OUTPUT%\2_ipconfig.txt
net config workstation >> %OUTPUT%\2_ipconfig.txt

:: Zasady haseł
net accounts > %OUTPUT%\3_net_accounts.txt

:: Eksport lokalnych zasad bezpieczeństwa
secedit /export /cfg %OUTPUT%\4_secpol.cfg >nul 2>&1

:: Informacje o GPO
gpresult /R > %OUTPUT%\5_gpresult.txt
gpresult /H %OUTPUT%\5_gpresult.html >nul 2>&1

:: Audyt zabezpieczeń
auditpol /get /category:* > %OUTPUT%\6_auditpol.txt

:: Logi zabezpieczeń
wevtutil qe Security /c:10 /f:text > %OUTPUT%\7_eventlog.txt

:: Kontrolery domeny (jeśli znasz nazwę domeny, zmień poniżej)
set /p DOMAIN=Podaj nazwę domeny (np. firma.local): 
nltest /dclist:%DOMAIN% > %OUTPUT%\8_dclist.txt

:: Grupy uprzywilejowane
net group "Domain Admins" /domain > %OUTPUT%\9_domain_admins.txt
net group "Enterprise Admins" /domain >> %OUTPUT%\9_domain_admins.txt

:: Zapora
netsh advfirewall show allprofiles > %OUTPUT%\10_firewall.txt

:: Ustawienia RDP
reg query "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections > %OUTPUT%\11_rdp_status.txt

:: Usługi
sc query state= all > %OUTPUT%\12_uslugi.txt

echo ---------------------------------------
echo Wszystko gotowe. Wyniki zapisane w: %OUTPUT%
pause
