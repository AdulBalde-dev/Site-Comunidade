from comunidadeimpressionadora import app, database
from comunidadeimpressionadora.models import Usuario, Post, Contato, TokenRedefinicao


with app.app_context():
    database.create_all()

################################
# with app.app_context():
#     usuario = Usuario(
#         username='Alai',
#         email='tenw313@gmail.com',
#         senha='12345'
#     )

#     usuario2 = Usuario(
#         username='Maincon',
#         email='alaiseide2002@gmail.com',
#         senha='1111111'
#     )
#     database.session.add(usuario)
#     database.session.add(usuario2)
#     database.session.commit()

# pegando informacoes do meu banco de dados

# with app.app_context():
#     meus_usuarios = Usuario.query.all()
#     print(meus_usuarios)
#     primeiro_usuario = meus_usuarios[0]
#     print(primeiro_usuario.posts)
#     segundo_usuario = meus_usuarios[1]
#     print(segundo_usuario.email)

# with app.app_context():
#     usuario_teste = Usuario.query.filter_by(id=2).first()
#     print(usuario_teste)
#     usuario = Usuario.query.filter_by(email='tenw313@gmail.com').first()
#     print(usuario)
#     print(usuario_teste.username)


# # Criar um usuario
# usuario3 = Usuario(username='Adul', email='baldeadul70@outlook.com', senha= '12345')
# # adicionar o usuario no meu banco de dados
# with app.app_context():
#     database.session.add(usuario3)
#     database.session.commit()

# fazer busca no meu banco de dados
# with app.app_context():
      # pegar o primeiro usuario
#     primeiro_usuario = Usuario.query.first()
#     print(primeiro_usuario.email)

    # pegar todos os usuarios
    # meus_usuarios = Usuario.query.all()
    # print(meus_usuarios[2].senha)


# fazendo busca no meu banco de dados e filtrando baseado numa condicao
# with app.app_context():
#     usuario_teste = Usuario.query.filter_by(id=2).first()
#     print(usuario_teste.email)

# Criando um posto

# with app.app_context():
#     meu_post = Post(titulo='primeiro poste de alai', id_usuario=1, corpo='Eu voando')
#     database.session.add(meu_post)
#     database.session.commit()


# fazendo busca no meu banco de dados
# with app.app_context():
#     meus_postes = Post.query.all()
#     print(meus_postes[0].autor.email)


# deletar tudo e criar o banco de dados de novo
# with app.app_context():
#     database.drop_all()
#     database.create_all()

# with app.app_context():
#     meus_usuarios = Usuario.query.all()
#     print(meus_usuarios[2].senha)

# with app.app_context():
#     usuario2 = Usuario.query.filter_by(username='Maicon').first()
#     print(usuario2.senha)


# from flask_bcrypt import generate_password_hash, check_password_hash

# password = "meinPasswort123"
# hashed_password = generate_password_hash(password)

# print(hashed_password)
# # verificar se a senha é igual a hash
# print(check_password_hash(hashed_password ,password))
# print(len(hashed_password))  # Ausgabe: 60
