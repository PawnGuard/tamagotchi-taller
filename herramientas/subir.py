"""Sube el codigo de src/ a la placa. Funciona en Windows, macOS y Linux.

    python herramientas/subir.py          # detecta la placa sola
    python herramientas/subir.py COM5     # o le dices el puerto

Es lo mismo que subir.sh, pero sin depender de bash. Necesita mpremote
(python -m pip install mpremote). No borra la mascota guardada (bicho.json)
ni main.py. Cierra Thonny antes: solo un programa puede usar el puerto.
"""
import glob
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "src")

# Borra los .py viejos de la placa (por si renombraste alguno), menos
# boot.py y main.py.
LIMPIAR = """import os
for f in os.listdir():
    if f.endswith('.py') and f not in ('boot.py', 'main.py'):
        os.remove(f)"""


def main():
    try:
        import mpremote  # noqa: F401
    except ImportError:
        sys.exit("Falta mpremote. Instalalo con:  python -m pip install mpremote")

    # Las pruebas en la PC dejan carpetas __pycache__: no hay que subirlas.
    for carpeta in glob.glob(os.path.join(SRC, "**", "__pycache__"), recursive=True):
        shutil.rmtree(carpeta)

    base = [sys.executable, "-m", "mpremote"]
    if len(sys.argv) > 1:
        base += ["connect", sys.argv[1]]

    # mpremote espera para siempre si la placa no contesta como MicroPython,
    # asi que primero se pregunta con un limite de tiempo.
    print("Buscando la placa...", flush=True)
    try:
        prueba = subprocess.run(base + ["exec", "print('ok')"], timeout=10)
    except subprocess.TimeoutExpired:
        sys.exit("La placa esta conectada pero no contesta como MicroPython.\n"
                 "- Si tiene un programa corriendo, desconectala y vuelve a conectarla.\n"
                 "- Si nunca le grabaste MicroPython (o tiene un programa de Arduino),\n"
                 "  pide al staff que la flashee (flashear.sh).")
    if prueba.returncode != 0:
        sys.exit(prueba.returncode)

    archivos = sorted(glob.glob(os.path.join(SRC, "*.py")))
    print("Subiendo", len(archivos), "archivos y la carpeta apartados...", flush=True)
    cmd = base + ["exec", LIMPIAR,
            "+", "cp", *archivos, ":",
            "+", "cp", "-r", os.path.join(SRC, "apartados"), ":",
            "+", "reset"]

    codigo = subprocess.call(cmd)
    if codigo == 0:
        print("Listo. Para jugar: python -m mpremote run src/tama.py")
    sys.exit(codigo)


if __name__ == "__main__":
    main()
