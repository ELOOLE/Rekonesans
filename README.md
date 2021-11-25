# Rekonesans
Rekonesans infrastruktury

W pierwszym kroku uruchamiamy za pomocą Metasploit db_nmap i następnie eksportujemy wyniki 
# msfconsole 
    services -u -c port,proto,name,info -o /sciezka/do/pliku


Podajemy ścieżkę do wytyczonych celów, plik /sciezka/do/pliku 

# skladnia
    /bin/python3 /sciezka/do/rekonesans.py --fin /sciezka/do/pliku
