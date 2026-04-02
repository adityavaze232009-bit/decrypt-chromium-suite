# Análisis de Pentesting: Decrypt Chrome Passwords

> [!NOTE]
> [English Version](REFACTOR.en.md) | **Versión en Español**

> [!NOTE]
> **Documento histórico** — Este archivo describe el plan de análisis inicial del proyecto. Todas las mejoras aquí descritas han sido implementadas en `main.py`. El nombre de archivo referenciado (`decrypt_chromium_passwd.py`) fue renombrado a `main.py` durante la refactorización.

Este repositorio contiene una herramienta diseñada para extraer y descifrar las credenciales guardadas en Google Chrome en entornos Windows. A continuación, se presenta un desglose de su funcionamiento técnico, junto con una propuesta de mejoras, optimizaciones y automatizaciones para elevar su nivel en auditorías de seguridad profesional.

## 1. Análisis de Funcionamiento Actual

El script `decrypt_chromium_passwd.py` sigue un flujo lógico de 5 pasos críticos para comprometer la base de datos de contraseñas de Chrome (versiones 80+):

1. **Extracción de la "Master Key"**: Chrome cifra las contraseñas usando una clave AES única para cada instalación. Esta clave se guarda cifrada en el archivo `%LocalAppData%\Google\Chrome\User Data\Local State`. El script la extrae y la descifra usando la API de Windows `CryptUnprotectData` (DPAPI), lo que significa que **solo puede ejecutarse bajo la sesión del usuario dueño de los datos**.
2. **Identificación de Perfiles**: Itera sobre las carpetas `Default` y `Profile*` en el directorio de datos de usuario de Chrome para cubrir todos los perfiles configurados.
3. **Copiado de Base de Datos**: Copia el archivo `Login Data` (una base de datos SQLite) a un archivo temporal (`Loginvault.db`). Esto es crucial porque si Chrome está abierto, el archivo original está bloqueado por el proceso del navegador.
4. **Descifrado AES-GCM**: Consulta la tabla `logins`. Para cada entrada:
    * Extrae el vector de inicialización (IV).
    * Utiliza la clave maestra descifrada anteriormente para realizar el descifrado AES en modo GCM.
5. **Persistencia de Resultados**: Genera un archivo `decrypted_password.csv` con los campos: Index, URL, Username y Password.

---

## 2. Mejoras y Optimizaciones Propuestas

### A. Soporte Multi-Navegador (Nivel Crítico)

Actualmente, el script solo apunta a Chrome. Casi todos los navegadores basados en **Chromium** usan el mismo mecanismo:

* **Microsoft Edge**: `%LocalAppData%\Microsoft\Edge\User Data\`
* **Brave-Browser**: `%LocalAppData%\BraveSoftware\Brave-Browser\User Data\`
* **Opera/Opera GX**: `%AppData%\Opera Software\Opera Stable\` (o Opera GX Stable)
* **Vivaldi**: `%LocalAppData%\Vivaldi\User Data\`

> [!TIP]
> Implementar una clase base o un diccionario de rutas permitiría automatizar el escaneo de todos los navegadores instalados en una sola ejecución.

### B. Optimización del Código

* **Uso de `pathlib`**: Reemplazar `os.path` y `os.environ` por `pathlib` para una manipulación de rutas más moderna y segura.
* **Manejo de Errores Silencioso**: En una auditoría, los errores en consola pueden alertar al usuario. Implementar un sistema de logging que escriba en archivos ocultos o envíe errores a un servidor remoto.
* **Limpieza Total**: El script actual borra el archivo temporal de la DB, pero deja el CSV. Se podría implementar una opción para borrar rastro (Wipe-on-Exit).

---

## 3. Capacidades de Pentesting y Exfiltración

Para una auditoría técnica más efectiva, se pueden automatizar las siguientes funciones:

### C. Exfiltración Automatizada

En lugar de depender de un CSV local, se pueden añadir "Exfiltration Modules":

* **Webhook de Discord/Telegram**: Enviar los resultados directamente a un canal privado de monitoreo.
* **Servidor HTTP/S Personalizado**: Hacer un POST con el contenido del CSV cifrado a un C2 (Command & Control).
* **Email Exfiltration**: Enviar el reporte vía SMTP (menos recomendado por detección de AV/EDR).

### D. Modo Sigilo (Stealth)

* **Detección de Navegador Abierto**: Si Chrome está abierto, el copiado de la base de datos es efectivo, pero el acceso al `Local State` podría ser detectado si hay un EDR muy agresivo.
* **Empaquetado (PyInstaller)**: Convertir el script en un `.exe` con todas las dependencias (sqlite3, pywin32, cryptodomex) integradas para que sea "portable" y no requiera Python instalado en el objetivo.

---

## 4. Automatización y Reporteo Moderno

### E. Reporte Visual Premium

Sustituir el CSV por un reporte HTML dinámico y elegante:

* Usar una plantilla HTML con búsqueda y filtrado in situ.
* Categorizar contraseñas por "Importancia" (ej. bancos, redes sociales, dominios corporativos).

### F. Escaneo de Credenciales en Red

* Si se tienen credenciales de administrador de dominio, automatizar el despliegue del script vía **PsExec** o **WinRM** en múltiples máquinas para recolectar contraseñas de toda una red en una auditoría interna.

---

## Resumen de Tareas Pendientes para el "Upgrade"

| Mejora | Tipo | Impacto |
| :--- | :--- | :--- |
| **Multi-Chromium** | Funcional | Alto (Extrae más datos) |
| **Exfiltración Remota** | Auditoría | Alto (Rapidez de datos) |
| **Reporte HTML UI** | Presentación | Medio (Profesionalismo) |
| **Wipe Artifacts** | Seguridad | Medio (Antiforense) |
| **Portability (.exe)** | Despliegue | Muy Alto (Sin dependencias) |

---
