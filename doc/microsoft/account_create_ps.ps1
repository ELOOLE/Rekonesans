# bez hasla
New-LocalUser -Name "User02" -Description "Description of this account." -NoPassword

# z haslem
$Password = Read-Host -AsSecureString
New-LocalUser "User03" -Password $Password -FullName "Third User" -Description "Description of this account."
