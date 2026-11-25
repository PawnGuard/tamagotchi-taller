# radio.py — ESP-NOW: los bichitos se hablan directo, sin router.
#
# Se usa difusion (a FF:FF:FF:FF:FF:FF): todos los del mismo canal oyen todo y
# nadie confirma que el paquete llego. Por eso duelo.py repite sus mensajes.
# La radio solo se prende dentro de AMIGOS: escuchar siempre gasta bateria.
import config

_TODOS = b"\xff" * 6
_sta = None
_e = None


def mi_id():
    """Los ultimos 2 bytes de la MAC: corto y casi unico en un salon."""
    import machine
    uid = machine.unique_id()
    return "%02X%02X" % (uid[-2], uid[-1])


def encender():
    global _sta, _e
    import network
    import espnow
    _sta = network.WLAN(network.STA_IF)
    _sta.active(True)
    try:
        _sta.disconnect()          # que no intente entrar a un Wi-Fi guardado
    except OSError:
        pass
    _sta.config(txpower=config.TXPOWER)
    _sta.config(channel=config.CANAL)
    _e = espnow.ESPNow()
    _e.active(True)
    try:
        _e.add_peer(_TODOS)
    except OSError:
        pass                       # ya estaba agregado


def apagar():
    global _e
    if _e:
        _e.active(False)
        _e = None
    if _sta:
        _sta.active(False)


def enviar(datos):
    try:
        _e.send(_TODOS, datos, False)  # False = no esperar confirmacion
    except OSError as err:
        print("radio:", err)


def recibir():
    """Un mensaje que haya llegado, o None. Nunca espera."""
    _, msg = _e.irecv(0)
    return msg
