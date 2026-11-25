#!/usr/bin/env bash
# subir.sh — copia el codigo de src/ a la placa y reinicia al bichito.
#
#   ./subir.sh                 # detecta el puerto solo
#   ./subir.sh /dev/ttyACM1    # o se lo dices
#
# No borra la mascota guardada (bicho.json) ni main.py. Si un monitor serie
# esta abierto (Arduino IDE, VS Code), cierralo antes: solo uno puede usar
# el puerto.
set -euo pipefail
cd "$(dirname "$0")"

PUERTO="${1:-$(ls /dev/ttyACM* 2>/dev/null | head -1)}"
[ -n "$PUERTO" ] || { echo "No encuentro ningun /dev/ttyACM*. Conecta la placa."; exit 1; }
echo "Puerto: $PUERTO"

# Las pruebas en la PC dejan carpetas __pycache__: no hay que subirlas.
find src -name __pycache__ -prune -exec rm -rf {} +

mpremote connect "$PUERTO" \
    exec "import os
for f in os.listdir():
    if f.endswith('.py') and f not in ('boot.py', 'main.py'):
        os.remove(f)" \
    + cp src/*.py : \
    + cp -r src/apartados : \
    + reset

echo "Listo. Si la placa tiene main.py, el bichito ya arranco con el codigo nuevo."
echo "Si no:  mpremote connect $PUERTO run src/tama.py"
