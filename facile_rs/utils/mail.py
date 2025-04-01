import smtplib


def send_mail(smtp_server, from_addr, to_addrs, subject, message):
    with smtplib.SMTP(smtp_server) as smtp:
        smtp.sendmail(from_addr, to_addrs, f'''
From: {from_addr}
To: {to_addrs}
Subject: {subject}

{message}
''')
