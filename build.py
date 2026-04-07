import os
import sys
import subprocess
import argparse

__version__ = "1.2.0"

def get_python_executable():
    return sys.executable

def run_command(cmd_list, description="Running command"):
    print(f"\n[*] {description}...")
    print(f"Executing: {' '.join(cmd_list)}")
    try:
        result = subprocess.run(cmd_list, check=True, capture_output=True, text=True)
        print("[+] Success.")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[-] Error: {e}")
        print(f"Stdout: {e.output}")
        print(f"Stderr: {e.stderr}")
        return False, e.stderr

def main():
    parser = argparse.ArgumentParser(
        description="Suite de Ofuscación y Compilación Robusta (Build Suite)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python build.py --name "MiApp" --icon "app.ico"
  python build.py --no-obf --onefile
  python build.py --noconsole --dist-dir "./bin"
        """
    )
    
    comp_group = parser.add_argument_group("Opciones de Compilación (PyInstaller)")
    comp_group.add_argument("--name", default="SysHealth", 
                            help="Nombre deseado para el archivo ejecutable (defecto: 'SysHealth').")
    comp_group.add_argument("--multi-file", action="store_true", 
                            help="Crea una carpeta con múltiples archivos en lugar de un único .exe.")
    comp_group.add_argument("--show-console", action="store_true", 
                            help="Muestra la ventana de comandos al ejecutar el archivo.")
    comp_group.add_argument("--icon", default=None, 
                            help="Ruta a un archivo .ico para el icono del programa.")
    comp_group.add_argument("--dist-dir", default="dist", 
                            help="Carpeta de destino para el ejecutable final (defecto: 'dist').")

    obf_group = parser.add_argument_group("Opciones de Ofuscación (PyArmor)")
    obf_group.add_argument("--no-obf", action="store_true", 
                           help="Desactiva la ofuscación de PyArmor y compila solo con PyInstaller vanilla.")
    
    args = parser.parse_args()

    python = get_python_executable()

    if not os.path.exists("main.py"):
        print("[-] Error: main.py not found in current directory.")
        return

    if args.no_obf:
        print("[*] Performing vanilla PyInstaller build (No Obfuscation)...")
        # Check if PyInstaller is available
        v_check, _ = run_command([python, "-m", "PyInstaller", "--version"], "Verifying PyInstaller")
        if not v_check:
            print("[-] Error: PyInstaller is not installed. Run: pip install pyinstaller")
            return

        # Definir parámetros base
        onefile = not args.multi_file
        windowed = not args.show_console

        pyi_cmd = [python, "-m", "PyInstaller", "main.py"]
        if onefile: pyi_cmd.append("--onefile")
        if windowed: pyi_cmd.append("--windowed")
        pyi_cmd.extend(["--hidden-import", "win32crypt"])
        pyi_cmd.extend(["--hidden-import", "Cryptodome"])
        if args.icon and os.path.exists(args.icon): pyi_cmd.extend(["--icon", args.icon])
        pyi_cmd.extend(["--name", args.name, "--distpath", args.dist_dir])
        
        run_command(pyi_cmd, f"Compilando con PyInstaller (Carpeta: {args.dist_dir})")
        print("\n[!] Vanilla build finished.")
        return

    # 1. Detect PyArmor version
    print("[*] Detecting PyArmor version...")
    success, version_out = run_command([python, "-m", "pyarmor.cli", "--version"], "Checking PyArmor CLI")
    
    if success:
        print("[+] PyArmor 8+ detectado.")
        onefile = not args.multi_file
        windowed = not args.show_console

        pyi_opts = []
        if onefile: pyi_opts.append("--onefile")
        if windowed: pyi_opts.append("--windowed")
        pyi_opts.append("--hidden-import=win32crypt")
        pyi_opts.append("--hidden-import=Cryptodome")
        if args.icon and os.path.exists(args.icon): pyi_opts.append(f"--icon={args.icon}")
        pyi_opts.append(f"--name {args.name}")
        pyi_opts.append(f"--distpath {args.dist_dir}")
        
        opts_str = " ".join(pyi_opts)
        run_command([python, "-m", "pyarmor.cli", "cfg", f"pack:pyi_options={opts_str}"], "Configurando PyArmor 9")
        
        # Build
        pack_mode = "onefile" if onefile else "onedir"
        run_command([python, "-m", "pyarmor.cli", "gen", "--output", f"{args.dist_dir}/obfuscated", "--pack", pack_mode, "main.py"], "Compilando con PyArmor 9")
    else:
        # Try legacy pyarmor
        print("[!] PyArmor 8+ CLI no encontrado. Probando modo Legacy...")
        success, version_out = run_command([python, "-m", "pyarmor", "--version"], "Verificando PyArmor Legacy")
        if success:
            print("[+] PyArmor 7.x detectado.")
            onefile = not args.multi_file
            windowed = not args.show_console

            pyi_opts = []
            if onefile: pyi_opts.append("--onefile")
            if windowed: pyi_opts.append("--windowed")
            pyi_opts.append(f"--name {args.name}")
            
            opts_str = " ".join(pyi_opts)
            run_command([python, "-m", "pyarmor", "pack", "-e", opts_str, "main.py"], "Compilando con PyArmor Legacy")
        else:
            print("[-] FATAL: PyArmor not found in environment. Please run: pip install pyarmor")

    print("\n[!] Process finished. Check 'dist/' folder for results.")

if __name__ == "__main__":
    main()
