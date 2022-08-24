# ściągnięcie pliku z sieci odpowiednik polecenia w Linux-ie wget
Invoke-WebRequest -Uri https://github.com/main.zip -OutFile c:\users\user\Downloads\main.zip

# w formie skryptu
# plik zrodlowy
$source = 'http://speedtest.tele2.net/10MB.zip'
# plik docelowy
$destination = 'c:\dload\10MB.zip'
# skladnia polecenia
Invoke-WebRequest -Uri $source -OutFile $destination


# to samo tylko trzeba sie zalogować
$credential = Get-Credential
$source = 'https://mirror.lzex.ml/100MB.zip'
$destination = 'c:\dload\100MB.zip'
Invoke-WebRequest -Uri $source -OutFile $destination -Credential $credential
