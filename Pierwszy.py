print("Czesc tutaj Wiktoria i Wojtus")
imie = input("Podaj jak masz na imie? ")
print(f"Czesc {imie}")
lat = input("Ile masz lat? ")

Wiktoria_lat = 13
Wojtus_lat = 6

if(int(lat)>int(Wiktoria_lat)):
    print(f"{imie} jest starszy od Wiktori")
else:
    print(f"{imie} jest mlodszy od Wiktori")

if(int(lat)>int(Wojtus_lat)):
    print(f"{imie} jest starszy od Wojtusia")
else:
    print(f"{imie} jest mlodszy od Wojtusia")
