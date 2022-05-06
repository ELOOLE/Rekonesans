import subprocess

def f_polecenie_uniwersalne(cmd):
    '''SOCAT
    INPUT:
        cmd - command
    OUTPUT:
        wynik polecenia
    '''     
    ps = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    try:
        output, errs = ps.communicate(timeout=20)

        return output, errs
    except subprocess.TimeoutExpired:
        ps.kill()

        return "", "TimeoutExpired"
    except Exception as error:
        return "", str(error)


def f_dirb(adres):
    wynik = f_polecenie_uniwersalne(f"dirb {adres} /usr/share/wordlists/dirb/common.txt")
    
    if(wynik[1] != "None"):
        try:
            sukces = str(wynik[0].decode("utf-8"))
        except Exception as e:
            sukces = str(wynik[0])
            
    return sukces        