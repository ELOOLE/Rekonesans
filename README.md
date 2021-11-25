# Rekonesans
Rekonesans infrastruktury

W pierwszym kroku uruchamiamy za pomocą Metasploit db_nmap i następnie eksportujemy wyniki 
# msfconsole 
    services -u -c port,proto,name,info -o /sciezka/do/pliku

Podajemy ścieżkę do wytyczonych celów (modyfikujemy plik rekonesans.py lub podajemy parametr w linii poleceń --fin)

# odczyt pliku
    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_nmap_msfconsole = '/sciezka/do/pliku'
    else:
        path_plik_nmap_msfconsole = args.fin

lub

/bin/python3 /home/pentester/Dokumenty/PPL/json_to_html.py --fin /sciezka/do/pliku
