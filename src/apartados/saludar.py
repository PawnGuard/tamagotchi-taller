# saludar.py — EJERCICIO 1 del taller.
#
# Al elegir SALUDAR el bichito saluda: sale un texto abajo, pone cara feliz
# y se alegra un poco. Con A cambias el saludo. Si saludas mucho rato, se cansa.
# Sales con C.
import dibujo
import sonido

NOMBRE = "SALUDAR"

# Saludos entre los que rota la tecla A.
SALUDOS = ("Saludando", "Hola!", "Que onda!", "Buenas!")

ALEGRIA = 10          # cuanto sube la felicidad al empezar a saludar
CANSA_CADA_MS = 3000  # cada 3 s de saludar...
CANSANCIO = 2         # ...baja 2 de energia (se cansa si te pasas de rato)

_saludo = 0           # cual saludo se muestra ahora
_acumulado = 0        # ms saludando, para contar el cansancio


def empezar(bicho):
    global _saludo, _acumulado
    _saludo = 0
    _acumulado = 0
    sonido.tocar("nacer")                                  # un sonidito al saludar
    bicho.felicidad = min(100, bicho.felicidad + ALEGRIA)  # saludar alegra


def tecla(bicho, t):
    global _saludo
    if t == "a":
        _saludo = (_saludo + 1) % len(SALUDOS)   # A cambia el saludo
        return False                             # no salimos, seguimos saludando
    return t == "c"                              # solo C sale


def paso(bicho, ms):
    """Se llama en cada vuelta mientras saludas. Si saludas mucho, cansa."""
    global _acumulado
    _acumulado += ms
    if _acumulado >= CANSA_CADA_MS:
        _acumulado -= CANSA_CADA_MS
        bicho.energia = max(0, bicho.energia - CANSANCIO)


def dibujar(fb, bicho):
    dibujo.casa(fb, bicho, SALUDOS[_saludo])     # dibuja la escena + el saludo