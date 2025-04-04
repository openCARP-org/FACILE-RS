import smtplib

TEMPLATE = '''
From: {from_addr}
To: {to_addrs}
Subject: {subject}

{message}
'''

def send_mail(smtp_server, from_addr, to_addrs, subject, message):
    with smtplib.SMTP(smtp_server) as smtp:
        smtp.sendmail(from_addr, to_addrs, TEMPLATE.format(
            from_addr=from_addr,
            to_addrs=to_addrs,
            subject=subject,
            message=message
        ))
