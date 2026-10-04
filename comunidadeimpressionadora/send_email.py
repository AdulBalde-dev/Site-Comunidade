"""Small helper for sending an HTML message through the app's mail settings."""

from flask_mail import Message

from comunidadeimpressionadora import app, mail


def enviar_email(destinatario, assunto, corpo_html):
    mensagem = Message(assunto, recipients=[destinatario], html=corpo_html)
    with app.app_context():
        mail.send(mensagem)
