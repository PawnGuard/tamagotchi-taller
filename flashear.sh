#!/usr/bin/env bash
# flashear.sh — instala MicroPython en una ESP32-C3 y sube el proyecto.
#
#   ./flashear.sh                 # detecta el puerto solo
#   ./flashear.sh /dev/ttyACM1    # o se lo dices
#
# Las placas vienen de fabrica SIN firmware: el sintoma es que el puerto
# escupe "invalid header: 0xffffffff" y mpremote falla con Errno 5.
set -euo pipefail

VERSION="20260824-v1.29.0"
FIRMWARE="ESP32_GENERIC_C3-${VERSION}.bin"
URL="https://micropython.org/resources/firmware/${FIRMWARE}"
PUERTO="${1:-$(ls /dev/ttyACM* 2>/dev/null | head -1)}"

[ -n "$PUERTO" ] || { echo "No encuentro ningun /dev/ttyACM*. Conecta la placa."; exit 1; }
echo "Puerto: $PUERTO"

if [ ! -f "$FIRMWARE" ]; then
    echo "Descargando $FIRMWARE ..."
    curl -fL -o "$FIRMWARE" "$URL"
fi

echo "Borrando la flash ..."
esptool --chip esp32c3 --port "$PUERTO" erase-flash

echo "Instalando MicroPython ..."
esptool --chip esp32c3 --port "$PUERTO" --baud 460800 write-flash 0x0 "$FIRMWARE"

sleep 3
echo "Verificando ..."
mpremote connect "$PUERTO" exec "import os; print(os.uname())"

echo "Subiendo el proyecto ..."
./subir.sh "$PUERTO"

echo
echo "Listo. Ahora:"
echo "  mpremote connect $PUERTO run src/prueba.py    # autodiagnostico"
echo "  mpremote connect $PUERTO run src/tama.py      # arrancar el bichito"
