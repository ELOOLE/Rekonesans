# Utwórz folder na wyniki
$OutputFolder = "rekonesans_wyniki"
New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null

# Informacje o użytkowniku
whoami /all | Out-File "$OutputFolder\1_whoami.txt"

# Zasady haseł
net accounts | Out-File "$OutputFolder\2_net_accounts.txt"

# Informacje o konfiguracji sieci
ipconfig /all | Out-File "$OutputFolder\3_ipconfig.txt"
net config workstation | Out-File "$OutputFolder\3_workstation.txt"

# Eksport lokalnej polityki
secedit /export /cfg "$OutputFolder\4_secpol.cfg"

# GPO - raport
gpresult /H "$OutputFolder\5_gpresult.html"

# Audyt zabezpieczeń
auditpol /get /category:* | Out-File "$OutputFolder\6_auditpol.txt"

# Logi bezpieczeństwa
Get-WinEvent -LogName Security -MaxEvents 10 | Format-List | Out-File "$OutputFolder\7_eventlog.txt"

# Kontrolery domeny
$domain = Read-Host "Podaj nazwę domeny (np. firma.local)"
nltest /dclist:$domain | Out-File "$OutputFolder\8_dclist.txt"

# Grupy uprzywilejowane
net group "Domain Admins" /domain | Out-File "$OutputFolder\9_domain_admins.txt"
net group "Enterprise Admins" /domain | Out-File "$OutputFolder\9_enterprise_admins.txt"

# Zapora
netsh advfirewall show allprofiles | Out-File "$OutputFolder\10_firewall.txt"

# Status RDP
Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections |
    Out-File "$OutputFolder\11_rdp_status.txt"

# Lista usług
Get-Service | Sort-Object Status | Out-File "$OutputFolder\12_uslugi.txt"

Write-Host "-------------------------------------------"
Write-Host "Wszystko gotowe. Wyniki zapisano w folderze: $OutputFolder"
