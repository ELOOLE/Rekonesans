import re
import os

"""
Zbieranie wszystkich unikalnych, poprawnych adresów IP z pliku lub katalogu i zapis do pliku. 
"""

# Wyrażenie regularne do poprawnych adresów IPv4
ip_pattern = re.compile(
    r'\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}'
    r'(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b'
)

def extract_ips_from_file(file_path):
    """Zwraca zbiór unikalnych IP z jednego pliku."""
    ips = set()
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            found_ips = ip_pattern.findall(line)
            ips.update(found_ips)
    return ips

def extract_ips_from_directory(directory):
    """Zwraca zbiór unikalnych IP z wszystkich plików w katalogu."""
    all_ips = set()
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            all_ips.update(extract_ips_from_file(file_path))
    return all_ips

def save_ips(ips, output_file):
    """Zapisuje IP do pliku bez duplikatów."""
    with open(output_file, "w") as f:
        for ip in sorted(ips):
            f.write(ip + "\n")
    print(f"[+] Zapisano {len(ips)} unikalnych IP do {output_file}")

if __name__ == "__main__":
    # Możesz zmienić na ścieżkę do pliku lub katalogu
    path_to_scan = "/home/muser/Downloads/debug2"
    output_file = "/home/muser/Downloads/debug2_ip"

    if os.path.isfile(path_to_scan):
        ips = extract_ips_from_file(path_to_scan)
    elif os.path.isdir(path_to_scan):
        ips = extract_ips_from_directory(path_to_scan)
    else:
        print("Ścieżka nie istnieje!")
        exit(1)

    for ip in ips:
        print(f"[+] {ip}")

    save_ips(ips, output_file)
