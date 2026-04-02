# 🛡️ Guía Maestra de Ofuscación Híbrida

Esta guía detalla el flujo de trabajo profesional para proteger la **Chromium Auditor Suite** contra ingeniería inversa, análisis estático y detecciones heurísticas de antivirus (AV/EDR).

---

## 🏗️ La Arquitectura de Tres Capas

Para lograr un binario "indescifrable", aplicamos tres niveles de protección progresivos:

### 🛡️ Nivel 1: Ofuscación de Datos (Base64)
*   **Objetivo**: Evitar que tokens de bots (`Telegram`) o URLs de webhooks (`Discord`) aparezcan como texto plano al analizar el binario con herramientas de "Strings".
*   **Acción**: Codificar tus credenciales en Base64 antes de pegarlas en el código.

### 🛡️ Nivel 2: Ofuscación de Fuente (`ofuscator.py`)
*   **Objetivo**: Convertir tu lógica de Python en múltiples capas de cifrado metamórfico que se ejecutan dinámicamente en memoria mediante `exec()`.
*   **Acción**: Ejecutar el ofuscador personalizado sobre el código fuente original.

### 🛡️ Nivel 3: Blindaje de Bytecode (`PyArmor`)
*   **Objetivo**: Cifrar el motor de Python (bytecode) y asegurar el flujo de ejecución (`Runtime Protection`). Esto impide que incluso si logran descompilar el archivo, puedan leer las funciones de descifrado internas.
*   **Acción**: Compilar el resultado final usando el empaquetador de PyArmor.

---

## 🚀 Flujo de Trabajo Paso a Paso

### Paso 1: Configurar Credenciales
Accede a `main.py` y rellena tus campos en Base64:
```python
HARDCODED_TG_TOKEN = "MTIzNDU2Nzg5MDpBQkMtREVGM..." # Tu Base64
```

### Paso 2: Generar Capas Metamórficas
Usa tu script `ofuscator.py` para crear la primera capa de armadura:
```bash
python ofuscator.py main.py
```
*Esto generará un nuevo `main.py` (sobrescrito o respaldado) con lógica de descifrado multicapa.*

### Paso 3: Blindaje Final y Compilación (.exe)
Utiliza PyArmor para cifrar el bytecode y empaquetar todo un único ejecutable portable:

```bash
# Instalación de herramientas
pip install pyarmor pyinstaller

# Empaquetado Híbrido Profesional
pyarmor pack -e " --onefile --noconsole --name 'AuditSuite_v1' " main.py
```

---

## 📊 Comparativa de Protección

| Método | Protección de Datos | Protección de Lógica | Resistencia a Descompiladores |
| :--- | :--- | :--- | :--- |
| **PyInstaller Estándar** | ❌ Baja | ❌ Nula | ❌ Muy Baja |
| **`ofuscator.py` Solo** | ✅ Media | ✅ Alta | ⚠️ Media |
| **Ofuscación Híbrida** | ⭐ Máxima | ⭐ Máxima | ⭐ Máxima |

---

## ⚖️ Recomendación de Pentesting

*   **Evadir Heurística**: Si el binario es detectado como malicioso, prueba a compilar **sin** la opción `--noconsole` para que parezca un script administrativo estándar de Windows.
*   **Bots de un solo uso**: Nunca uses tus tokens principales de Telegram. Crea un bot exclusivo para cada auditoría y elimínalo al finalizar para prevenir la trazabilidad.

---
<div align="center">
Protección Avanzada para Operaciones de Seguridad Profesional
</div>
