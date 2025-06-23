# import the smtplib module. It should be included in Python by default
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def montar_email():
    pass

def enviar_email(srvmail, login, senha, destinatarios, assunto, corpo_email, lista_anexos):
    qtd_dest = destinatarios.count('@')
    # Se há destinatários, envia o e-mail para cada um deles
    if qtd_dest > 0:
        lst_dest = destinatarios.split(',')
        idx = 0
        while idx < qtd_dest:
            # Cria o documento com várias partes
            msg = MIMEMultipart()
            msg["From"] = login
            destinatario = lst_dest[idx]
            msg["To"] = destinatarios
            msg["Subject"] = assunto
            imgFilename = ''
            for anexo in lista_anexos:
                # Anexa a imagem
                nome_anexo = lista_anexos + '_anexo'
                imgFilename = nome_anexo  # Repare que é diferente do nome do arquivo local!
                with open(lista_anexos, 'rb') as f:
                    msgImg = MIMEImage(f.read(), name=imgFilename)
                msg.attach(msgImg)
            # Anexa o corpo do texto
            msgText = MIMEText('<b>{}</b><br><img src="cid:{}"><br>'.format(corpo_email, imgFilename), 'html')
            msg.attach(msgText)
            # Login Credentials for sending the mail
            srvmail.sendmail(login, destinatario, msg.as_string())
            idx = idx + 1
    status = 'Email enviado'

def criar_servidor_email(smtpsrv, login, senha):
    srvmail = smtplib.SMTP(smtpsrv)
    srvmail.starttls()
    srvmail.login(login, senha)
    return srvmail


