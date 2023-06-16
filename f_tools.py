import f_biblioteka

def f_socat(proto, ip, port):
    """ 
    function: socat 

    @param proto: Proto TCP or UDP
    @param ip: ip address
    @param port: port numer of the service, numerical between 1-65535
    @return: cmd and output of this command or error message
    """
    cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {proto.upper()}:{ip}:{port},connect-timeout=5 - "

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