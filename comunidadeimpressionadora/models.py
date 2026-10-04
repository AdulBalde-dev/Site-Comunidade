# Arquivo de banco de dados
# para poder criar o banco de dados precisamos da instancia desse banco de dados que esta no main.py

from comunidadeimpressionadora import database, login_manager
from datetime import datetime, timezone
from flask_login import UserMixin

# encontrar o usuario apartir de um id
@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    # __tablename__ = 'usuarios'  # Nome da tabela no banco
    """
        Modelo de Usuário que representa os usuários do sistema.
    """
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(50), nullable=False)
    email = database.Column(database.String(120), nullable=False, unique=True)
    senha = database.Column(database.String(80), nullable=False)

    confirmado = database.Column(database.Boolean, default=False)
    data_confirmacao = database.Column(database.DateTime, nullable=True)
    codigo_confirmacao = database.Column(database.String(6), nullable=False)  # Código de confirmação

    foto_perfil = database.Column(database.String(50), nullable=False, default='default.jpg')
    cursos = database.Column(database.String(500), nullable=False, default='Nao Informado')

    # esse backref='autor' é para depois na tabela Post eu poder descobrir o autor do post
    # Nota Importante: Ao definir cascade='all, delete-orphan', você garante que quando um usuário for excluído, todos os posts associados a ele também serão excluídos automaticamente. Assim, não é necessário deletar os posts manualmente na rota.
    # Relação: Um usuário tem muitos posts
    posts = database.relationship('Post', backref='autor', lazy=True, cascade='all, delete-orphan')

    # Relacionamento com TokenRedefinicao
    # esse backref='usuario' é para depois na tabela TokenRedefinicao eu poder descobrir o usuario do que esse token pertence
    # Nota Importante: Ao definir cascade='all, delete-orphan', você garante que quando um usuário for excluído, todos os tokens_redefinicao associados a ele também serão excluídos automaticamente. Assim, não é necessário deletar os tokens_redefinicao manualmente na rota.
    # Relação:
    # Um Usuário pode ter muitos TokensRedefinicao.
    # Cada TokenRedefinicao pertence a um único Usuário.
    tokens_redefinicao = database.relationship('TokenRedefinicao', backref='usuario', lazy=True, cascade='all, delete-orphan')


    # quantidade de post que o cara tem
    def contar_posts(self):
        return len(self.posts)

    def __repr__(self):
        return f'<Usuário {self.username}>'
    
    def is_active(self):
        return self.confirmado  # Retorna se o usuário está ativo (se confirmou o e-mail)

class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String(50), nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    # Use datetime.now(timezone.utc) para criar um datetime consciente do fuso horário UTC
    data_criacao = database.Column(database.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # 'usuario.id' é a minha tabela de Usuario pegando o id
    id_usuario = database.Column(database.Integer,  database.ForeignKey('usuario.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.id} de Usuário {self.id_usuario}>'



class Contato(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String(100), nullable=False)
    email = database.Column(database.String(100), nullable=False)
    mensagem = database.Column(database.Text, nullable=False)


class TokenRedefinicao(database.Model):
    """
    Modelo para armazenar tokens de redefinição de senha.
    """
    id = database.Column(database.Integer, primary_key=True)  # Identificador único
    token = database.Column(database.String(255), unique=True, nullable=False)  # Token único
    usuario_id = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)  # ID do usuário

    # expiracao = database.Column(database.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))  # Data de expiração
    data_expiracao = database.Column(database.DateTime(timezone=True), nullable=False)  # Data e hora de expiração do token
    usado = database.Column(database.Boolean, default=False, nullable=False)  # Indica se o token já foi usado
