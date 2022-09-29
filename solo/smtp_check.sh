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



echo -e "[*] \e[32mDIG $1 \e[0m"

serwery=$(dig ANY @194.204.152.34 $1 | grep MX | awk '{print $6}')

while read -r line
do
    echo -e "[*] \e[32mCheck MX $line \e[0m"
    echo -e "[*] \e[32mTest 01 wysylam z obcej skrzynki na obcy adres w sieci Internet \e[0m"
    (echo "helo"
    sleep 2
    echo "ehlo mx.kprm.gov.pl"
    sleep 2
    echo "MAIL FROM: <seketariat@kprm.gov.pl>"
    sleep 2
    echo "RCPT TO: <pentesty@twoja_skrzynka.pl>"
    sleep 2
    echo "DATA"
    sleep 2
    echo "Subject: Pozdrowienia z pentestow"
    sleep 2
    echo "Dzien dobry,"
    sleep 2
    echo "Poproszę o odesłanie tej wiadomości w formie zalaczniki na adres email: pentesty@twoja_skrzynka.pl"
    sleep 2
    echo "Pozdrawiam"
    sleep 2
    echo "MM"
    sleep 2 
    echo "."
    sleep 2
    echo "quit"
    ) | telnet $line 25

    echo -e "[*] \e[32mCheck MX $line \e[0m"
    echo -e "[*] \e[32mTest 02 wysylam z obcej skrzynki na adres w wewnątrz organizacji \e[0m"
    (echo "helo"
    sleep 2
    echo "ehlo mx.kprm.gov.pl"
    sleep 2
    echo "MAIL FROM: <seketariat@kprm.gov.pl>"
    sleep 2
    echo "RCPT TO: <kontakt@$1>"
    sleep 2
    echo "DATA"
    sleep 2
    echo "Subject: Pozdrowienia z pentestow"
    sleep 2
    echo "Dzien dobry,"
    sleep 2
    echo "Poproszę o odesłanie tej wiadomości w formie zalaczniki na adres email: pentesty@twoja_skrzynka.pl"
    sleep 2
    echo "Pozdrawiam"
    sleep 2
    echo "MM"
    sleep 2 
    echo "."
    sleep 2
    echo "quit"
    ) | telnet $line 25

    echo -e "[*] \e[32mCheck MX $line \e[0m"
    echo -e "[*] \e[32mTest 03 wysylam ze skrzynki wewnątrz organizacji na adres w wewnątrz organizacji \e[0m"
    (echo "helo"
    sleep 2
    echo "ehlo mx.kprm.gov.pl"
    sleep 2
    echo "MAIL FROM: <seketariat@$1>"
    sleep 2
    echo "RCPT TO: <kontakt@$1>"
    sleep 2
    echo "DATA"
    sleep 2
    echo "Subject: Pozdrowienia z pentestow"
    sleep 2
    echo "Dzien dobry,"
    sleep 2
    echo "Poproszę o odesłanie tej wiadomości w formie zalaczniki na adres email: pentesty@twoja_skrzynka.pl"
    sleep 2
    echo "Pozdrawiam"
    sleep 2
    echo "MM"
    sleep 2 
    echo "."
    sleep 2
    echo "quit"
    ) | telnet $line 25
done < <(printf '%s\n' "$serwery")
