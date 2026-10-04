from flask import render_template, redirect, url_for, flash, request, abort, session
from comunidadeimpressionadora import app, database, bcrypt
from comunidadeimpressionadora.forms import FormCriarConta, FormLogin, FormEdiarPerfil, ContatoForm, FormCriarPost, ConfirmarExclusaoContaForm, EsqueciSenhaForm, RedefinirSenhaForm, AlterarSenhaForm, ConfirmacaoEmailForm
from comunidadeimpressionadora.models import Usuario, Contato, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from functools import wraps
from PIL import Image
from comunidadeimpressionadora.forgotpassword import gerar_token, validar_token, enviar_email
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from comunidadeimpressionadora.utils import enviar_email_bem_vindo, enviar_email_alteracao_senha, enviar_email_exclusao_conta, enviar_email_confirmacao_redefinicao_senha, enviar_email_confirmacao, confirmar_token, gerar_codigo_confirmacao

# from flask_babel import gettext
# # No início de routes.py, após os imports
# print("Tipo de babel:", type(babel))
# print("Atributos do babel:", dir(babel))

# pagina principal
@app.route("/")
def home():
    # ordenar os post do recentes para mais antigos order_by(Post.id.desc())
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)


# pagina de contato
@app.route("/contato", methods=['GET', 'POST'])
def contato():
        contatoform = ContatoForm()
        if contatoform.validate_on_submit():
            contato = Contato(
                            nome=contatoform.nome.data,
                            email=contatoform.email.data,
                            mensagem=contatoform.mensagem.data
                        )

            database.session.add(contato)
            database.session.commit()
            flash('Sua mensagem foi enviada com sucesso!', 'alert-success')
        elif request.method == 'GET' and current_user.is_authenticated:
           contatoform.nome.data = current_user.username
           contatoform.email.data = current_user.email

        # Configuração do email
        # meu_email = "alaiseide2006@gmail.com"  # Substitua pelo seu email

        # # Criar a mensagem
        # msg = MIMEMultipart()
        # msg['From'] = meu_email
        # msg['To'] = meu_email  # Você pode substituir por qualquer outro email
        # msg['Subject'] = "Nova mensagem de contato"
        # corpo_email = f"Nome: {contatoform.nome.data}\nEmail: {contatoform.email.data}\nMensagem:\n{contatoform.mensagem.data}"
        # msg.attach(MIMEText(corpo_email, 'plain'))

        # # Enviar o email
        # server = smtplib.SMTP('smtp.gmail.com', 587)  # Use o servidor SMTP do seu provedor de email
        # server.starttls()
        # server.login(meu_email, minha_senha)
        # text = msg.as_string()
        # server.sendmail(meu_email, meu_email, text)
        # server.quit()
        # Aqui você pode adicionar o código para lidar com os dados do formulário de contato
        # Por exemplo, você pode enviar um e-mail com a mensagem ou armazená-la em um banco de dados

        return render_template('contato.html', contatoform=contatoform)

# pagina de usuarios
@app.route("/usuarios")
@login_required
def usuarios():
    # meus_usuarios=lista_usuarios está dentro da minha funcao render_template() para poderem ser mostrados dentro da minha pagina html

    # pegando todos os usuarios do meu banco de dados 
    lista_usuarios = Usuario.query.all()
    ## print(lista_usuarios)
    return render_template('usuarios.html', meus_usuarios=lista_usuarios)


# pagina de login e criar_conta
# A funcao e uma pagina de formulario tem que ter o metodo POST/GET
@app.route('/login', methods=['GET', 'POST'])
def login(): 
    # se o usuario estiver autenticado redireciona para o home, impedir ele de acessar a pagina de login
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # instanciando o meu formulario de login a minha classe FormLogin()
    form_login = FormLogin()

    # instanciando o meu formulario de criar_conta a minha classe FormCriarConta()
    form_criarconta = FormCriarConta()
    # Verifica se o usuario fez login com sucesso
    if 'botao_submit_login' in request.form and form_login.validate_on_submit():
        # Então, resumindo, essa linha de código está procurando no banco de dados pelo usuário que possui o email fornecido no formulário de login e armazenando esse usuário na variável usuario.
        usuario = Usuario.query.filter_by(email = form_login.email.data).first()
        #print(usuario.senha)
        # se o usuario existe e se a senha que ele preencheu é a mesma que ta no banco de dados
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            # deixa o usuario fazer login se ele ja confirmou o seu email
            if usuario.confirmado:
                # fazendo login do usuario
                login_user(usuario, remember=form_login.lembrar_dados.data)
                # exibir msg de login feito com sucesso aseguido do e-amil dessa pessoal
                flash(f'Login feito com sucesso no e-mail: {form_login.email.data}', 'alert-success')
                # redirecionar para outra pagina
                # o return deve estar sempre atras do redirect(url_for('home'))

                # Obtém o parâmetro 'next' da query string da URL, que é geralmente usado para redirecionar o usuário após o login.
                parametro_next = request.args.get('next')
                # Verifica se o parâmetro 'next' foi fornecido na query string.
                destino = urlparse(urljoin(request.host_url, parametro_next or ""))
                if parametro_next and destino.scheme in {"http", "https"} and destino.netloc == request.host:
                    # Se o parâmetro 'next' estiver presente, redireciona o usuário para o URL fornecido pelo parâmetro 'next'.
                    return redirect(parametro_next)
                else:
                    # Se o parâmetro 'next' não estiver presente, redireciona o usuário para a página inicial ('home') da aplicação.
                    return redirect(url_for("home"))
            else:
                flash(f'Por favor, confirme o seu e-mail para poder acessar sua conta e fazer login.','alert-info')
                return redirect(url_for("unconfirmed"))
        else:
            flash(f'Falha no Login. E-mail ou Senha Incorretos.','alert-danger')

            
        """
        request.form é um dicionário que contém todos os campos do formulário. A chave é o nome do campo e o valor é o valor do campo. Então, 'botao_submit_criarconta' in request.form verifica se a chave 'botao_submit_criarconta' está presente no dicionário request.form, o que significaria que o botão de submit do formulário de criação de conta foi pressionado."""
   
    # Verifica se o usuario criou conta com sucesso
    if 'botao_submit_criarconta' in request.form and form_criarconta.validate_on_submit():
        # Gera o código de confirmação
        codigo_confirmacao = gerar_codigo_confirmacao()  # Gera o código de 6 dígitos
        # print(request.form)
        # criptografar a senha
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
        #print(senha_cript)
        # Criar o usuario
        # adicionar na sessao
        # dar commit da sessao
        usuario = Usuario(username=form_criarconta.username.data, 
                          email=form_criarconta.email.data, 
                          senha=senha_cript, 
                          codigo_confirmacao=codigo_confirmacao)
        database.session.add(usuario)
        database.session.commit()
        enviar_email_confirmacao(usuario)  # Envia o e-mail de confirmação para o usuário
        flash('Um e-mail de confirmação foi enviado. Verifique sua caixa de entrada.', 'alert-success')  # Notifica o usuário
        # fazendo login do usuario
        # login_user(usuario)

        # Envia o e-mail de boas-vindas
        #enviar_email_bem_vindo(usuario)
        # exibir msg de conta criada com sucesso
        #flash(f'Conta Criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        # redirecionar para outra pagina
        # o return deve estar sempre atras do redirect(url_for('home'))
        return redirect(url_for("home"))

    # form_login=form_login, form_criarconta=form_criarconta está dentro da minha funcao render_template() para poderem ser mostrados dentro da minha pagina html
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


# Rota para confirmar o e-mail usando o token e o código de confirmação
@app.route('/confirmar/<token>', methods=['GET', 'POST'])
def confirmar_email(token):
    form = ConfirmacaoEmailForm()  # Instancia o formulário de confirmação
    email = confirmar_token(token)  # Confirma o token e obtém o e-mail
    if not email:
        flash('O link de confirmação é inválido ou expirou.', 'alter-danger')  # Se o token for inválido ou expirado, mostra erro
        return redirect(url_for('login'))  # Redireciona para o login

    usuario = Usuario.query.filter_by(email = email).first_or_404()  # Procura o usuário pelo e-mail no banco de dados
    if usuario.confirmado:  # Se o e-mail já foi confirmado, avisa o usuário
        flash('Conta já confirmada. Por favor, faça login.', 'alert-info')
        return redirect(url_for('login'))

    if form.validate_on_submit():  # Se o formulário for enviado
        # Concatenar os valores dos campos do formulário para formar o código completo
        codigo_digitado = ''.join([
            form.code1.data,
            form.code2.data,
            form.code3.data,
            form.code4.data,
            form.code5.data,
            form.code6.data
        ])
        if codigo_digitado == usuario.codigo_confirmacao:  # Verifica se o código está correto
            usuario.confirmado = True  # Marca o usuário como confirmado
            usuario.data_confirmacao = datetime.now(timezone.utc)  # Salva a data de confirmação
            database.session.commit()  # Salva as mudanças no banco de dados
            enviar_email_bem_vindo(usuario)
            flash('Sua conta foi confirmada! Agora você pode fazer login.', 'alert-success')  # Mensagem de sucesso
            return redirect(url_for('login'))  # Redireciona para a página de login
        else:
            flash('Código de confirmação inválido. Tente novamente.', 'alert-danger')  # Se o código estiver errado, mostra erro

    return render_template('confirmar_codigo.html', form=form)  # Renderiza a página para inserir o código

# Decorador para rotas que exigem que o usuário tenha o e-mail confirmado
def login_com_confirmacao(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmado:  # Se o usuário não confirmou o e-mail
            flash('Por favor, confirme seu e-mail para acessar esta página.', 'alert-info')
            return redirect(url_for('unconfirmed'))  # Redireciona para a página de e-mail não confirmado
        return f(*args, **kwargs)
    return decorated_function

# Rota para informar ao usuário que ele ainda não confirmou o e-mail
@app.route('/unconfirmed')
def unconfirmed():
    if current_user.is_authenticated and not current_user.confirmado:
        flash('Por favor, confirme seu e-mail.', 'alert-info')  # Avisa o usuário para confirmar o e-mail
    return render_template('unconfirmed.html')  # Renderiza a página de confirmação pendente

# pagina de sair
@app.route('/sair', methods=['POST'])
@login_required
def sair():
    # sair e redirecionar para a pagina home
    logout_user()
    flash('Logout feito com Sucesso', 'alert-success')
    return redirect(url_for('home'))

# pagina de ver o perfil
@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = f'/static/fotos_perfil/{current_user.foto_perfil}'
    # foto_perfil = url_for(f'static', filename='fotos_perfil/{current_user.foto_perfil}')
    return render_template('perfil.html', foto_perfil=foto_perfil)

# pagina de criar post
@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    formcriarpost = FormCriarPost()

    if formcriarpost.validate_on_submit():
        post = Post(titulo=formcriarpost.titulo.data, 
                    corpo=formcriarpost.corpo.data, 
                    autor=current_user
                )
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', formcriarpost=formcriarpost)


# uma funcao que vai fazer todas as validacoes da imagem e salvar-la
def salvar_imagem(imagem):
    # adicionar um codigo aleatorio no nome da imagem
    codigo = secrets.token_hex(8)
    # separar o nome do arquivo com a extensao
    _, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = codigo + extensao.lower()
    # salvar a imagem na pasta fotos_perfil
    #  o app.root_path seria o caminho do novo app que é comunidadeimpressionadora
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    # reduzir o tamanho da imagem
    # 200x200 px
    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida = imagem_reduzida.convert('RGB')
    imagem_reduzida.thumbnail(tamanho)
    # salvar a imagem na pasta fotos_perfil
    imagem_reduzida.save(caminho_completo)
    # mudar o campo foto_perfil do usuario para o novo nome
    return nome_arquivo

# uma funcao para atualizar os cursos 
def atualizar_cursos(formulario):
    lista_cursos = []
    # percorrer todos os campos de cursos do formulario
    for campo in formulario:
        # verifica se o campo do formulario comeca com curso_
        if 'curso_' in campo.name:
            # verificar se o campo for marcado
            if campo.data:
                # adicionar o texto do campo.label  (Excel Impressionador) na lista de cursos
                lista_cursos.append(campo.label.text)
    # Então, se lista_cursos fosse ['Curso1', 'Curso2', 'Curso3'], a linha de código retornaria a string 'Curso1;Curso2;Curso3'. Espero que isso esclareça! Se você tiver mais perguntas, fique à vontade para
    return ';'.join(lista_cursos)


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    # uma instancia da minha classe FormEdiarPerfil
    formeditarperfil = FormEdiarPerfil()
    # validar o meu formulario
    if formeditarperfil.validate_on_submit():
        # mudar o email e o username do usuario
        current_user.email = formeditarperfil.email.data
        current_user.username = formeditarperfil.username.data
        # verificar se eu tenho que mudar a foto de perfil
        if formeditarperfil.foto_perfil.data:
            # adicionar um codigo aleatorio no nome da imagem
            # reduzir o tamanho da imagem
            # salvar a imagem na pasta fotos_perfil
            # mudar o campo foto_perfil do usuario para o novo nome da imagem
            nome_imagem = salvar_imagem(formeditarperfil.foto_perfil.data)
            #print(formeditarperfil.foto_perfil.data)
            # mudar a foto do perfil
            current_user.foto_perfil = nome_imagem
        # Atualizar os cursos do usuarios
        current_user.cursos = atualizar_cursos(formeditarperfil)

        database.session.commit()
        flash(f'Perfil Atualizado com Sucesso', 'alert-success')
        # redirecionar para a pagina do perfil dele
        return redirect(url_for('perfil'))
    
    # preencher o formulario automaticamente
    # Verifica se a requisição HTTP é do tipo GET, ou seja, se é a primeira vez que a página está sendo carregada.
    elif request.method == 'GET':
        # Se a requisição for do tipo GET, preenche os campos do formulário de edição de perfil com os dados atuais do usuário.
        # Preenche o campo de e-mail com o e-mail atual do usuário logado.
        formeditarperfil.email.data = current_user.email
        # Preenche o campo de nome de usuário com o nome de usuário atual do usuário logado.
        formeditarperfil.username.data = current_user.username
    
    foto_perfil = f'/static/fotos_perfil/{current_user.foto_perfil}'
    # foto_perfil = url_for(f'static', filename='fotos_perfil/{current_user.foto_perfil}')
    return render_template('editarperfil.html', foto_perfil=foto_perfil, formeditarperfil=formeditarperfil)




# O decorador @app.route é usado para associar uma URL a uma função específica.
# Neste caso, a URL é '/post/<post_id>'. '<post_id>' é uma variável na URL.
# Esta é a definição da função 'exibir_post'. Ela é chamada quando a URL acima é acessada.
# A função recebe um argumento, 'post_id', que é o valor da variável na URL.
@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):

    # Aqui, 'Post.query.get(post_id)' está fazendo uma consulta ao banco de dados para obter o post com o id especificado.
    # 'Post' é presumivelmente uma classe que representa uma postagem no seu banco de dados.
    # 'query' é um objeto que permite fazer consultas ao banco de dados.
    # 'get(post_id)' está buscando o post com o id especificado.
    post = Post.query.get_or_404(post_id)

    # Aqui, estamos verificando se o usuário atual é o autor do post.
    # Se for, criamos um novo formulário de edição de post.
    # Se não for, definimos 'form' como None. Isso pode ser útil para controlar o que é exibido para o usuário na página.
    if current_user == post.autor:

        formeditarpost = FormCriarPost()
        if request.method == 'GET':
            # preencher os campos de titulo e corpo  automaticamente
            formeditarpost.titulo.data = post.titulo
            formeditarpost.corpo.data = post.corpo

        elif formeditarpost.validate_on_submit():
            # formeditarpost.titulo.data é o formulario que o cara preencheu
            post.titulo = formeditarpost.titulo.data
            post.corpo = formeditarpost.corpo.data
            # posso dar so database.session.commit() porque ele ja existe no meu banco de dados
            database.session.commit()
            flash('Post Atualizado com Sucesso', 'alert-success')
            return redirect(url_for('home'))
    else:
        formeditarpost = None

    # Aqui, estamos renderizando o template 'post.html' e passando o post e o formulário para o template.
    # Isso permitirá que você use os dados do post e do formulário no seu template.
    return render_template('post.html', post=post, formeditarpost=formeditarpost)


# Esta linha define a rota para excluir um post. Ela aceita tanto métodos GET quanto POST.
@app.route('/post/<int:post_id>/excluir', methods=['POST'])
# O decorador @login_required garante que o usuário deve estar logado para acessar esta rota.
@login_required
# Esta é a função que será chamada quando a rota acima for acessada.
def excluir_post(post_id):


    # Aqui, estamos buscando o post com o id especificado do banco de dados.
    post = Post.query.get_or_404(post_id)

    # Verificamos se o usuário atual é o autor do post.
    if current_user == post.autor:

        # Se for, excluímos o post do banco de dados e confirmamos a transação.
        database.session.delete(post)
        database.session.commit()

        # Exibimos uma mensagem para o usuário informando que o post foi excluído com sucesso.
        flash('Post Excluido com Sucesso', 'alert-danger')

        # Redirecionamos o usuário para a página inicial.
        return redirect(url_for('home'))

    # Se o usuário atual não for o autor do post, retornamos um erro 403 (Proibido).
    else:
        abort(403)



# @babel.localeselector
# def get_locale():
#     return session.get('language', 'pt')

# # Rota para definir o idioma
# @app.route('/set_language/<language>')
# def set_language(language):
#     session['language'] = language
#     flash(gettext('Idioma alterado com sucesso!'), 'alert-success')
#     return redirect(request.referrer or url_for('perfil'))



##############
# Usuário diz que esqueceu a senha.
# Nós enviamos um link especial para o email dele.
# Ele clica no link e escolhe uma nova senha.
# Atualizamos a senha na nossa caixinha.

# Página para o usuário dizer que esqueceu a senha

# @app.route('/esqueci_senha', methods=['GET', 'POST'])
# def esqueci_senha():
#     if current_user.is_authenticated:
#         # Usuário já está logado, redirecionar para a página inicial ou perfil
#         return redirect(url_for('perfil'))  # Substitua 'inicio' pela rota adequada

#     if request.method == 'POST':
#         email = request.form['email']
#         # Aqui vamos procurar o usuário pelo email
#         usuario = Usuario.query.filter_by(email=email).first()
#         # se existir usuario
#         if usuario:
#             # Criar um token (chave especial)
#             token = gerar_token(usuario)
#             # Enviar o email com o link mágico
#             enviar_email(usuario.email, token)
#             flash('Um email foi enviado com instruções para redefinir sua senha.', 'alert-success')
#         else:
#             flash('Email não encontrado.', 'alert-info')
#         return redirect(url_for('login'))
#     return render_template('esqueci_senha.html')

@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if current_user.is_authenticated:
        return redirect(url_for('perfil'))
    form = EsqueciSenhaForm()  # Cria uma instância do formulário
    if form.validate_on_submit():  # Verifica se o formulário foi enviado e é válido
        email = form.email.data  # Obtém o email do formulário
        # Procurar o usuário pelo email
        usuario = Usuario.query.filter_by(email=email).first()  # Busca o usuário pelo email
        if usuario:
            # Gera um token para o usuário
            token = gerar_token(usuario)
            # Gera o link completo para redefinir a senha
            link = url_for('redefinir_senha', token=token, _external=True)
            # Enviar o email
            enviar_email(
                email=usuario.email,
                assunto='Redefinição de Senha - Comunidade Impressionadora',
                template='email_redefinir_senha',
                usuario=usuario,
                link=link,
                ano_atual=datetime.now().year
            )
            flash('Um email foi enviado com instruções para redefinir sua senha.', 'alert-success')
            return redirect(url_for('login'))
        else:
            flash('Email não encontrado.', 'alert-danger')
            return redirect(url_for('esqueci_senha'))
    return render_template('esqueci_senha.html', form=form)




@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    if current_user.is_authenticated:
        # Usuário já está logado, redirecionar para a página inicial ou perfil
        return redirect(url_for('home'))  # Substitua 'inicio' pela rota adequada
    """
    Rota para redefinir a senha usando o token recebido.
    """
    # Valida o token
    token_obj = validar_token(token)
    if not token_obj:
            # Se o token for inválido ou expirou, exibe uma mensagem de erro
            flash('O link é inválido ou expirou.', 'alert-danger')
            return redirect(url_for('esqueci_senha'))
    
    # Busca o usuário associado ao token pelo id desse usuario
    usuario = Usuario.query.get(token_obj.usuario_id)

    if not usuario:
        # Se o usuário não for encontrado, exibe uma mensagem de erro
        flash('Usuário não encontrado.', 'alert-danger')
        return redirect(url_for('esqueci_senha'))
    
    form = RedefinirSenhaForm()  # Cria uma instância do formulário de redefinição de senha

    if form.validate_on_submit():  # Verifica se o formulário foi enviado e é válido
        if bcrypt.check_password_hash(usuario.senha, form.senha.data):  # Comparação com o usuário buscado pelo token
            flash('A nova senha não pode ser igual à antiga.', 'alert-danger')
        else:
            nova_senha = form.senha.data  # Obtém a nova senha do formulário
            
            # Atualiza a senha do usuário utilizando Flask-Bcrypt
            usuario.senha = bcrypt.generate_password_hash(nova_senha).decode('utf-8')
            
            # Marca o token como usado para evitar reuso
            token_obj.usado = True
            
            # Salva as alterações no banco de dados
            database.session.commit()
            
            # Envia o e-mail de confirmação de redefinição de senha
            enviar_email_confirmacao_redefinicao_senha(usuario)

            # Exibe uma mensagem de sucesso
            flash('Sua senha foi redefinida com sucesso!', 'alert-success')
            return redirect(url_for('home'))
    
    # Renderiza o formulário de redefinir_senha.html
    return render_template('redefinir_senha.html', form=form)


@app.route('/alterar_senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        # As validações já são tratadas no formulário
        # Atualiza a senha do usuário
        # codifica a senha que o usuario digitou no formulario
        nova_senha_hash = bcrypt.generate_password_hash(form.nova_senha.data).decode('utf-8')
        # muda a senha o usuario
        current_user.senha = nova_senha_hash
        database.session.commit()
        # Envia o e-mail de notificação de alteração de senha
        enviar_email_alteracao_senha(current_user)
        flash('Sua senha foi atualizada com sucesso!', 'alert-success')
        return redirect(url_for('perfil'))
    return render_template('alterar_senha.html', form=form)


# @app.route('/excluir_conta', methods=['GET', 'POST'])
# @login_required
# def excluir_conta():
#     form = DeleteAccountForm()
#     if form.validate_on_submit():
#         user = Usuario.query.get(current_user.id)
#         database.session.delete(user)
#         database.session.commit()
#         logout_user()
#         flash('Sua conta e todo o seu conteúdo foram excluídos.', 'alert-success')
#         return redirect(url_for('home'))
#     return render_template('excluir_conta.html', form=form)

# @app.route('/excluir_conta',  methods=['GET', 'POST'])
# @login_required
# def excluir_conta():
#     # Usamos o formulário com senha e checkbox de confirmação
#     delete_account_form = DeleteAccountForm()

#     if delete_account_form.validate_on_submit():
#         # Verificar se a senha fornecida está correta
#         if not bcrypt.check_password_hash(current_user.senha, delete_account_form.senha.data):
#             flash('Senha incorreta. Tente novamente.', 'alert-danger')
#             return redirect(url_for('excluir_conta'))
        
#         # Verificar se o checkbox foi marcado
#         if not delete_account_form.confirmacao.data:
#             flash('Você deve marcar a caixa de confirmação para excluir sua conta.', 'alert-danger')
#             return redirect(url_for('excluir_conta'))
        
#         # Se tudo estiver correto, proceder com a exclusão
#         usuario = Usuario.query.get(current_user.id)

#         # Enviar o e-mail de notificação de exclusão de conta
#         enviar_email_exclusao_conta(usuario)
        
#         # Excluir o usuário do banco de dados
#         database.session.delete(usuario)
#         database.session.commit()
        
#         # Fazer logout após excluir a conta
#         logout_user()
        
#         flash('Sua conta e todo o seu conteúdo foram excluídos.', 'alert-success')
#         return redirect(url_for('home'))  # Redirecionar para a página inicial
#     else:
#         # Se a requisição não for válida, mostrar uma mensagem de erro
#         flash('Requisição inválida.', 'alert-danger')
#         return redirect(url_for('perfil'))

@app.route('/confirmar_exclusao', methods=['GET', 'POST'])
@login_required
def confirmar_exclusao():
    form = ConfirmarExclusaoContaForm()
    if form.validate_on_submit():
        # Verificar se a senha está correta
        if not bcrypt.check_password_hash(current_user.senha, form.senha.data):
            flash('Senha incorreta. Tente novamente.', 'alert-danger')
            return redirect(url_for('confirmar_exclusao'))
        
        # Verificar se o checkbox foi marcado
        if not form.confirmacao.data:
            flash('Você deve marcar a caixa de confirmação para excluir sua conta.', 'alert-danger')
            return redirect(url_for('confirmar_exclusao'))
        
        # Excluir a conta
        usuario = current_user
        enviar_email_exclusao_conta(usuario)
        database.session.delete(usuario)
        database.session.commit()
        
        # Fazer logout
        logout_user()
        
        flash('Sua conta foi excluída com sucesso.', 'alert-success')
        return redirect(url_for('home'))

    return render_template('confirmar_exclusao.html', form=form)

@app.route('/politica_privacidade')
@login_required
def politica_privacidade():
    return render_template('politica_privacidade.html')


@app.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('configuracoes.html')
