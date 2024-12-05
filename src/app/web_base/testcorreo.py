import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
smtp_server = 'smtp-es.securemail.pro'  # Tu servidor SMTP aquí
smtp_port = 587  # El puerto SMTP, suele ser 587 para TLS
smtp_username = 'info@yml-multilanguage.com'  # Tu nombre de usuario SMTP
smtp_password = 'Pppp54321!#'  # Tu contraseña SMTP


from_addr = 'info@yml-multilanguage.com'
to_addr = 'pabloantoniodel@gmail.com'
subject = 'Asunto del mensaje'

# Crear el objeto del mensaje
message = MIMEMultipart()
message['From'] = from_addr
message['To'] = to_addr
message['Subject'] = subject

# Agrega el cuerpo del mensaje, aquí es texto plano pero también puedes enviar HTML.
body = 'Este es el cuerpo de tu correo electrónico.'
message.attach(MIMEText(body, 'plain'))
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()  # Iniciar cifrado TLS
server.login(smtp_username, smtp_password)
server.sendmail(from_addr, to_addr, message.as_string())
server.quit()  # Cerrar la conexión