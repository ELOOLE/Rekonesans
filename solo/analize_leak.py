import re
import os

def check_email_addr(dane:str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    #return re.fullmatch(regex, email

    return re.findall(regex, dane)

def podziel_po_dlugosci():
    with open("/home/kali/Downloads/leaks/domeny_pl.txt","r") as dane:
        for line in dane:
            line = line.strip()
            if(len(line) > 200):
                with open("/home/kali/Downloads/leaks/wieksze.txt", "a+") as wieksze:
                    wieksze.write(f"{line}\n")
            else:
                with open("/home/kali/Downloads/leaks/tmp.txt", "a+") as tmp:
                    tmp.write(f"{line}\n")

def po_adresie_email():
    with open("/home/kali/Downloads/leaks/tmp.txt","r") as dane:
        for line in dane:
            line = line.strip()
            e_addr = check_email_addr(line)
            if len(e_addr) >= 1:
                for i in e_addr:
                    i = str(i).strip().lower()

                    try:
                        os.mkdir(f"/home/kali/Downloads/leaks/{i[0]}")
                    except:
                        pass

                    with open(f"/home/kali/Downloads/leaks/{i[0]}/{i}", "a+") as email:
                        email.write(f"{line}\n")
                    
                    with open(f"/home/kali/Downloads/leaks/emails.txt", "a+") as email2:
                        email2.write(f"{i}\n")
            else:
                with open("/home/kali/Downloads/leaks/noemail.txt", "a+") as noemail:
                    noemail.write(f"{line}\n")


                #input("enter")

if __name__ == "__main__":
    #podziel_po_dlugosci()
    po_adresie_email()
