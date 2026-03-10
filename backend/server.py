import json
import os
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, session, send_from_directory

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
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

LOGO_FILE = "file_00000000f4f071f595c0c1874257c729.png"

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

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(STATIC_DIR, LOGO_FILE, mimetype="image/png")

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
.logo-top{display:flex;justify-content:center;margin-bottom:14px;}
.logo-top img{width:84px;height:84px;object-fit:cover;border-radius:50%;border:2px solid #1f4d8f;box-shadow:0 0 16px rgba(62,166,255,0.25);}
footer{margin-top:48px;padding-top:22px;border-top:1px solid #163968;color:#9fc7f3;text-align:center;font-size:14px;}
</style>
"""

HEAD = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" type="image/png" href="/favicon.ico">
"""

HOME_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
""" + HEAD + """
<title>BravaX Exchange</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="logo-top">
  <img src="/static/file_00000000f4f071f595c0c1874257c729.png" alt="Logo BRVX">
</div>
<div class="badge">{{ coin_symbol }} • Exchange oficial</div>
<h1>{{ coin_name }} Exchange</h1>
<p class="subtitle">
Compre {{ coin_symbol }} por PIX e acompanhe o valor da moeda em reais e dólar.
</p>

<div class="hero-actions">
<a class="btn btn-primary" href="/deposit">Comprar BRVX</a>
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
<p>Referência em dólar para exibição.</p>
<div class="token-line">1 {{ coin_symbol }} = US$ {{ price_usd }}</div>
</div>

<div class="card">
<h3>Compra</h3>
<p>Pagamento inicial via PIX com confirmação manual.</p>
<div class="token-line">Ativo</div>
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
""" + HEAD + """
<title>Comprar BRVX</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="logo-top">
  <img src="/static/file_00000000f4f071f595c0c1874257c729.png" alt="Logo BRVX">
</div>
<div class="badge">Depósito via PIX</div>
<h1>Comprar {{ coin_symbol }}</h1>
<p class="subtitle">
Faça o pagamento via PIX e depois clique em “Já paguei” para registrar seu pedido.
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
Depois do pagamento, preencha os dados abaixo para registrar sua compra.
</div>

<form method="post" action="/waiting" style="margin-top:18px;">
<label>Seu nome</label>
<input name="name" placeholder="Seu nome" required>

<label>Seu email</label>
<input name="email" type="email" placeholder="Seu email" required>

<label>Carteira BRVX</label>
<input name="wallet_address" placeholder="Seu endereço BRVX" required>

<label>Valor pago em reais</label>
<input name="amount_brl" type="number" step="0.01" min="10" placeholder="Ex: 100" required>

<button class="btn btn-primary" type="submit">Já paguei</button>
<a class="btn btn-secondary" href="/">Voltar</a>
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
""" + HEAD + """
<title>Aguardando confirmação</title>
""" + STYLE + """
</head>
<body>
<div class="container">
<header class="hero">
<div class="logo-top">
  <img src="/static/file_00000000f4f071f595c0c1874257c729.png" alt="Logo BRVX">
</div>
<div class="badge">Pedido registrado</div>
<h1>Aguardando confirmação</h1>
<p class="subtitle">
Seu pagamento foi registrado e está aguardando conferência.
</p>
</header>

<section class="section">
<div class="card form-box">
<p class="info-line"><strong>Pedido:</strong> #{{ order_id }}</p>
<p class="info-line"><strong>Nome:</strong> {{ name }}</p>
<p class="info-line"><strong>Email:</strong> {{ email }}</p>
<p class="info-line"><strong>Valor pago:</strong> R$ {{ amount_brl }}</p>
<p class="info-line"><strong>BRVX estimado:</strong> {{ brvx_amount }} {{ coin_symbol }}</p>
<p class="info-line"><strong>Carteira:</strong> {{ wallet_address }}</p>

<div class="status-box">
<p><strong>Status:</strong> aguardando confirmação</p>
<p class="small">Assim que o admin confirmar, o saldo poderá ser liberado.</p>
</div>

<div class="hero-actions">
<a class="btn btn-secondary" href="/">Início</a>
<a class="btn btn-primary" href="/deposit">Novo pedido</a>
</div>
</div>
</section>

<footer>{{ coin_name }} ({{ coin_symbol }}) • Status do pedido</footer>
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

@app.route("/status")
def status():
    return {"status": "running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
