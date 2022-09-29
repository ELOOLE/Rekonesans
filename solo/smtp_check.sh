#!/bin/bash
#### coding: MM #######################################################
#                                                                     #
# smtp_check.sh - check smtp server configuration                     # 
#                                                                     #
# FILE                                                                #
# smtp_check.sh                                                       #
#                                                                     #
# DATE                                                                #
# 2022-09-29                                                          #
#                                                                     #
# DESCRIPTION                                                         #
# set domain name                                                     #
# example: ./smtp_check.sh domain.xx                                  #
#                                                                     #
# AUTHOR                                                              #
# MM - xxxxxxxxxxxxxxxxxxxxxxxxxxxxx                                  #
#                                                                     #
# CHANGELOG                                                           #
# v0.2                                                                #
#                                                                     #
#######################################################################

sleep=1
port=25
echo -e "[*] \e[32mDIG $1 \e[0m"

serwery=$(dig ANY @8.8.8.8 $1 | grep MX | awk '{print $6}')

while read -r line
do
    echo -e "[*] \e[32mCheck MX $line \e[0m"
    echo -e "[*] \e[32mTest 01 wysylam z obcej skrzynki na obcy adres w sieci Internet \e[0m"
    (echo "helo"
    sleep $sleep
    echo "ehlo mx.kprm.gov.pl"
    sleep $sleep
    echo "MAIL FROM: <seketariat@kprm.gov.pl>"
    sleep $sleep
    echo "RCPT TO: <pentesty@twoja_skrzynka.pl>"
    sleep $sleep
    echo "DATA"
    sleep $sleep
    echo "Subject: Pozdrowienia z pentestow"
    sleep $sleep
    echo "Dzien dobry,"
    sleep $sleep
    echo "Poproszę o odesłanie tej wiadomości w formie zalaczniki na adres email: pentesty@twoja_skrzynka.pl"
    sleep $sleep
    echo "Pozdrawiam"
    sleep $sleep
    echo "MM"
    sleep $sleep 
    echo "."
    sleep $sleep
    echo "quit"
    ) | telnet $line $port

    echo -e "[*] \e[32mCheck MX $line \e[0m"
    echo -e "[*] \e[32mTest 02 wysylam z obcej skrzynki na adres w wewnątrz organizacji \e[0m"
    (echo "helo"
    sleep $sleep
    echo "ehlo mx.kprm.gov.pl"
    sleep $sleep
    echo "MAIL FROM: <seketariat@kprm.gov.pl>"
    sleep $sleep
    echo "RCPT TO: <kontakt@$1>"
    sleep $sleep
    echo "DATA"
    sleep $sleep
    echo "Subject: Pozdrowienia z pentestow"
    sleep $sleep
    echo "Dzien dobry,"
    sleep $sleep
    echo "Poproszę o odesłanie tej wiadomości w formie zalaczniki na adres email: pentesty@twoja_skrzynka.pl"
    sleep $sleep
    echo "Pozdrawiam"
    sleep $sleep
    echo "MM"
    sleep $sleep 
    echo "."
    sleep $sleep
    echo "quit"
    ) | telnet $line $port

    echo -e "[*] \e[32mCheck MX $line \e[0m"
    echo -e "[*] \e[32mTest 03 wysylam ze skrzynki wewnątrz organizacji na adres w wewnątrz organizacji \e[0m"
    (echo "helo"
    sleep $sleep
    echo "ehlo mx.kprm.gov.pl"
    sleep $sleep
    echo "MAIL FROM: <seketariat@$1>"
    sleep $sleep
    echo "RCPT TO: <kontakt@$1>"
    sleep $sleep
    echo "DATA"
    sleep $sleep
    echo "Subject: Pozdrowienia z pentestow"
    sleep $sleep
    echo "Dzien dobry,"
    sleep $sleep
    echo "Poproszę o odesłanie tej wiadomości w formie zalaczniki na adres email: pentesty@twoja_skrzynka.pl"
    sleep $sleep
    echo "Pozdrawiam"
    sleep $sleep
    echo "MM"
    sleep $sleep 
    echo "."
    sleep $sleep
    echo "quit"
    ) | telnet $line $port
done < <(printf '%s\n' "$serwery")
