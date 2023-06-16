import f_biblioteka

def f_socat(protokol, ip, port):
    #########
    # socat #
    #########
    #
    # polecenie:
    cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol.upper()}:{ip}:{port},connect-timeout=5 - "

    # wykonanie polecenia:
    socat_output = f_biblioteka.f_polecenie_uniwersalne(cmd)

    # sprawdzam
    # [0] - wynik
    # [1] - komunikat bledu
    if(socat_output[1] == None):
        # wynik
        output = f_biblioteka.f_trim_output(socat_output[0])
        if(len(output) > 0):
            return cmd, output
        else:
            return cmd, "none"
    else:
        return cmd, socat_output[1]    