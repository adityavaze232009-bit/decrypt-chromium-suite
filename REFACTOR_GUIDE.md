# Guía de Refactorización: Suite Auditoría Chromium Passwords

Este documento detalla el plan integral para transformar el script actual en una herramienta profesional de pentesting en entornos controlados.

## Roadmap Estratégico

| Nivel | Fase | Plazo | Prioridad | Dificultad |
| :--- | :--- | :--- | :--- | :--- |
| **Básico** | **Fase 1: Optimización y Limpieza** | Corto Plazo | Crítica | Fácil |
| **Intermedio** | **Fase 2: Expansión Chromium** | Corto Plazo | Alta | Media |
| **Avanzado** | **Fase 3: Exfiltración y Sigilo** | Medio Plazo | Media | Alta |
| **Experto** | **Fase 4: Empaquetado y Reporteo** | Largo Plazo | Opcional | Muy Alta |

---

## Detalle por Fases

### Fase 1: Optimización y Limpieza (Corto Plazo / Fácil)

**Objetivo**: Mejorar la robustez del código actual y estandarizar su ejecución.

* [ ] **Migración a `pathlib`**: Reemplazar manipulaciones de rutas de `os.path` por objetos `Path`.
* [ ] **Sistema de Logging Silencioso**: Implementar logs en archivo oculto para evitar ruido en consola.
* [ ] **Argumentos de Línea de Comandos**: Añadir `argparse` para controlar perfiles específicos o rutas de salida.
* [ ] **Refactor de Manejo de Excepciones**: Captura de errores granular (ej. errores de permisos vs. base de datos bloqueada).

### Fase 2: Expansión Chromium (Corto Plazo / Media)

**Objetivo**: Ampliar el alcance de la herramienta a todos los navegadores instalados.

* [ ] **Abstraction Layer**: Crear un motor genérico para navegadores basados en Chromium.
* [ ] **Diccionario de Rutas**: Añadir soporte para:
  * Microsoft Edge
  * Brave Browser
  * Opera y Opera GX
  * Vivaldi
* [ ] **Detección Automática**: Escanear rutas comunes para encontrar instalaciones activas de estos navegadores.

### Fase 3: Exfiltración y Sigilo (Medio Plazo / Avanzada)

**Objetivo**: Integrar capacidades ofensivas de recolección de datos y protección.

* [ ] **Módulos de Exfiltración**:
  * Webhook de **Discord** (Envío instantáneo).
  * Notificación vía **Telegram**.
  * Transferencia vía **Post HTTP** a servidor C2.
* [ ] **Técnicas de Sigilo**:
  * Modo "Silent" (Sin salida de consola).
  * Auto-limpieza de artefactos temporales (DBs copiadas).
  * Exclusión de carpetas de análisis de AV (opcional).

### Fase 4: Toolset Avanzado (Largo Plazo / Experto)

**Objetivo**: Profesionalizar el reporte final y facilitar el despliegue.

* [ ] **Reporteo HTML Premium**: Generar un archivo HTML con tablas dinámicas y búsqueda (puedo usar Tailwind o CSS puro inyectado).
* [ ] **Empaquetado con PyInstaller**: Crear un ejecutable portable (`.exe`) que contenga todas las dependencias (sqlite, pywin32).
* [ ] **Estadísticas de Seguridad**: Mostrar un reporte indicando qué contraseñas son débiles o repetidas.

---

## Cómo empezar la ejecución

Se recomienda comenzar con la **Fase 1** para tener una base de código sólida. Una vez completada, la **Fase 2** proporcionará el mayor retorno de inversión en términos de resultados de auditoría.

---
*Este plan ha sido diseñado para auditorías de seguridad en entornos controlados y pentesting ético.*
