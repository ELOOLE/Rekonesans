# Rekonesans

W pierwszym kroku uruchamiamy za pomocą Metasploit moduł "db_nmap" i skanujemy adresy IP w poszukiwaniu usług:

# msfconsole (przykłady skanowania TCP i UDP)
    msf6 > db_nmap -sT -sV -O -Pn -n -p- -d xxx.xxx.xxx.xxx/24
    msf6 > db_nmap -sU -sV -Pn -n --top-ports 500 -d xxx.xxx.xxx.xxx/24


Następnie eksportujemy wyniki z metasploita do pliku, poleceniem jak ponizej:

# msfconsole (eksport wyników skanowania nmap)
    msf6 > services -u -c port,proto,name,info -o /sciezka/do/pliku


Uruchamiamy skrypt rekonesans.py wraz z przelacznikiem --fin lub modyfikujemy skrypt w miejscu gdzie w metodzie main jest jawnie podana sciezka do tego pliku
Chodzi o ścieżkę do pliku /sciezka/do/pliku powstałego z eksportu z metaspolita. 

# skladnia
    /bin/python3 /sciezka/do/rekonesans.py --fin /sciezka/do/pliku

# Powstanie kilka plikow
    /sciezka/do/pliku - plik wygenerowany przez metasploita
    /sciezka/do/pliku.log - plik logu z dzialania skryptu rekonesans.py
    /sciezka/do/pliku_IP.IP.IP.IP_http.jpg
    /sciezka/do/pliku_IP.IP.IP.IP_https.jpg
    ...
    /sciezka/do/pliku.json - plik, na którym dalej działamy za pomocą mojej autorskiej aplikacji https://sciezka-do--skompilowanej-wersji.zip
    /sciezka/do/pliku.html - plik przejściowy
    /sciezka/do/pliku_convert.html - ostateczna wizualizacja dzialania skryptu rekonesans.py
