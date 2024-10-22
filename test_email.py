

import smtplib

FROMADDR = "fd912735@gmail.com"
LOGIN    = FROMADDR
PASSWORD = "yrvz ttwz bfyl vyuk"
TOADDRS  = ["fd912735@gmail.com"]
SUBJECT  = "Test"

msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n"
       % (FROMADDR, ", ".join(TOADDRS), SUBJECT) )
msg += "some text\r\n"

server = smtplib.SMTP('smtp.gmail.com', 587)
server.set_debuglevel(1)
server.ehlo()
server.starttls()
server.login(LOGIN, PASSWORD)
server.sendmail(FROMADDR, TOADDRS, msg)
server.quit()

        