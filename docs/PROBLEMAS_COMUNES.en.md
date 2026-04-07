# Common Troubleshooting (English)

This document outlines frequent issues encountered during the build and obfuscation of the project and how to resolve them.

---

## 1. PyArmor: The term 'pyarmor' is not recognized

### Symptom
Attempting to run `pyarmor` results in an error message indicating the command is not recognized.

### Cause
This typically happens for two reasons:
1. The Python scripts directory (e.g., `C:\Python314\Scripts\`) is not correctly added to the system PATH.
2. The PyArmor installation preferred the direct CLI module instead of creating a global executable.

### Solution (Using build.py)
To prevent manual errors and PATH issues, use the included automation script:
```powershell
python build.py --name "AppName"
```

Alternatively, use the direct module entry point:
```powershell
python -m pyarmor.cli --version
```

---

## 2. Syntax Error in `pyarmor pack` (Version Incompatibility)

### Symptom
Receiving error messages for unknown arguments or commands when using `pyarmor pack`, following older tutorials.

### Cause
You have installed **PyArmor 8.x or 9.x**, where the bundling workflow changed significantly compared to version 7. The `pack` command no longer exists in its previous form, and arguments have been restructured.

### Solution for PyArmor 9+
Use the `gen --pack` command. Below is the equivalent to `--onefile --noconsole`:

1. **Configure PyInstaller Options**:
   Set the executable name and console flags in PyArmor's local configuration:
   ```powershell
   python -m pyarmor.cli cfg pack:pyi_options="--onefile --noconsole --name SysHealth"
   ```

2. **Run Execution/Bundle**:
   Generate the obfuscated bundle using the `--pack` flag:
   ```powershell
   python -m pyarmor.cli gen --pack onefile main.py
   ```

3. **Verification**:
   The output produced will be in the `dist/` directory. Note that if using the **Trial version**, there are limits on script complexity and obfuscation.
