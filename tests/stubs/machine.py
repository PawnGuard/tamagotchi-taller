# Stub de machine para correr el codigo del dispositivo en la PC.
class Pin:
    IN = 0
    OUT = 1
    PULL_UP = 2
    _estado = {}                  # gpio -> valor que devuelve value()

    def __init__(self, n, modo=None, pull=None, value=None):
        self.n = n
        if value is not None:
            Pin._estado[n] = value

    def value(self, v=None):
        if v is None:
            return Pin._estado.get(self.n, 1)
        Pin._estado[self.n] = v


class SoftI2C:
    def __init__(self, **kw):
        pass

    def scan(self):
        return [0x27]

    def writeto(self, direccion, datos):
        pass


I2C = SoftI2C


class PWM:
    def __init__(self, pin):
        self.pin = pin
        self._freq = 0
        self._duty = 0

    def freq(self, f=None):
        if f is None:
            return self._freq
        self._freq = f

    def duty_u16(self, d=None):
        if d is None:
            return self._duty
        self._duty = d
