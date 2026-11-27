# wifi_rickroll.py — Broma inofensiva: un AP real con nombre cambiante
import dibujo
import network
import time

NOMBRE = "RICKROLL"

_estado = {"ap": None, "indice": 0, "tiempo": 0}

# Fragmentos de la letra (cada uno será el SSID)
_LETRA = [
    "Never gonna give you up",
    "Never gonna let you down",
    "Never gonna run around",
    "And desert you",
]

def empezar(bicho):
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=_LETRA[0], password="12345678")  # WPA2, mínimo 8 caracteres
    _estado["ap"] = ap
    _estado["indice"] = 0
    _estado["tiempo"] = 0

def paso(bicho, ms):
    _estado["tiempo"] += ms
    if _estado["tiempo"] >= 200:          # cambia cada 20 s
        _estado["tiempo"] = 0
        _estado["indice"] = (_estado["indice"] + 1) % len(_LETRA)
        try:
            _estado["ap"].config(essid=_LETRA[_estado["indice"]])
        except Exception:
            pass

def tecla(bicho, t):
    if t.lower() == "c":
        if _estado["ap"] is not None:
            _estado["ap"].active(False)
        return True
    return False

def dibujar(fb, bicho):
    texto = _LETRA[_estado["indice"]][:14]  # recortado para pantalla
    dibujo.casa(fb, bicho, texto)