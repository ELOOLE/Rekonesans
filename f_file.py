def f_policz_wiersze_w_pliku(path):
    '''liczy ilosc linijek w wierszu'''
    '''zwraca: int, ilość linijek w podanym pliku'''
    # otwieram plik
    otwarty_plik = open(path, "r")
    line_count = 0
    # czytam linijce po linijce
    for line in otwarty_plik:
        if line != "\n":
            line_count += 1

    # zamykam plik            
    otwarty_plik.close()
    # zwracam wynik
    return line_count