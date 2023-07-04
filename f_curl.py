import shlex
import subprocess

def f_curl_variables_JS(addr):
    # budujemy polecenie
    cmd_curl = f"curl -Lks {addr} | grep window "

    args1 = shlex.split(cmd_curl)
    ps_cmd_curl1 = subprocess.Popen(
        args1,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    try:
        curl_output = str(ps_cmd_curl1.communicate(timeout=10)[0].decode('utf-8'))

         # zmienna [wynik] ma dane, ktore zostana zwrocone przez funkcje
        output = str(curl_output).strip()
        output_window = output.split("\n")
        link_addr = ""

        for x in output_window:
            if("window" in x):
                link_addr = x

        start = link_addr.find("/")
        end = link_addr[start:].find('"') + start

        output = link_addr[start + 1:end]

        if(len(output) == 0):
            output = "none"
    except subprocess.TimeoutExpired:
        ps_cmd_curl1.kill()
        output = "TimeoutExpired"
    return output