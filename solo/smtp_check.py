import random
import smtplib
import string
from email.message import EmailMessage
import base64

def body_of_email():
    body = """\
    Witaj,

    W związku z przeprowadzonymi testami penetracyjnymi, chcielibyśmy poinformować, że w systemie występują następujące podatności.
    Jedną z nich jest możliwość wysyłania korespondencji e-mail z dowolnego adresu e-mail. W celu zabezpieczenia systemu przed atakami typu phishing, zalecamy zaimplementowanie mechanizmu SPF, DKIM oraz DMARC.
    Prosimy o przekazanie tej wiadomości w formie załącznika na nasz adres.
    
    Z poważaniem,\nZespół ds. pentestów\n"""
    return body

def subject_of_email():
    email_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"Testowy e-mail {email_id}"

def attach_pdf(msg, pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    #pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename='attachment.pdf')

def send_email(addr, subject, body, pdf_path):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'your_email@example.com'
    msg['To'] = addr
    msg.set_content(body)

    attach_pdf(msg, pdf_path)

    smtpObj = smtplib.SMTP('smtp.example.com', 25)
    smtpObj.ehlo()
    smtpObj.starttls()
    #smtpObj.login('username', 'password')
    smtpObj.send_message(msg)
    smtpObj.quit()

if __name__ == '__main__':
    addr = 'recipient@example.com'
    subject = subject_of_email()
    body = body_of_email()
    pdf_path = '/path/to/your/attachment.pdf'
    send_email(addr, subject, body, pdf_path)
