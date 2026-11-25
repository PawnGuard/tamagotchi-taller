# memoria.py — guardar y cargar el bichito en la flash.
#
# Escritura atomica: se escribe a un archivo temporal y luego se renombra.
# Si se corta la luz a mitad de la escritura, queda el archivo viejo intacto
# (nunca uno a medias). Es la misma tecnica que usan las bases de datos.
import json
import os
import config


def cargar():
    """Devuelve el dict guardado, o None si no hay nada o esta corrupto."""
    try:
        with open(config.ARCHIVO) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def guardar(est):
    tmp = config.ARCHIVO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(est, f)
    try:
        os.rename(tmp, config.ARCHIVO)        # atomico en littlefs
    except OSError:                                  # FAT no pisa archivos:
        os.remove(config.ARCHIVO)             # borrar y renombrar
        os.rename(tmp, config.ARCHIVO)


def borrar():
    try:
        os.remove(config.ARCHIVO)
    except OSError:
        pass
