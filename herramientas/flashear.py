"""Instala MicroPython en la ESP32-C3 y sube el codigo. Windows, macOS y Linux.

    python herramientas/flashear.py              # busca la placa sola
    python herramientas/flashear.py COM5         # o le dices el puerto
    python herramientas/flashear.py --descargar  # solo baja el firmware (hazlo en casa)
    python herramientas/flashear.py --si         # no pregunta antes de borrar

Solo hace falta si la placa no tiene MicroPython: viene sin firmware, o le
subiste un programa de Arduino. BORRA TODO lo que tiene la placa, tu mascota
guardada (bicho.json) incluida.

Necesita esptool y mpremote:  python -m pip install -r requirements.txt
"""
import hashlib
import os
import subprocess
import sys
import time
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIRMWARE = "ESP32_GENERIC_C3-20260824-v1.29.0.bin"
URL = "https://micropython.org/resources/firmware/" + FIRMWARE
SHA256 = "bf72ed9eb88ad3a8f49d02c3d371f9ea34c90a8a303aeb9e324d8efd4a2a655a"
RUTA = os.path.join(RAIZ, FIRMWARE)
ESPRESSIF = 0x303A          # fabricante del USB de la ESP32-C3


def salir(texto):
    print()
    sys.exit(texto)


def revisar_paquetes():
    faltan = []
    for paquete in ("esptool", "mpremote", "serial"):
        try:
            __import__(paquete)
        except ImportError:
            faltan.append(paquete)
    if faltan:
        salir("Faltan paquetes (%s). Instalalos con:\n"
              "  python -m pip install -r requirements.txt" % ", ".join(faltan))


# --- Firmware ------------------------------------------------------------------

def huella(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def conseguir_firmware():
    """Baja el firmware oficial si no esta, y comprueba que no venga danado."""
    if os.path.exists(RUTA) and huella(RUTA) == SHA256:
        print("Firmware: ya esta descargado.")
        return
    print("Descargando MicroPython 1.29.0 (1.7 MB) de micropython.org...")
    parcial = RUTA + ".part"
    try:
        urllib.request.urlretrieve(URL, parcial)
    except OSError as e:
        salir("No se pudo descargar (%s).\nRevisa tu internet, o bajalo con el navegador:\n"
              "  %s\ny guardalo en la carpeta del repositorio." % (e, URL))
    if huella(parcial) != SHA256:
        os.remove(parcial)
        salir("El archivo descargado no coincide con el oficial. Intenta otra vez.")
    os.replace(parcial, RUTA)
    print("Firmware: listo.")


# --- La placa ------------------------------------------------------------------

def placas():
    from serial.tools import list_ports
    return [p.device for p in list_ports.comports() if p.vid == ESPRESSIF]


def existe(puerto):
    from serial.tools import list_ports
    return puerto in [p.device for p in list_ports.comports()] or os.path.exists(puerto)


def buscar_placa(pedido=None, espera_s=0):
    """Devuelve el puerto de la placa. espera_s: cuanto esperar a que aparezca."""
    limite = time.time() + espera_s
    while True:
        if pedido:                       # te dijeron cual: solo hay que esperarlo
            if existe(pedido):
                return pedido
        else:
            encontradas = placas()
            if len(encontradas) == 1:
                return encontradas[0]
            if len(encontradas) > 1:
                salir("Hay %d placas conectadas: %s\nDeja solo una, o di cual:\n"
                      "  python herramientas/flashear.py %s"
                      % (len(encontradas), ", ".join(encontradas), encontradas[0]))
        if time.time() >= limite:
            if pedido:
                salir("No encuentro el puerto %s. Revisa el nombre con:\n"
                      "  python -m mpremote devs" % pedido)
            salir("No encuentro ninguna ESP32-C3.\n"
                  "- Revisa que el cable sea de datos (con uno que solo carga no se ve).\n"
                  "- Si sigue sin aparecer: desconectala, manten apretado BOOT,\n"
                  "  conectala y suelta BOOT. Luego corre esto otra vez.")
        time.sleep(0.5)


def revisar_puerto(puerto):
    """Abre el puerto un instante para dar un error claro si no se puede."""
    import serial
    try:
        serial.Serial(puerto).close()
    except serial.SerialException as e:
        texto = str(e)
        if "ermission" in texto and sys.platform.startswith("linux"):
            salir("No tienes permiso para usar %s. Corre esto, cierra sesion y vuelve a entrar:\n"
                  "  sudo usermod -aG dialout $USER" % puerto)
        salir("No pude abrir %s: otro programa lo esta usando.\n"
              "Cierra Thonny, el Arduino IDE o cualquier monitor serie y corre esto otra vez."
              % puerto)


def esptool(puerto, *orden):
    cmd = [sys.executable, "-m", "esptool", "--chip", "esp32c3", "--port", puerto]
    return subprocess.call(cmd + list(orden)) == 0


def grabar(puerto):
    if not esptool(puerto, "erase-flash"):
        return False
    return esptool(puerto, "--baud", "460800", "write-flash", "0x0", RUTA)


def contesta(puerto):
    """True si la placa responde como MicroPython."""
    cmd = [sys.executable, "-m", "mpremote", "connect", puerto,
           "exec", "import os; print(os.uname().release)"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        return False
    if r.returncode == 0:
        print("MicroPython", r.stdout.strip(), "funcionando.")
    return r.returncode == 0


# --- Todo junto ------------------------------------------------------------------

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opciones = {a for a in sys.argv[1:] if a.startswith("--")}

    revisar_paquetes()
    conseguir_firmware()
    if "--descargar" in opciones:
        print("Listo. En el taller solo conecta la placa y corre este script sin --descargar.")
        return

    pedido = args[0] if args else None
    puerto = buscar_placa(pedido, espera_s=3)
    print("Placa en", puerto)
    revisar_puerto(puerto)

    if "--si" not in opciones:
        r = input("Esto BORRA todo lo que tiene la placa, tu mascota incluida. Seguir? (s/n) ")
        if r.strip().lower() not in ("s", "si", "sí", "y", "yes"):
            salir("No se borro nada.")

    if not grabar(puerto):
        print("\nNo se pudo grabar. Pon la placa en modo de carga:")
        print("  1. Desconectala.")
        print("  2. Manten apretado el boton BOOT y conectala.")
        print("  3. Suelta BOOT.")
        input("Cuando lo hayas hecho, presiona Enter para reintentar...")
        puerto = buscar_placa(pedido, espera_s=10)
        if not grabar(puerto):
            salir("Tampoco funciono. Pide ayuda al staff.")

    # Despues de grabar, la placa se reinicia y su USB desaparece un momento.
    print("Esperando a que la placa reinicie...")
    time.sleep(2)
    for _ in range(10):
        puerto = buscar_placa(pedido, espera_s=10)
        if contesta(puerto):
            break
        time.sleep(1)
    else:
        salir("MicroPython quedo grabado pero la placa no contesta.\n"
              "Desconectala y conectala, y luego: python herramientas/subir.py")

    print("Subiendo el codigo...")
    codigo = subprocess.call([sys.executable, os.path.join(RAIZ, "herramientas", "subir.py"), puerto])
    if codigo != 0:
        sys.exit(codigo)
    print("Para que arranque sola al conectarla:  python -m mpremote cp autoarranque/main.py :main.py")


if __name__ == "__main__":
    main()
