from flask_mail import Message
from flask import render_template, url_for
from comunidadeimpressionadora import mail
import random  # Para gerar códigos aleatórios
import string  # Para gerar strings, como o código de confirmação
from itsdangerous import URLSafeTimedSerializer  # Para criar tokens seguros
from comunidadeimpressionadora import app
import threading


def enviar_email_bem_vindo(usuario):
    # Cria o e-mail com o assunto e o destinatário
    msg = Message('Bem-vindo à Comunidade!', recipients=[usuario.email])
     # Gera o link com o domínio correto, substitua "meusite.com" pelo seu domínio
    link = url_for('perfil', _external=True)

    # Renderiza o template com o link correto
    # Renderiza o conteúdo HTML do e-mail
    msg.html = render_template('email_bem_vindo.html', usuario=usuario, link=link)
    
    # Envia o e-mail
    mail.send(msg)


def enviar_email_alteracao_senha(usuario):
    # Cria o e-mail com o assunto e o destinatário
    msg = Message('Alteração de Senha - Comunidade', recipients=[usuario.email])
    
    # Renderiza o conteúdo HTML do e-mail
    msg.html = render_template('email_alteracao_senha.html', usuario=usuario)
    
    # Envia o e-mail
    mail.send(msg)

def enviar_email_exclusao_conta(usuario):
    # Cria o e-mail com o assunto e o destinatário
    msg = Message('Conta Excluída - Comunidade', recipients=[usuario.email])
    
    # Renderiza o conteúdo HTML do e-mail
    msg.html = render_template('email_exclusao_conta.html', usuario=usuario)
    
    # Envia o e-mail
    mail.send(msg)

def enviar_email_confirmacao_redefinicao_senha(usuario):
    # Cria o e-mail com o assunto e o destinatário
    msg = Message(
        'Sua senha foi redefinida com sucesso!',
        recipients=[usuario.email]
    )
    
    # Renderiza o conteúdo HTML do e-mail usando o template
    msg.html = render_template('email_confirmacao_redefinicao_senha.html', usuario=usuario)
    
    # Envia o e-mail
    mail.send(msg)



# Função que envia o email usando uma thread
def enviar_email_thread(msg):
    with app.app_context():
        mail.send(msg)

# unção para gerar o código de confirmação (um código de 6 dígitos, por exemplo)
def gerar_codigo_confirmacao():
    return ''.join(random.choices(string.digits, k=6))  # Gera um código de 6 dígitos

# Função que gera o token seguro para enviar no link de confirmação
def gerar_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])  # Cria o serializer usando a chave secreta
    return serializer.dumps(email, salt='email-confirmation-salt')  # Gera o token com base no e-mail

# Função para confirmar o token enviado por e-mail (expira em 1 hora)
def confirmar_token(token, expiracao=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirmation-salt', max_age=expiracao)  # Verifica o token
    except:
        return False  # Retorna False se o token for inválido ou expirado
    return email  # Retorna o e-mail associado ao token se estiver tudo certo


# Função que gera a URL de confirmação com o token
def gerar_confirmar_url(usuario):
    token = gerar_token(usuario.email)  # Gera o token para o e-mail do usuário
    confirmar_url = url_for('confirmar_email', token=token, _external=True)
    # Substituir localhost pelo IP da sua máquina
    # Você pode modificar o link que é enviado no e-mail para usar o IP local do seu computador automaticamente. Modifique a geração do link de confirmação, alterando o url_for para usar o IP da sua máquina, em vez de localhost.
    return confirmar_url  # Retorna a URL gerada


# Função que envia o e-mail de confirmação contendo o link e o código de confirmação
def enviar_email_confirmacao(usuario):
    confirmar_url = gerar_confirmar_url(usuario)  # Gera a URL de confirmação
    codigo_confirmacao = usuario.codigo_confirmacao  # Pega o código de confirmação do usuário
    html = render_template('confirmar_email.html', confirmar_url=confirmar_url, codigo_confirmacao=codigo_confirmacao)  # Cria o corpo do e-mail
    msg = Message('Confirme seu E-mail', recipients=[usuario.email])
    msg.html = html  # Adiciona o HTML ao e-mail
    # Cria uma thread para enviar o e-mail em segundo plano
    thread = threading.Thread(target=enviar_email_thread, args=(msg,))
    thread.start()  # Inicia a thread para enviar o e-mail
