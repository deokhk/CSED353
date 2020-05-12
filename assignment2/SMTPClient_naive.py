import ssl
from socket import *
import base64

username = 'deokhk@postech.ac.kr'
password = ''              # IMPORTANT NOTE!!!!!!!!!!: PLEASE REMOVE THIS FIELD WHEN YOU SUBMIT!!!!!

subject = 'Computer Network Assignment2 - Email Client'
from_ = 'deokhk@postech.ac.kr'
to_ = 'deokhk@postech.ac.kr'
content = 'It is so hard for me!!!'

# Message to send
endmsg = '\r\n.\r\n'

# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = 'smtp.office365.com'
port = 587

# 1. Establish a TCP connection with a mail server [2pt]

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, port))

# 2. Dialogue with the mail server using the SMTP protocol. [2pt]

recv_msg = clientSocket.recv(1024).decode()
print("Reponse after connection request:" + recv_msg)
if recv_msg[:3] != '220':
    print('220 reply not received from server.')

EhloCommand = 'EHLO\r\n'
clientSocket.send(EhloCommand.encode())
recv_msg = clientSocket.recv(1024).decode()
print("Reponse after EHLO command:" + recv_msg)
if recv_msg[:3] != '250':
    print('250 reply not received from server.')

# 3. Login using SMTP authentication using your postech account. [5pt]

# Send STARTTLS
StartTlsCommand = 'STARTTLS\r\n'
clientSocket.send(StartTlsCommand.encode())
recv_msg = clientSocket.recv(1024).decode()
print("Response after STARTTLS command:" + recv_msg)

# Wrap socket using ssl.PROTOCOL_SSLv23
clientSocket = ssl.wrap_socket(clientSocket, ssl_version=ssl.PROTOCOL_SSLv23)

# Use base64.b64encode for the username and password
username_encrypted = base64.b64encode(username.encode())
password_encrypted = base64.b64encode(password.encode())

# Send EHLO
clientSocket.send(EhloCommand.encode())
recv_msg = clientSocket.recv(1024).decode()
print("Response after EHLO command:" + recv_msg)
if recv_msg[:3] != '250':
    print('250 reply not received from server.')

# Send AUTH LOGIN
AuthLoginCommand = 'AUTH LOGIN\r\n'
clientSocket.send(AuthLoginCommand.encode())
recv_msg=clientSocket.recv(1024).decode()
print("Response after AUTH LOGIN command:" +recv_msg)

# Send Encrypted UserName
clientSocket.send(username_encrypted+'\r\n'.encode())
recv_msg=clientSocket.recv(1024).decode()
print("Response after sending encrypted username:" + recv_msg)

# Send Encrypted Password
clientSocket.send(password_encrypted+'\r\n'.encode())
recv_msg=clientSocket.recv(1024).decode()
print("Response after sending encrypted password:" + recv_msg)

# Send HELO
HeloCommand = 'HELO\r\n'
clientSocket.send(HeloCommand.encode())
recv_msg=clientSocket.recv(1024).decode()
print("Response after HELO command:" +recv_msg)

# 4. Send a e-mail to your POSTECH mailbox. [5pt]

# Send MAILFROM
MailFromCommand = "MAIL FROM:<" +from_ +">\r\n"
clientSocket.send(MailFromCommand.encode())
recv_msg = clientSocket.recv(1024).decode()
print("Response after MAIL FROM command: "+recv_msg)

# Send RCPTTO
RcptToCommand = "RCPT TO:<" +to_ +">\r\n"
clientSocket.send(RcptToCommand.encode())
recv_msg = clientSocket.recv(1024).decode()
print("Response after RCPT TO command: "+recv_msg)

# Send Data
data = "DATA\r\n"
clientSocket.send(data.encode())
recv_msg = clientSocket.recv(1024).decode()
print("Response after DATA command: "+recv_msg)

# Send Subject
SubjectMsg = "Subject: "+subject + "\r\n\r\n"
clientSocket.send(SubjectMsg.encode())

# Send Content
clientSocket.send(content.encode())
clientSocket.send(endmsg.encode())
recv_msg = clientSocket.recv(1024)

print("Response after sending message body:"+recv_msg.decode())

# 5. Destroy the TCP connection [2pt]

QuitCommand = "QUIT\r\n"
clientSocket.send(QuitCommand.encode())
recv_msg = clientSocket.recv(1024).decode()
print("Response after closing connection:"+recv_msg)
clientSocket.close()
