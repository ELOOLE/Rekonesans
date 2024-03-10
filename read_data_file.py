from f_biblioteka import f_policz_wiersze_w_pliku,f_socat,f_amap
import re

def f_odczyt_pliku(plik):
    # How many services we will check
    line_count = f_policz_wiersze_w_pliku(plik)

    # open file with data   
    handler_file_with_data = open(plik, 'r')

    # counter of services
    i = 1

    # read from file line by line
    for service_info in handler_file_with_data:
        (ip, port, protokol, usluga, opis_nmap) = service_info.replace("\"","").strip().split(',')
       
        # check if ip is real ip value
        r = re.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}")
        if r.match(ip) is None:
            LINE_COUNT -= 1
        else:
            if(protokol == "tcp"):
                #print(f"[*] ({protokol},{usluga},{opis_nmap}) nmap {ip} -p {port} ")
                # socat
                print(f"[*] ({protokol},{usluga},{opis_nmap}) socat {ip} {port} ")
                cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol}:{ip}:{port},connect-timeout=5 - "
                with open(plik+f".do.socat") as my_file:
                    print(my_file.read())

                #socat_output = f_socat(protokol, ip, port)
                # amap
                print(f"[*] ({protokol},{usluga},{opis_nmap}) amap -bqv {ip} {port} ")
                #amap_output = f_amap(protokol, ip, port)
                # curl
                print(f"[*] ({protokol},{usluga},{opis_nmap}) curl {ip} {port} ")
                # web screen shot
                print(f"[*] ({protokol},{usluga},{opis_nmap}) curl web shoot {ip} {port} ")
                # web links
                print(f"[*] ({protokol},{usluga},{opis_nmap}) curl links {ip} {port} ")

            elif(protokol == "udp"):
                print(f"[*] ({protokol},{usluga},{opis_nmap}) nmap {ip} -sU -p {port} ")
        

    return 