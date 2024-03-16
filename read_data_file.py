from f_biblioteka import f_policz_wiersze_w_pliku, extract_ip_addresses
import socket

def f_odczyt_pliku(plik):
    # How many services we will check
    line_count = f_policz_wiersze_w_pliku(plik)
    print(f"[i] {line_count} wierszy w pliku ")

    # open file with data   
    handler_file_with_data = open(plik, 'r')

    # counter of services
    i = 1

    # read from file line by line
    for service_info in handler_file_with_data:
        (ip, port, protokol, usluga, opis_nmap) = service_info.replace("\"","").lower().strip().split(',')
              
        if extract_ip_addresses(ip) is None:
            line_count -= 1
            print(f"[-] adres ip: [{ip}] niepoprawny")
        else:
            if(protokol.lower() == "tcp"):
                #print(f"[*] ({protokol},{usluga},{opis_nmap}) nmap {ip} -p {port} ")
                # socat
                cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol.upper()}:{ip}:{port},connect-timeout=5 - "
                print(f"[*] do wykonania: {cmd}")
                print(get_tcp_banner(ip, port))
                # amap
                
                # curl
                
                # web screen shot
                
                # web links
            elif(protokol == "udp"):
                cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol.upper()}:{ip}:{port},connect-timeout=5 - "
                print(get_udp_banner(ip, port))
                print(f"[*] do wykonania: {cmd}")
        
    return 


def get_tcp_banner(ip, port):
    try:
        port = int(port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Set a timeout for the connection
        s.connect((ip, port))
        banner = s.recv(1024).decode('utf-8')
        s.close()
        return banner
    except Exception as e:
        return f"Error: {str(e)}"


def get_udp_banner(ip, port):
    try:
        port = int(port)
        socket.setdefaulttimeout(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(b'\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01', (ip, port))
        response, _ = s.recvfrom(1024)
        return response
    except:
        return None
