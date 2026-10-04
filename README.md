# Comunidade Impressionadora

Aplicação web em Flask para compartilhar publicações, conhecer outros alunos e trocar experiências. Inclui cadastro, confirmação de e-mail, login, perfis, posts, contato e redefinição de senha.

## Rodar localmente

Requer Python 3.10 ou superior.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
python main.py
```

Acesse http://127.0.0.1:5000. A configuração local usa `instance/comunidade.db` (SQLite). Para enviar e-mails, preencha as variáveis SMTP no `.env`.

Antes de iniciar pela primeira vez, crie o esquema de um banco novo com `flask --app main db upgrade`. Se estiver usando o SQLite antigo com contas e publicações, faça a cópia de segurança e siga o procedimento de migração abaixo antes de iniciar.

Se o Controle de Aplicativos do Windows bloquear `_util_cy` do SQLAlchemy, reinstale o SQLAlchemy sem a extensão opcional:

```powershell
$env:DISABLE_SQLALCHEMY_CEXT = "1"
python -m pip uninstall -y SQLAlchemy
python -m pip install --no-binary=SQLAlchemy SQLAlchemy
```

Se o banco SQLite existente ainda não estiver sob controle de migrações, faça uma cópia de segurança e marque a estrutura antiga antes de aplicar a migração de compatibilidade:

```powershell
Copy-Item instance\comunidade.db instance\comunidade.backup.db
$env:DATABASE_URL = "sqlite:///comunidade.db"
flask --app main db stamp aaf8ad2bb972
flask --app main db upgrade
```

Em um banco vazio, rode apenas `flask --app main db upgrade`. Se já houver tabelas e dados no SQLite antigo, rode primeiro o procedimento de cópia e migração acima; o `stamp` evita que o Alembic tente recriar as tabelas existentes.

## Publicação

Use um serviço que execute aplicações Python/WSGI. O `Procfile` inicia o Gunicorn e usa a porta informada pelo serviço. Configure no painel do provedor:

- `SECRET_KEY`: valor aleatório forte, exclusivo da produção.
- `DATABASE_URL`: URL de um banco persistente. PostgreSQL e MySQL são suportados pelos drivers incluídos.
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` e `MAIL_DEFAULT_SENDER`: credenciais de um provedor SMTP para confirmação de conta e redefinição de senha.
- `MAIL_USE_TLS=true` (ou `MAIL_USE_SSL=true`, conforme o provedor).

Rode `flask --app main db upgrade` como etapa de deploy antes de receber tráfego. Configure também domínio, HTTPS e backups do banco no provedor. SQLite serve para desenvolvimento local; não use um disco efêmero como armazenamento de produção.

Para gerar uma chave de produção:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Nunca publique o arquivo `.env` nem credenciais. As senhas SMTP e do banco que já estiveram no código devem ser trocadas antes do deploy; removê-las dos arquivos atuais não apaga cópias do histórico Git.
