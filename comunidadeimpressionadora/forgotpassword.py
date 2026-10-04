import threading
from flask import render_template
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from comunidadeimpressionadora import database, app, mail

from .models import TokenRedefinicao
from datetime import datetime, timedelta, timezone

# Inicializa o serializador para criar tokens seguros
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# função para gerar o token
# Vamos criar uma função que cria uma chave especial para o usuário:
# def gerar_token(usuario):
#     s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     return s.dumps({'usuario_id': usuario.id})

def gerar_token(usuario):
    """
    Gera um token seguro contendo o ID do usuário e armazena no banco de dados.

    :param usuario: Objeto do modelo Usuario
    :return: String do token gerado
    """
    # Chave ('usuario_id'): É como um nome que você dá para o que está guardando.
    # Valor (usuario.id): Isso é o que você quer guardar dentro da caixa.
    # Cria um token seguro usando o serializador com o ID do usuário
    token_str = serializer.dumps({'usuario_id': usuario.id})
    
    # Calcula a data de expiração (1 hora a partir de agora)
    data_expiracao = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Cria um objeto TokenRedefinicao
    # adiciona o toekn, id do usuario e a data de expiracao no banco de dados.
    token = TokenRedefinicao(
        token=token_str,
        usuario_id=usuario.id,
        data_expiracao=data_expiracao
    )
    
    # Adiciona o token à sessão do banco de dados
    database.session.add(token)
    
    # Salva as alterações no banco de dados
    database.session.commit()
    
    return token_str


def validar_token(token_str):
    """
    Valida o token recebido. Verifica se o token existe, não foi usado e não expirou.

    :param token_str: String do token recebido
    :return: Objeto TokenRedefinicao se válido, caso contrário None
    """
    try:
        # Decodifica o token para obter os dados (ID do usuário)
        dados = serializer.loads(token_str, max_age=3600)  # 3600 segundos = 1 hora
        # pega o id do usuario
        usuario_id = dados.get('usuario_id')
        
        # Busca o token no banco de dados com os critérios: token igual, usuário correspondente e não usado
        token = TokenRedefinicao.query.filter_by(token=token_str,
                                                usuario_id=usuario_id,
                                                usado=False).first()
        
        if token:
            # Garantir que token.data_expiracao seja timezone-aware
            if token.data_expiracao.tzinfo is None:
                token.data_expiracao = token.data_expiracao.replace(tzinfo=timezone.utc)
            
            # Verifica se o token ainda é válido
            if token.data_expiracao >= datetime.now(timezone.utc):
                return token  # Token válido
            else:
                return None  # Token expirado
        else:
            return None  # Token não encontrado
    except Exception:
        # Em caso de erro (token inválido ou expirado), retorna None
        return None

# def enviar_email(email, token):
#     link = url_for('redefinir_senha', token=token, _external=True)
#     # Aqui você configuraria seu serviço de email para enviar o link
#     # Por simplicidade, vamos só imprimir o link
#     print(f'Clique no link para redefinir sua senha: {link}')


# Função que envia o e-mail em segundo plano (usando thread)
def enviar_email_thread(msg):
    with app.app_context():
        mail.send(msg)

# Função que prepara e inicia o envio de e-mail em uma thread
def enviar_email(email, assunto, template, **kwargs):
    """
    Envia um email contendo o link para redefinir a senha.
    :param email: Email do destinatário
    :param assunto: Assunto do email
    :param template: Nome do template HTML para o email
    :param kwargs: Argumentos adicionais para renderizar o template
    """
    msg = Message(assunto, recipients=[email])
    msg.html = render_template(template + '.html', **kwargs)

    # Cria uma thread para enviar o e-mail em segundo plano
    thread = threading.Thread(target=enviar_email_thread, args=(msg,))
    thread.start()  # Inicia a thread para enviar o e-mail
