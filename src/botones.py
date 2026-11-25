# botones.py — los botones A, B y C, sin bloquear y sin rebotes.
#
# revisar() se llama 20 veces por segundo. Devuelve la tecla que se ACABA de
# apretar ("a", "b" o "c"), o None. Ademas deja en `apretados` las que siguen
# apretadas en este momento (el pong lo usa para mover la paleta).
#
# Rebote: al apretar, el metal del boton "tiembla" y la senal cambia varias
# veces en pocos milisegundos. Por eso un cambio solo cuenta si pasaron
# REBOTE_MS desde el anterior.
from machine import Pin
from time import ticks_ms, ticks_diff
import config

REBOTE_MS = 30

apretados = set()
_pines = {}
_t_cambio = {}


def iniciar():
    for tecla, gpio in config.BOTONES:
        _pines[tecla] = Pin(gpio, Pin.IN, Pin.PULL_UP)   # suelto = 1, apretado = 0
        _t_cambio[tecla] = 0


def revisar():
    nueva = None
    ahora = ticks_ms()
    for tecla, pin in _pines.items():
        abajo = pin.value() == 0
        if abajo != (tecla in apretados) and ticks_diff(ahora, _t_cambio[tecla]) > REBOTE_MS:
            _t_cambio[tecla] = ahora
            if abajo:
                apretados.add(tecla)
                nueva = nueva or tecla
            else:
                apretados.discard(tecla)
    return nueva
