# Laboratorio de autenticación — Burp Suite

Aplicación **solo educativa** para evaluar el comportamiento de un inicio de sesión propio mediante un diccionario de cinco contraseñas. No admite usuarios reales ni almacena datos personales.

## Archivos
- `app.py`: rutas `/`, `/login`, `/panel`, `/logout`, `/health`, autenticación y bloqueo opcional.
- `templates/login.html`: formulario.
- `templates/panel.html`: acceso exitoso.
- `diccionario_prueba.txt`: cinco contraseñas de **laboratorio**, incluida la de demostración.
- `requirements.txt`: dependencias del servidor.

## Ejecutar en Kali (opcional antes del despliegue)

```bash
sudo apt update
sudo apt install -y python3 python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visita `http://127.0.0.1:5000`.

Credenciales de prueba local: usuario `alumno`, contraseña `Laboratorio2026!`.

## Desplegar en Render
1. Crea un repositorio **privado** en GitHub (o público si únicamente contiene estos archivos educativos). Sube los archivos conservando la carpeta `templates`.
2. En Render, **New > Web Service**, conecta el repositorio.
3. Configuración:
   - Language: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --workers 1 app:app`
   - Instance Type: Free (si está disponible para tu cuenta)
4. En **Environment** añade las variables:
   - `LAB_USERNAME` = `alumno`
   - `LAB_PASSWORD` = `Laboratorio2026!` (solo cuenta ficticia)
   - `SECRET_KEY` = un valor largo y aleatorio (generado mediante `python3 -c 'import secrets; print(secrets.token_hex(32))'`)
   - `ENABLE_RATE_LIMIT` = `false`
   - `RENDER` = `true`
5. Crea el servicio y visita la dirección HTTPS asignada por Render.
6. **No publiques datos ni contraseñas reales**. El repositorio contiene un diccionario educativo y la cuenta solo abre una pantalla ficticia.

## Captura con Burp
1. `Proxy > Intercept > Open browser`.
2. Visita tu URL de Render y envía el formulario con un valor incorrecto. En `Proxy > HTTP history`, busca `POST /login`.
3. Clic derecho > `Send to Intruder`. Marca solo el valor de `password` en el cuerpo (`password=§ejemplo§`).
4. Selecciona `Sniper` y payloads `Simple list`; carga `diccionario_prueba.txt`.
5. Ejecuta **una única serie corta de cinco pruebas**. Una respuesta `302` puede indicar éxito; una respuesta `401`, credenciales erróneas. Confirma verificando la cabecera `Location: /panel`.
6. Documenta el estado de Intruder y sus resultados.
7. En Render cambia `ENABLE_RATE_LIMIT` a `true`, **guarda y vuelve a desplegar**. Repite la prueba, dejando **la contraseña correcta para la quinta petición**; después de tres fallos se devolverá `429` (bloqueo temporal de 5 minutos).

IMPORTANTE: Los contadores están en memoria y se reinician cuando Render duerme, reinicia o redespliega el servicio. Este es un ejemplo de protección básica, no una solución para sistemas de producción. Para sistemas reales conviene un almacén compartido y controles adicionales (MFA, registro de eventos, supervisión, etc.).

## Resultados esperados
- Modo demostración: cuatro respuestas `401`, una `302`.
- Modo protección: primeras tres respuestas `401`, restantes `429`.
- Si quieres repetir sin esperar cinco minutos, redepliega el servicio de laboratorio para reiniciar la memoria.

## Cierre
Elimina el servicio Render al terminar la entrega. No reutilices este formulario para datos reales, ni ensayes contra sitios que no controles.
