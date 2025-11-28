import socket
import requests
import urllib3
from colorama import init
from termcolor import colored
import texttable
import argparse
import os
from concurrent.futures import ThreadPoolExecutor

# Wyłączanie ostrzeżeń SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def read_file(datafile, additional_ports):
    # Przygotowanie tabeli do wyświetlania wyników
    table = texttable.Texttable()
    table.header(["url", "ip", "http code", "https code"] + [f"port {port}" for port in additional_ports])
    table.set_cols_width([50, 20, 10, 10] + [10 for _ in additional_ports])

    # Słownik do przechowywania liczby wystąpień IP
    ip_count = {}

    # Ustalenie ścieżki do pliku wynikowego
    output_file = os.path.splitext(datafile)[0]  # Usuwamy rozszerzenie pliku wejściowego
    output_file = f"{output_file}_wynik.txt"  # Dodajemy przedrostek "_wynik.txt"

    # Otwarcie pliku wynikowego w trybie zapisu
    with open(output_file, "w") as result_file:
        try:
            with open(datafile, "r") as h_datafile:
                urls = h_datafile.readlines()
        except FileNotFoundError:
            print(f"[+] File {datafile} not found.")
            return
        except IOError as e:
            print(f"[-] Error reading file {datafile}: {e}")
            return

        # Przetwarzanie URLi w sposób równoległy
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda url: process_url(url, additional_ports, ip_count), urls)

        # Zapis wyników do pliku oraz wypisanie na ekran
        for result in results:
            table.add_row(result)
            result_line = " ".join(map(str, result)) + "\n"
            result_file.write(result_line)

        # Wyświetlenie tabeli w terminalu
        print(table.draw())

        # Podsumowanie IP
        print("\n[+] Podsumowanie IP i liczba ich wystąpień:")
        
        # Sortowanie wyników po adresach IP
        sorted_ip_count = sorted(ip_count.items())

        # Tworzymy tabelę podsumowania
        summary_table = texttable.Texttable()
        summary_table.header(["IP Address", "Wystąpienia"])
        for ip, count in sorted_ip_count:
            summary_table.add_row([ip, count])
        
        print(summary_table.draw())

    print(f"[+] Zapisano wyniki do pliku: {output_file}")

def process_url(url, additional_ports, ip_count):
    url = url.strip()
    ip = get_hostname_ip(url)

    # Zwiększ liczbę wystąpień IP
    if ip != "error":
        if ip in ip_count:
            ip_count[ip] += 1
        else:
            ip_count[ip] = 1
    
    # Statusy dla standardowych portów HTTP i HTTPS
    http_code = get_http_code_respond(f"http://{url}", verify=False)  # Dla HTTP nie przekazujemy verify
    https_code = get_http_code_respond(f"https://{url}", verify=False)  # Dla HTTPS przekazujemy verify=False

    # Sprawdzanie dodatkowych portów
    port_codes = []
    for port in additional_ports:
        port_code = check_port_status(url, port)
        port_codes.append(port_code)

    # Zwracanie wyników jako lista
    return [url, ip, http_code, https_code] + port_codes

def get_hostname_ip(fqdn):
    try:
        return socket.gethostbyname(fqdn)
    except Exception as e:
        return "error"

def get_http_code_respond(url, verify=True):
    try:
        # Weryfikacja tylko dla HTTPS, bo HTTP nie ma certyfikatów SSL
        if url.startswith("https://"):
            response = requests.get(url, verify=verify, timeout=7)
        else:
            response = requests.get(url, timeout=7)  # Dla HTTP nie potrzeba verify

        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[-] Error with {url}: {e}")
        return "error"

def check_port_status(url, port):
    try:
        response = requests.get(f"http://{url}:{port}", verify=False, timeout=7)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[-] Error connecting to {url}:{port}: {e}")
        return "error"

def get_status_color(code):
    if code == 200:
        return "green"
    elif 300 <= code < 400:
        return "yellow"
    elif 400 <= code < 500 or 500 <= code < 600:
        return "red"
    return "white"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Program do sprawdzania statusu URL-i z pliku")
    parser.add_argument("file", help="Ścieżka do pliku z listą URL-i")
    parser.add_argument("--ports", type=int, nargs='*', default=[], help="Lista dodatkowych portów do sprawdzenia (np. --ports 8080 5000)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    read_file(args.file, args.ports)
