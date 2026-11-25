# sonido.py — melodias en el piezo, sin detener al bichito.
#
#   sonido.tocar("comer")
#
# tocar() solo deja la melodia en una fila; atender() (lo llama tama.py todo
# el tiempo) cambia de nota cuando toca. Nunca hay sleep().
#
# Sin iniciar() (por ejemplo en las pruebas en la PC) no suena nada, pero
# `ultima` recuerda que melodia se pidio.
from time import ticks_ms, ticks_diff, ticks_add
import config

# (frecuencia en Hz, duracion en ms). Frecuencia 0 = silencio.
MELODIAS = {
    "nacer":  ((523, 120), (659, 120), (784, 220)),
    "comer":  ((880, 70),),
    "curar":  ((659, 80), (523, 80), (659, 140)),
    "alerta": ((1200, 90), (0, 70), (1200, 90)),
    "muerte": ((392, 220), (330, 220), (262, 420)),
    "reto":   ((988, 60), (0, 40), (988, 60), (1319, 140)),
    "ganar":  ((523, 90), (659, 90), (784, 90), (1047, 240)),
    "perder": ((392, 160), (370, 160), (349, 300)),
    "tic":    ((1760, 25),),
}

ultima = None
_pwm = None
_fila = []
_hasta = 0


def iniciar():
    global _pwm
    if config.PIN_PIEZO is not None:
        from machine import Pin, PWM
        _pwm = PWM(Pin(config.PIN_PIEZO))
        _pwm.duty_u16(0)


def tocar(nombre):
    global ultima, _fila, _hasta
    ultima = nombre
    _fila = list(MELODIAS.get(nombre, ()))
    _hasta = ticks_ms()


def atender():
    global _hasta
    if not _pwm or ticks_diff(ticks_ms(), _hasta) < 0:
        return
    if _fila:
        freq, ms = _fila.pop(0)
        if freq:
            _pwm.freq(freq)
            _pwm.duty_u16(20000)
        else:
            _pwm.duty_u16(0)
        _hasta = ticks_add(ticks_ms(), ms)
    else:
        _pwm.duty_u16(0)


def sonando():
    """True mientras quede melodia por tocar."""
    return bool(_fila) or ticks_diff(_hasta, ticks_ms()) > 0


def callar():
    global _fila
    _fila = []
    if _pwm:
        _pwm.duty_u16(0)
