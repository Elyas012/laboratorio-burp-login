"""Aplicación demostrativa de autenticación para una práctica AUTORIZADA con Burp.
Sin usuarios reales ni información sensible. No usar como plantilla de producción.
"""
import os
import time
from collections import defaultdict, deque
from threading import Lock

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'solo-desarrollo-cambiar-en-render'),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('RENDER', '').lower() == 'true',
)

USERNAME = os.environ.get('LAB_USERNAME', 'alumno')
PASSWORD_HASH = generate_password_hash(os.environ.get('LAB_PASSWORD', 'Laboratorio2026!'))
PROTECTION_ENABLED = os.environ.get('ENABLE_RATE_LIMIT', 'false').lower() == 'true'
WINDOW_SECONDS = 300
MAX_FAILURES = 3
failed_attempts = defaultdict(deque)
failed_lock = Lock()


def current_key():
    # Para esta demostración se usa la IP que Flask conoce; no se confía en
    # encabezados X-Forwarded-For suministrados por clientes.
    return (request.remote_addr or 'unknown', request.form.get('username', '').strip().lower())


def current_failures(key, now):
    with failed_lock:
        items = failed_attempts[key]
        while items and now - items[0] >= WINDOW_SECONDS:
            items.popleft()
        return len(items)


def add_failure(key, now):
    with failed_lock:
        failed_attempts[key].append(now)


@app.get('/')
def index():
    if session.get('authenticated'):
        return redirect(url_for('panel'))
    return render_template('login.html', error=None, protected=PROTECTION_ENABLED)


@app.post('/login')
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    key = current_key()
    now = time.monotonic()

    if PROTECTION_ENABLED and current_failures(key, now) >= MAX_FAILURES:
        return render_template('login.html', error='Demasiados intentos. Intenta de nuevo más tarde.', protected=True), 429

    # Comparamos ambas credenciales; para un laboratorio no se almacenan cuentas reales.
    if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
        session.clear()
        session['authenticated'] = True
        session['username'] = USERNAME
        return redirect(url_for('panel'), code=302)

    if PROTECTION_ENABLED:
        add_failure(key, now)
    return render_template('login.html', error='Usuario o contraseña incorrectos.', protected=PROTECTION_ENABLED), 401


@app.get('/panel')
def panel():
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template('panel.html', username=session['username'], protected=PROTECTION_ENABLED)


@app.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.get('/health')
def health():
    return {'status': 'ok', 'mode': 'protected' if PROTECTION_ENABLED else 'lab'}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', '5000')), debug=False)
