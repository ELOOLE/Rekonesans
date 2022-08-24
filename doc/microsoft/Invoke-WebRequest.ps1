# ściągnięcie pliku z sieci odpowiednik polecenia w Linux-ie wget
Invoke-WebRequest -Uri https://github.com/main.zip -OutFile c:\users\user\Downloads\main.zip

# w formie skryptu
# plik zrodlowy
$source = 'http://speedtest.tele2.net/10MB.zip'
# plik docelowy
$destination = 'c:\dload\10MB.zip'
# skladnia polecenia
Invoke-WebRequest -Uri $source -OutFile $destination
