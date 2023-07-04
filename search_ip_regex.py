import re


def f_file_read(file1):
    print(f"[*] file: {file1}")

    with open(file1, "r", encoding="utf-8", errors="ignore") as rfile1:
        for line in rfile1.readlines():
            line = line.strip()
            x = re.findall("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}", line)
            if x:
                for i in x:
                    print(f"[+] {i}")
                    with open("/home/muser/Downloads/debug2_ip", "+a") as wfile1:
                        wfile1.write(f"{i}\n")


if __name__ == '__main__':
    f_file_read("/home/muser/Downloads/debug2")