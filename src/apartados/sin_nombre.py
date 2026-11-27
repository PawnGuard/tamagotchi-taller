# ble_spam.py — Emisor de paquetes BLE Continuity (Nearby Action).
#
# Al elegir BLE, empieza a emitir paquetes BLE con un Action Type aleatorio
# de la lista, mostrando en pantalla el último emitido.
#
# Presiona C para detener el advertising y salir.
#
# Uso didáctico / de laboratorio: sirve para estudiar cómo se estructuran
# los paquetes de advertising BLE (Manufacturer Specific Data, Continuity).
import dibujo
import random
import time

NOMBRE = "BLE SPAM"

# Tipos de acción Continuity "Nearby Action" típicos
_TYPES = [0x27, 0x09, 0x02, 0x1e, 0x2b, 0x2d, 0x2f, 0x01, 0x06, 0x20, 0xc0]

# Estado del módulo (vive mientras se está en esta "pantalla")
_estado = {
    "ble": None,
    "ultimo": None,      # último action_type emitido
    "emitidos": 0,       # contador
}


def _get_advertisement_data():
    """Construye el paquete de advertising (17 bytes)."""
    packet = bytearray(17)
    packet[0] = 16       # Longitud del bloque AD
    packet[1] = 0xFF     # Tipo AD: Manufacturer Specific
    packet[2] = 0x4C     # Company ID (Apple) byte bajo
    packet[3] = 0x00     # Company ID byte alto
    packet[4] = 0x0F     # Continuity: Nearby Action
    packet[5] = 0x05     # Longitud del mensaje
    packet[6] = 0xC1     # Action Flags

    action_type = random.choice(_TYPES)
    packet[7] = action_type

    for j in range(8, 11):               # Authentication Tag (3 bytes)
        packet[j] = random.getrandbits(8)

    packet[11] = 0x00
    packet[12] = 0x00
    packet[13] = 0x10                    # otro subcampo

    for j in range(14, 17):              # 3 bytes aleatorios
        packet[j] = random.getrandbits(8)

    return packet, action_type


def empezar(bicho):
    """Inicializa el BLE. Se importa aquí para que la PC no falle."""
    import bluetooth
    ble = bluetooth.BLE()
    ble.active(True)
    _estado["ble"] = ble
    _estado["ultimo"] = None
    _estado["emitidos"] = 0


def _emitir():
    """Emite un paquete y actualiza el estado."""
    ble = _estado["ble"]
    adv, action_type = _get_advertisement_data()
    ble.gap_advertise(100_000, adv_data=adv)   # ~100 ms
    _estado["ultimo"] = action_type
    _estado["emitidos"] += 1


def paso(bicho, ms):
    """Llamado periódicamente por el loop del taller: emitimos ~cada 200 ms."""
    if _estado["ble"] is None:
        return
    _emitir()


def tecla(bicho, t):
    t = t.lower()
    if t == "c":
        ble = _estado["ble"]
        if ble is not None:
            ble.gap_advertise(None)   # detener advertising
            try:
                ble.active(False)
            except Exception:
                pass
        return True
    return False


def dibujar(fb, bicho):
    ult = _estado["ultimo"]
    if ult is None:
        texto = "BLE listo..."
    else:
        texto = "0x{:02X} (#{})".format(ult, _estado["emitidos"])
    dibujo.casa(fb, bicho, texto)