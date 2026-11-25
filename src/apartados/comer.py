# comer.py — una accion rapida: cambia al bichito y devuelve un texto.
import sonido

NOMBRE = "COMER"


def empezar(bicho):
    if bicho.hambre >= 100:
        return "LLENO!"
    bicho.hambre += 30
    sonido.tocar("comer")
    return "NAM NAM"
