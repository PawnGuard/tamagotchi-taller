# juego.py — las pantallas del bichito y a donde lleva cada boton.
#
# Logica pura: no toca hardware. tama.py le avisa de lo que pasa:
#   tecla(t)        se apreto "a", "b" o "c"
#   paso(ms)        pasaron ms milisegundos
#   dibujar(fb)     pinta la pantalla
#
# Maquina de estados de la pantalla:
#
#   CASA --A--> MENU --B--> APARTADO --(el apartado dice que termino)--> MENU
#               MENU --C--> CASA
#
# Cada opcion del menu es un APARTADO: un archivo en apartados/ (ver
# apartados/__init__.py). Mientras estas dentro de un apartado, el tiempo del
# bichito se detiene: no le da hambre mientras juegas.
import config
import dibujo
import menu
from bicho import Bicho, HUEVO, MUERTO

CASA, MENU, APARTADO = "casa", "menu", "apartado"
AVISO_MS = 1500

bicho = None
pantalla = CASA
elegido = 0             # que opcion del menu esta seleccionada
activo = None           # el apartado abierto
_aviso = None           # texto que sale abajo un momento
_t_aviso = 0


def empezar(guardado=None):
    global bicho, pantalla, elegido, activo, _aviso
    bicho = Bicho(guardado)
    pantalla, elegido, activo, _aviso = CASA, 0, None, None


def avisar(texto):
    """Muestra un texto abajo de la pantalla por AVISO_MS."""
    global _aviso, _t_aviso
    _aviso, _t_aviso = texto, AVISO_MS


def tecla(t):
    global pantalla, elegido, _aviso
    if pantalla == APARTADO:
        if hasattr(activo, "tecla"):
            termino = _llamar("tecla", t)
        else:
            termino = t == "c"          # sin tecla(), C te saca
        if termino:
            _cerrar()
        return
    if _aviso:                          # cualquier tecla quita el aviso
        _aviso = None
        return
    if bicho.etapa == MUERTO:
        if t == "b":
            empezar()
            avisar("HUEVO NUEVO")
        return
    if pantalla == CASA:
        if t == "a":
            pantalla = MENU
    elif pantalla == MENU:
        if t == "a":
            elegido = (elegido + 1) % len(menu.MENU)
        elif t == "b":
            _abrir(menu.MENU[elegido])
        elif t == "c":
            pantalla = CASA


def paso(ms):
    global _aviso, _t_aviso
    dibujo.reloj += ms
    if _aviso:
        _t_aviso -= ms
        if _t_aviso <= 0:
            _aviso = None
    if pantalla == APARTADO:
        if hasattr(activo, "paso") and _llamar("paso", ms):
            _cerrar()
        return
    aviso = bicho.vivir(ms / 1000 * config.ESCALA / 60)
    if aviso:
        avisar(aviso)


def dibujar(fb):
    fb.fill(0)
    if pantalla == APARTADO:
        if hasattr(activo, "dibujar"):
            activo.dibujar(fb, bicho)
        else:
            dibujo.casa(fb, bicho, activo.NOMBRE)
    elif _aviso:
        dibujo.casa(fb, bicho, _aviso)
    elif pantalla == MENU:
        dibujo.casa(fb, bicho, "<%s>" % menu.MENU[elegido].NOMBRE, recuadro=True)
    else:
        dibujo.casa(fb, bicho)


# --- Abrir y cerrar apartados -------------------------------------------------

def abrir(ap):
    """Abre un apartado sin pasar por el menu (tama.py lo usa para el INTRO)."""
    _abrir(ap)


def _abrir(ap):
    global pantalla, activo
    if not getattr(ap, "SIEMPRE", False):
        if bicho.etapa == HUEVO:
            return avisar("AUN NO NACE")
        if bicho.dormido():
            return avisar("ZZZ...")
    activo = ap
    respuesta = _llamar("empezar")
    if isinstance(respuesta, str):      # accion rapida: dice algo y listo
        activo = None
        avisar(respuesta)
    else:
        pantalla = APARTADO


def _llamar(funcion, *datos):
    """Llama a una funcion del apartado y luego cuida al bichito."""
    respuesta = getattr(activo, funcion)(bicho, *datos)
    bicho.limitar()                     # por si el apartado se paso de 100
    if funcion != "paso":
        bicho.cambiado = True           # para que se guarde
    if bicho.etapa == MUERTO:
        return True                     # si se murio, se acaba el apartado
    return respuesta


def _cerrar():
    global pantalla, activo
    if hasattr(activo, "terminar"):
        respuesta = activo.terminar(bicho)
        bicho.limitar()
        if isinstance(respuesta, str):
            avisar(respuesta)
    pantalla, activo = MENU, None
