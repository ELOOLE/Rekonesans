# Rekonesans

W pierwszym kroku uruchamiamy za pomocą Metasploit db_nmap i skanujemy adresy IP w poszukiwaniu usług. Następnie eksportujemy wyniki z metasploita do pliku plaskiego, poleceniem jak ponizej:

# msfconsole 
    services -u -c port,proto,name,info -o /sciezka/do/pliku


Uruchamiamy skrypt rekonesans.py wraz z przelacznikiem --fin lub modyfikujemy skrypt w miejscu gdzie w metodzie main jest jawnie podana sciezka do tego pliku
Chodzi o ścieżkę do pliku /sciezka/do/pliku powstałego z eksportu z metaspolita. 

# skladnia
    /bin/python3 /sciezka/do/rekonesans.py --fin /sciezka/do/pliku
