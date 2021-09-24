def parsuje_addr (adres):
    '''Parsuje adres URL'''
    h_port = ""
    if("https" in adres):
        h_port = "https"
    elif("http" in adres):
        h_port = "http"
    else:
        return "err"

    host = adres[(int(str(adres).find(":")) + 3):]
    host = host[:str(host).find(":")]

    port = adres.split(host)
    port[1]=port[1][1:]

    port =port[1][:str(port[1]).find("/")]

    reszta = adres.split(port)
    reszta = reszta[1]

    return [h_port, host, port, reszta]
