# Solución de Problemas Comunes

Este documento detalla los problemas frecuentes encontrados durante la compilación y ofuscación del proyecto y cómo resolverlos.

## 1. PyArmor: El término 'pyarmor' no se reconoce como nombre de comando

### Síntoma
Intentas ejecutar `pyarmor` y recibes un mensaje de error indicando que no se reconoce el comando.

### Causa
Esto suele ocurrir por dos razones principales:
1. El directorio de scripts de Python (ej. `C:\Python314\Scripts\`) no está correctamente agregado al PATH del sistema.
2. La instalación de PyArmor prefirió el módulo CLI directo en lugar de crear un ejecutable global.

### Solución (Mediante build.py)
Para evitar errores manuales y problemas de PATH, usa el script de automatización incluido:
```powershell
python build.py --name "NombreApp"
```

Alternativamente, puedes usar el punto de entrada directo del módulo:
```powershell
python -m pyarmor.cli --version
```

---

## 2. Error de sintaxis en `pyarmor pack` (Incompatibilidad de Versión)

### Síntoma
Recibes un error de argumentos o comandos desconocidos al intentar usar `pyarmor pack` como en versiones antiguas de tutoriales.

### Causa
Has instalado **PyArmor 8.x o 9.x**, donde el flujo de empaquetado cambió drásticamente respecto a la versión 7. El comando `pack` ya no existe de la misma forma y los parámetros han sido reestructurados.

### Solución para PyArmor 9+
Debes usar el comando `gen --pack`. A continuación se muestra cómo lograr el equivalente a un `--onefile --noconsole`:

1. **Configurar opciones de PyInstaller**:
   Define el nombre del ejecutable y las configuraciones de consola en la configuración local de PyArmor:
   ```powershell
   python -m pyarmor.cli cfg pack:pyi_options="--onefile --noconsole --name SysHealth"
   ```

2. **Ejecutar el empaquetado**:
   Genera el ejecutable pasando el parámetro `--pack`:
   ```powershell
   python -m pyarmor.cli gen --pack onefile main.py
   ```

3. **Verificación**:
   El resultado aparecerá en la carpeta `dist/`. Ten en cuenta que si usas la versión **Trial**, existen límites en la complejidad de los scripts que puedes ofuscar.
