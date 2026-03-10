import json
import os
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, session
app = Flask(__name__)
app.secret_key = "BRVX_SUPER_SECRET_2026"

COIN_NAME = "BravaX"
COIN_SYMBOL = "BRVX"
PRICE_BRL = 0.10
PRICE_USD = 0.02

PIX_NAME = "Dionathan Duarte Martins"
PIX_KEY = "51999007349"

ADMIN_PASSWORD = "BRVX123456"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)

STYLE = """
<style>
*{box-sizing:border-box;}
body{margin:0;font-family:Arial,sans-serif;background:#050816;color:#ffffff;}
.container{width:92%;max-width:1100px;margin:0 auto;padding:24px 0 50px;}
.hero{text-align:center;padding:40px 0 24px;}
.badge{display:inline-block;background:rgba(62,166,255,0.12);border:1px solid #1f4d8f;color:#7cc4ff;padding:8px 14px;border-radius:999px;font-size:14px;margin-bottom:18px;}
h1{margin:0;font-size:52px;color:#3ea6ff;}
.subtitle{font-size:21px;margin:16px auto 0;max-width:760px;color:#d8e9ff;line-height:1.5;}
.hero-actions{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:28px;}
.btn{display:inline-block;text-decoration:none;padding:14px 20px;border-radius:12px;font-weight:bold;border:1px solid #1f4d8f;transition:0.2s ease;cursor:pointer;}
.btn-primary{background:#3ea6ff;color:#04101f;}
.btn-secondary{background:#0d1328;color:#ffffff;}
.btn-success{background:#16a34a;color:#ffffff;}
.section{margin-top:38px;}
.section h2{font-size:34px;margin-bottom:18px;color:#ffffff;}
.grid{display:grid;gap:16px;}
.grid-3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr));}
.card{background:linear-gradient(180deg,#0d1328,#111b38);border:1px solid #1f4d8f;border-radius:18px;padding:22px;box-shadow:0 0 16px rgba(20,90,180,0.18);}
.card h3{margin-top:0;margin-bottom:10px;color:#59b2ff;font-size:26px;}
.card p{margin:0;color:#d5e7ff;line-height:1.6;font-size:16px;}
.token-line{margin-top:10px;color:#ffffff;font-weight:bold;}
.info-line{margin-top:8px;color:#dbeaff;line-height:1.6;}
.form-box{max-width:700px;margin:0 auto;}
label{display:block;margin-bottom:8px;color:#dbeaff;font-weight:bold;}
input{width:100%;padding:14px;border-radius:10px;border:1px solid #1f4d8f;background:#09101f;color:#ffffff;margin-bottom:16px;font-size:16px;}
.notice{background:#0d1328;border:1px solid #1f4d8f;border-radius:14px;padding:18px;color:#dbeaff;margin-top:18px;}
.status-box{background:#111b38;border:1px solid #1f4d8f;border-radius:16px;padding:20px;margin-top:20px;}
.small{color:#9fc7f3;font-size:14px;}
a.link{color:#7cc4ff;text-decoration:none;}
.table-wrap{overflow-x:auto;}
table{width:100%;border-collapse:collapse;margin-top:12px;}
th,td{padding:12px;text-align:left;border-bottom:1px solid #1f4d8f;color:#dbeaff;vertical-align:top;}
th{color:#7cc4ff;}
.actions{display:flex;gap:8px;flex-wrap:wrap;}
.status-pill{display:inline-block;padding:6px 10px;border-radius:999px;border:1px solid #1f4d8f;background:#0d1328;color:#dbeaff;font-size:13px;}
footer{margin-top:48px;padding-top:22px;border-top:1px solid #163968;color:#9fc7f3;text-align:center;font-size:14px;}
@media (max-width:700px){
  h1{font-size:40px;}
  .subtitle{font-size:18px;}
  .section h2{font-size:28px;}
}
</style>
"""

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_orders():
    return load_json(ORDERS_FILE, [])

def save_orders(orders):
    save_json(ORDERS_FILE, orders)

def load_users():
    return load_json(USERS_FILE, {})

def save_users(users):
    save_json(USERS_FILE, users)

def get_logged_user():
    email = session.get("user_email", "").strip().lower()
    users = load_users()
    if email and email in users:
        return users[email]
    return None

def require_user():
    user = get_logged_user()
    if not user:
        return None
    return user

def create_user_if_missing(email, name, wallet_address):
    users = load_users()
    email = email.strip().lower()

    if email not in users:
        users[email] = {
            "name": name,
            "email": email,
            "wallet_address": wallet_address,
            "balance_brvx": 0.0,
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        save_users(users)

    return users

HOME_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ coin_name }} Exchange</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">{{ coin_symbol }} • Exchange oficial • PIX para BRVX</div>
<h1>{{ coin_name }} Exchange</h1>
<p class="subtitle">
Compre {{ coin_symbol }} por PIX, acompanhe o valor em reais e dólar, visualize o status da moeda e gerencie saldo interno da exchange.
</p>
<div class="hero-actions">
<a class="btn btn-primary" href="{{ url_for('deposit') }}">Comprar BRVX</a>
<a class="btn btn-secondary" href="https://bravax-node.onrender.com/explorer">Explorer</a>
</div>
</header>

<section class="section">
<h2>Status da moeda</h2>
<div class="grid grid-3">
<div class="card">
<h3>Preço em BRL</h3>
<p>Valor atual configurado da moeda.</p>
<div class="token-line">1 {{ coin_symbol }} = R$ {{ price_brl }}</div>
</div>

<div class="card">
<h3>Preço em USD</h3>
<p>Referência em dólar para exibição no painel.</p>
<div class="token-line">1 {{ coin_symbol }} = US$ {{ price_usd }}</div>
</div>

<div class="card">
<h3>Taxa de saque</h3>
<p>Regra configurada no projeto.</p>
<div class="token-line">30% antes de 2 anos</div>
</div>
</div>
</section>

<footer>{{ coin_name }} ({{ coin_symbol }}) • Exchange inicial</footer>
</div>
</body>
</html>
"""

DEPOSIT_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Depositar via PIX</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">Depósito via PIX</div>
<h1>Comprar {{ coin_symbol }}</h1>
<p class="subtitle">
Faça o pagamento via PIX e depois clique em “Já paguei” para enviar seu depósito para análise.
</p>
</header>

<section class="section">
<div class="card form-box">
<h3>Pagamento</h3>
<p class="info-line"><strong>Nome:</strong> {{ pix_name }}</p>
<p class="info-line"><strong>Chave PIX:</strong> {{ pix_key }}</p>
<p class="info-line"><strong>Preço:</strong> 1 {{ coin_symbol }} = R$ {{ price_brl }}</p>
<p class="info-line"><strong>Valor mínimo:</strong> R$ 10,00</p>

<div class="notice">
Depois do pagamento, preencha os dados abaixo para enviar sua compra para confirmação.
</div>

<form method="post" action="{{ url_for('waiting') }}" style="margin-top:18px;">
<label>Seu nome</label>
<input type="text" name="name" placeholder="Digite seu nome" required>

<label>Seu e-mail</label>
<input type="email" name="email" placeholder="Digite seu e-mail" required>

<label>Valor pago em reais</label>
<input type="number" step="0.01" min="10" name="amount_brl" placeholder="Ex: 100" required>

<label>Endereço BRVX da carteira</label>
<input type="text" name="wallet_address" placeholder="Cole aqui seu endereço BRVX" required>

<button class="btn btn-primary" type="submit">Já paguei</button>
<a class="btn btn-secondary" href="{{ url_for('home') }}">Voltar</a>
</form>
</div>
</section>

<footer>{{ coin_name }} ({{ coin_symbol }}) • Compra via PIX</footer>
</div>
</body>
</html>
"""

WAITING_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aguardando confirmação</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">Pagamento enviado</div>
<h1>Aguardando confirmação</h1>
<p class="subtitle">Seu depósito foi registrado e agora está aguardando conferência.</p>
</header>

<section class="section">
<div class="card form-box">
<h3>Resumo do pedido</h3>
<p class="info-line"><strong>Pedido:</strong> #{{ order_id }}</p>
<p class="info-line"><strong>Nome:</strong> {{ name }}</p>
<p class="info-line"><strong>E-mail:</strong> {{ email }}</p>
<p class="info-line"><strong>Valor pago:</strong> R$ {{ amount_brl }}</p>
<p class="info-line"><strong>BRVX estimado:</strong> {{ brvx_amount }} {{ coin_symbol }}</p>
<p class="info-line"><strong>Carteira:</strong> {{ wallet_address }}</p>

<div class="status-box">
<p><strong>Status:</strong> aguardando confirmação</p>
<p class="small">
Assim que o pagamento for confirmado no painel administrativo,
as moedas serão creditadas no saldo interno do usuário.
</p>
</div>

<div class="hero-actions">
<a class="btn btn-secondary" href="{{ url_for('home') }}">Voltar ao início</a>
<a class="btn btn-primary" href="{{ url_for('deposit') }}">Novo depósito</a>
</div>
</div>
</section>

<footer>{{ coin_name }} ({{ coin_symbol }}) • Status do depósito</footer>
</div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cadastro</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">Cadastro de usuário</div>
<h1>Criar conta</h1>
<p class="subtitle">Crie sua conta para acessar sua wallet BRVX.</p>
</header>

<section class="section">
<div class="card form-box">
{% if error %}
<div class="notice">{{ error }}</div>
{% endif %}
<form method="post" action="/register">
<label>Nome</label>
<input type="text" name="name" placeholder="Seu nome completo" required>

<label>Email</label>
<input type="email" name="email" placeholder="Seu email" required>

<label>Senha</label>
<input type="password" name="password" placeholder="Crie uma senha" required>

<label>Carteira BRVX</label>
<input type="text" name="wallet_address" placeholder="Seu endereço BRVX" required>

<button class="btn btn-primary" type="submit">Criar conta</button>
<a class="btn btn-secondary" href="/">Voltar</a>
</form>
</div>
</section>

<footer>Cadastro BRVX</footer>
</div>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">Área do usuário</div>
<h1>Login</h1>
<p class="subtitle">Entre na sua conta para acessar sua wallet.</p>
</header>

<section class="section">
<div class="card form-box">
{% if error %}
<div class="notice">{{ error }}</div>
{% endif %}
<form method="post" action="/login">
<label>Email</label>
<input type="email" name="email" placeholder="Seu email" required>

<label>Senha</label>
<input type="password" name="password" placeholder="Sua senha" required>

<button class="btn btn-primary" type="submit">Entrar</button>
<a class="btn btn-secondary" href="/">Voltar</a>
</form>
</div>
</section>

<footer>Login BRVX</footer>
</div>
</body>
</html>
"""
ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login Admin</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">Área protegida</div>
<h1>Login Admin</h1>
<p class="subtitle">Digite a senha administrativa para acessar o painel.</p>
</header>

<section class="section">
<div class="card form-box">
{% if error %}
<div class="notice">{{ error }}</div>
{% endif %}

<form method="post" action="/admin-login">
<label>Senha do admin</label>
<input type="password" name="password" placeholder="Digite a senha" required>

<button class="btn btn-primary" type="submit">Entrar</button>
<a class="btn btn-secondary" href="/">Voltar</a>
</form>
</div>
</section>

<footer>BravaX Admin Protegido</footer>
</div>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Admin BRVX</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">Painel administrativo</div>
<h1>Admin BRVX</h1>
<p class="subtitle">
Área inicial para conferência manual dos pagamentos PIX.
</p>
</header>

<section class="section">
<div class="grid grid-3">
<div class="card">
<h3>Status</h3>
<p>Painel admin ativo.</p>
<div class="token-line">Confirmação manual</div>
</div>

<div class="card">
<h3>Preço atual</h3>
<p>Configuração inicial da moeda.</p>
<div class="token-line">R$ {{ price_brl }} / US$ {{ price_usd }}</div>
</div>

<div class="card">
<h3>Taxa de saque</h3>
<p>Regra configurada no projeto.</p>
<div class="token-line">30% antes de 2 anos</div>
</div>
</div>
</section>

<section class="section">
<h2>Pedidos</h2>
<div class="card table-wrap">
{% if orders %}
<table>
<thead>
<tr>
<th>ID</th>
<th>Nome</th>
<th>Email</th>
<th>Valor</th>
<th>BRVX</th>
<th>Status</th>
<th>Ações</th>
</tr>
</thead>
<tbody>
{% for order in orders %}
<tr>
<td>#{{ order["id"] }}</td>
<td>{{ order["name"] }}</td>
<td>{{ order["email"] }}</td>
<td>R$ {{ order["amount_brl"] }}</td>
<td>{{ order["brvx_amount"] }} {{ coin_symbol }}</td>
<td><span class="status-pill">{{ order["status"] }}</span></td>
<td>
<div class="actions">
{% if order["status"] == "aguardando confirmação" %}
<a class="btn btn-success" href="/admin/confirm/{{ order['id'] }}?key={{ admin_key }}">Confirmar</a>
{% endif %}
</div>
</td>
</tr>
<tr>
<td colspan="7">
<div class="small">
Carteira: {{ order["wallet_address"] }}<br>
Criado em: {{ order["created_at"] }}
</div>
</td>
</tr>
{% endfor %}
</tbody>
</table>
{% else %}
<p>Nenhum pedido registrado ainda.</p>
{% endif %}
</div>
</section>

<section class="section">
<h2>Usuários</h2>
<div class="card table-wrap">
{% if users %}
<table>
<thead>
<tr>
<th>Nome</th>
<th>Email</th>
<th>Carteira</th>
<th>Saldo</th>
</tr>
</thead>
<tbody>
{% for email, user in users.items() %}
<tr>
<td>{{ user["name"] }}</td>
<td>{{ user["email"] }}</td>
<td>{{ user["wallet_address"] }}</td>
<td>{{ "%.2f"|format(user["balance_brvx"]) }} {{ coin_symbol }}</td>
</tr>
{% endfor %}
</tbody>
</table>
{% else %}
<p>Nenhum usuário registrado ainda.</p>
{% endif %}
</div>
</section>

<footer>{{ coin_name }} ({{ coin_symbol }}) • Admin inicial</footer>
</div>
</body>
</html>
"""

CONFIRMED_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pedido confirmado</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">Pedido confirmado</div>
<h1>Pagamento confirmado</h1>
<p class="subtitle">O saldo BRVX interno do usuário foi creditado com sucesso.</p>
</header>

<section class="section">
<div class="card form-box">
<h3>Resumo</h3>
<p class="info-line"><strong>Pedido:</strong> #{{ order["id"] }}</p>
<p class="info-line"><strong>Usuário:</strong> {{ order["name"] }}</p>
<p class="info-line"><strong>E-mail:</strong> {{ order["email"] }}</p>
<p class="info-line"><strong>Saldo creditado:</strong> {{ order["brvx_amount"] }} {{ coin_symbol }}</p>
<p class="info-line"><strong>Status:</strong> {{ order["status"] }}</p>

<div class="hero-actions">
<a class="btn btn-primary" href="/admin?key={{ admin_key }}">Voltar ao admin</a>
<a class="btn btn-secondary" href="{{ url_for('home') }}">Início</a>
</div>
</div>
</section>

<footer>{{ coin_name }} ({{ coin_symbol }}) • Confirmação concluída</footer>
</div>
</body>
</html>
"""

WALLET_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wallet BRVX</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="badge">Carteira BRVX</div>
<h1>Wallet</h1>
<p class="subtitle">
Painel da carteira do usuário na exchange.
</p>
</header>

<section class="section">
<div class="grid grid-3">
<div class="card">
<h3>Saldo</h3>
<p>Saldo total na exchange.</p>
<div class="token-line">{{ balance }} BRVX</div>
</div>

<div class="card">
<h3>Valor em BRL</h3>
<p>Estimativa atual.</p>
<div class="token-line">R$ {{ value_brl }}</div>
</div>

<div class="card">
<h3>Valor em USD</h3>
<p>Estimativa em dólar.</p>
<div class="token-line">$ {{ value_usd }}</div>
</div>
</div>
</section>

<section class="section">
<div class="card">
<h3>Informações da conta</h3>
<p class="info-line"><strong>Nome:</strong> {{ name }}</p>
<p class="info-line"><strong>Email:</strong> {{ email }}</p>
<p class="info-line"><strong>Carteira BRVX:</strong> {{ wallet }}</p>
<p class="info-line"><strong>Criado em:</strong> {{ created }}</p>
</div>
</section>

<section class="section">
<div class="grid grid-3">
<div class="card">
<h3>Transferir</h3>
<p>Enviar BRVX para outro usuário.</p>
</div>

<div class="card">
<h3>Sacar</h3>
<p>Retirar BRVX para carteira externa.</p>
</div>

<div class="card">
<h3>Histórico</h3>
<p>Visualizar transações.</p>
</div>
</div>
</section>

<footer>
BravaX Wallet
</footer>
</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(
        HOME_HTML,
        coin_name=COIN_NAME,
        coin_symbol=COIN_SYMBOL,
        price_brl=f"{PRICE_BRL:.2f}",
        price_usd=f"{PRICE_USD:.2f}"
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        wallet_address = request.form.get("wallet_address", "").strip()

        users = load_users()

        if email in users:
            error = "Este email já está cadastrado."
        elif not name or not email or not password or not wallet_address:
            error = "Preencha todos os campos."
        else:
            users[email] = {
                "name": name,
                "email": email,
                "password": password,
                "wallet_address": wallet_address,
                "balance_brvx": 0.0,
                "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            save_users(users)
            session["user_email"] = email
            return redirect(url_for("wallet_user"))

    return render_template_string(REGISTER_HTML, error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        users = load_users()

        if email not in users:
            error = "Usuário não encontrado."
        elif users[email].get("password", "") != password:
            error = "Senha inválida."
        else:
            session["user_email"] = email
            return redirect(url_for("wallet_user"))

    return render_template_string(LOGIN_HTML, error=error)


@app.route("/logout")
def logout_user():
    session.pop("user_email", None)
    return redirect(url_for("home"))

@app.route("/status")
def status():
    return {"status": "running"}

@app.route("/deposit")
def deposit():
    return render_template_string(
        DEPOSIT_HTML,
        coin_name=COIN_NAME,
        coin_symbol=COIN_SYMBOL,
        price_brl=f"{PRICE_BRL:.2f}",
        pix_name=PIX_NAME,
        pix_key=PIX_KEY
    )

@app.route("/waiting", methods=["POST"])
def waiting():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    wallet_address = request.form.get("wallet_address", "").strip()

    try:
        amount_brl = float(request.form.get("amount_brl", "0"))
    except ValueError:
        amount_brl = 0.0

    brvx_amount = 0.0
    if amount_brl > 0:
        brvx_amount = amount_brl / PRICE_BRL

    orders = load_orders()
    order_id = len(orders) + 1

    create_user_if_missing(email, name, wallet_address)

    order = {
        "id": order_id,
        "name": name,
        "email": email,
        "amount_brl": round(amount_brl, 2),
        "brvx_amount": round(brvx_amount, 2),
        "wallet_address": wallet_address,
        "status": "aguardando confirmação",
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    orders.append(order)
    save_orders(orders)

    return render_template_string(
        WAITING_HTML,
        coin_name=COIN_NAME,
        coin_symbol=COIN_SYMBOL,
        order_id=order_id,
        name=name,
        email=email,
        amount_brl=f"{amount_brl:.2f}",
        wallet_address=wallet_address,
        brvx_amount=f"{brvx_amount:.2f}"
    )

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    error = ""

    if request.method == "POST":
        password = request.form.get("password", "").strip()

        if password == ADMIN_PASSWORD:
            return redirect(url_for("admin", key=ADMIN_PASSWORD))
        else:
            error = "Senha inválida"

    return render_template_string(ADMIN_LOGIN_HTML, error=error)

@app.route("/admin")
def admin():
    key = request.args.get("key", "")

    if key != ADMIN_PASSWORD:
        return redirect(url_for("admin_login"))

    return render_template_string(
        ADMIN_HTML,
        coin_name=COIN_NAME,
        coin_symbol=COIN_SYMBOL,
        price_brl=f"{PRICE_BRL:.2f}",
        price_usd=f"{PRICE_USD:.2f}",
        orders=load_orders(),
        users=load_users(),
        admin_key=ADMIN_PASSWORD
    )

@app.route("/admin/confirm/<int:order_id>")
def confirm_order(order_id):
    key = request.args.get("key", "")
    if key != ADMIN_PASSWORD:
        return redirect(url_for("admin_login"))

    orders = load_orders()
    users = load_users()

    target = None
    for order in orders:
        if order["id"] == order_id:
            target = order
            break

    if not target:
        return redirect(url_for("admin", key=ADMIN_PASSWORD))

    if target["status"] != "confirmado":
        target["status"] = "confirmado"

        email = target["email"]
        if email in users:
            users[email]["balance_brvx"] = round(
                float(users[email].get("balance_brvx", 0.0)) + float(target["brvx_amount"]),
                2
            )
            save_users(users)

        save_orders(orders)

    return render_template_string(
        CONFIRMED_HTML,
        coin_name=COIN_NAME,
        coin_symbol=COIN_SYMBOL,
        order=target,
        admin_key=ADMIN_PASSWORD
    )

@app.route("/wallet")
def wallet_user():
    user = require_user()
    if not user:
        return redirect(url_for("login"))

    balance = float(user.get("balance_brvx", 0))
    value_brl = round(balance * PRICE_BRL, 2)
    value_usd = round(balance * PRICE_USD, 2)

    return render_template_string(
        WALLET_HTML,
        name=user["name"],
        email=user["email"],
        wallet=user["wallet_address"],
        created=user["created_at"],
        balance=f"{balance:.2f}",
        value_brl=f"{value_brl:.2f}",
        value_usd=f"{value_usd:.2f}"
    )

@app.route("/wallet/<email>")
def wallet(email):
    users = load_users()
    email = email.strip().lower()

    if email not in users:
        return "Usuário não encontrado"

    user = users[email]
    balance = float(user.get("balance_brvx", 0))
    value_brl = round(balance * PRICE_BRL, 2)
    value_usd = round(balance * PRICE_USD, 2)

    return render_template_string(
        WALLET_HTML,
        name=user["name"],
        email=user["email"],
        wallet=user["wallet_address"],
        created=user["created_at"],
        balance=f"{balance:.2f}",
        value_brl=f"{value_brl:.2f}",
        value_usd=f"{value_usd:.2f}"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
