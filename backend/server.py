import json
import os
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, session, send_from_directory

app = Flask(__name__)
app.secret_key = "BRVX_SUPER_SECRET_2026"

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), "static"),
        "file_00000000f4f071f595c0c1874257c729.png",
        mimetype="image/png"
    )

COIN_NAME = "BravaX"
COIN_SYMBOL = "BRVX"
PRICE_BRL = 0.10
PRICE_USD = 0.02

PIX_NAME = "Dionathan Duarte Martins"
PIX_KEY = "51999007349"

ADMIN_PASSWORD = "BRVX123456"

FAVICON_PATH = "/static/file_00000000f4f071f595c0c1874257c729.png"

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
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
@app.route("/")
def home():
    return "BravaX Exchange Online"

@app.route("/status")
def status():
    return {"status": "online"}

@app.route("/register", methods=["GET","POST"])
def register():
    return "register page"

@app.route("/login", methods=["GET","POST"])
def login():
    return "login page"

@app.route("/wallet")
def wallet_user():
    return "wallet"

@app.route("/deposit")
def deposit():
    return "deposit"

@app.route("/admin")
def admin():
    return "admin panel"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
