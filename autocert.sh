#!/bin/bash
# =============================================================================
# autocert.sh — Firmado de código autofirmado para ejecutables Windows (.exe)
# Requiere: openssl, osslsigncode (Linux/WSL)
# Uso:      bash autocert.sh <ruta_al_exe> [contraseña_pfx]
# =============================================================================

EXE="$1"
CERT_PASS="${2:-$(openssl rand -hex 16)}"  # Contraseña aleatoria si no se provee
CERT_PFX="certificado_tmp.pfx"

# ── Verificar argumento ──────────────────────────────────────────────────────
if [ -z "$EXE" ] || [ ! -f "$EXE" ]; then
    echo "❌ Uso: bash autocert.sh <ruta_al_exe> [contraseña_pfx]"
    echo "   Ejemplo: bash autocert.sh dist/ChromiumAuditor.exe"
    exit 1
fi

# ── Instalar osslsigncode si no está disponible ──────────────────────────────
if ! command -v osslsigncode &> /dev/null; then
    echo "📦 osslsigncode no encontrado. Instalando..."
    if command -v apt &> /dev/null; then
        sudo apt update -qq && sudo apt install osslsigncode -y -qq
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy osslsigncode --noconfirm
    elif command -v brew &> /dev/null; then
        brew install osslsigncode
    else
        echo "❌ No se pudo instalar osslsigncode. Instálalo manualmente."
        exit 1
    fi
fi

# ── Generar certificado autofirmado (efímero) ────────────────────────────────
echo "🔐 Generando certificado autofirmado..."

# Metadatos verosímiles para reducir sospecha en análisis PE
openssl req -new -x509 -days 3650 -nodes \
    -out cert_tmp.pem -keyout key_tmp.pem \
    -subj "/C=US/ST=California/L=San Jose/O=Network Diagnostics Inc/OU=IT/CN=netdiag-tools.com" \
    -addext "subjectAltName=DNS:netdiag-tools.com" \
    2>/dev/null

openssl pkcs12 -export \
    -out "$CERT_PFX" \
    -inkey key_tmp.pem \
    -in cert_tmp.pem \
    -passout "pass:$CERT_PASS" \
    2>/dev/null

echo "✅ Certificado generado."

# ── Firmar el ejecutable ─────────────────────────────────────────────────────
echo "✍️  Firmando: $EXE"

osslsigncode sign \
    -pkcs12 "$CERT_PFX" \
    -pass "$CERT_PASS" \
    -n "Network Diagnostics Tool" \
    -i "https://netdiag-tools.com" \
    -ts "http://timestamp.digicert.com" \
    -in  "$EXE" \
    -out "${EXE}.signed.exe"

if [ $? -eq 0 ]; then
    mv "${EXE}.signed.exe" "$EXE"
    echo "✅ Firma aplicada correctamente: $EXE"
    echo "   Timestamp: DigiCert TSA (válido indefinidamente)"
else
    echo "❌ Error al firmar. Revisa que osslsigncode esté correctamente instalado."
    rm -f "${EXE}.signed.exe"
fi

# ── Limpieza de artefactos criptográficos ────────────────────────────────────
rm -f cert_tmp.pem key_tmp.pem "$CERT_PFX"
echo "🧹 Artefactos criptográficos eliminados."
