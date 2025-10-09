import csv
import argparse
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description='Przetwarzanie pliku z portami TCP/UDP.')
    parser.add_argument('-fin', '--file_input', required=True, help='Ścieżka do pliku wejściowego (CSV)')
    parser.add_argument('-fout', '--file_output', required=True, help='Ścieżka do pliku wyjściowego (CSV)')
    return parser.parse_args()

def main():
    args = parse_args()

    ip_ports = defaultdict(lambda: {'tcp': set(), 'udp': set()})

    # Wczytaj dane z pliku wejściowego
    with open(args.file_input, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            ip = row['host'].strip()
            port = row['port'].strip()
            proto = row['proto'].strip().lower()

            if proto in ['tcp', 'udp']:
                ip_ports[ip][proto].add(port)

    # Zapisz dane do pliku wyjściowego
    with open(args.file_output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['adres ip', 'porty TCP', 'porty UDP'])

        for ip in sorted(ip_ports):
            tcp_ports = ','.join(sorted(ip_ports[ip]['tcp'], key=int))
            udp_ports = ','.join(sorted(ip_ports[ip]['udp'], key=int))
            writer.writerow([ip, tcp_ports, udp_ports])

if __name__ == '__main__':
    main()
