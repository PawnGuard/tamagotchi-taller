# amigos.py — duelos de piedra, papel o tijera con otros bichitos, por radio.
#
# El protocolo vive en duelo.py (con el truco anti-trampa del compromiso).
# Aqui solo se conecta: la radio, los botones y la pantalla.
#
#   Buscando amigos:  A = siguiente amigo   B = retarlo   C = salir
#   Te retan:         B = aceptar           C = rechazar
#   Eligiendo mano:   A = otra mano         B = confirmar C = rendirse
import duelo
import radio
import sonido
import dibujo
import sprites

NOMBRE = "AMIGOS"

PREMIO_GANAR = 25            # felicidad
PREMIO_EMPATE = 10
PREMIO_PERDER = 5            # jugar siempre alegra un poco
COSTO_ENERGIA = 5

RESULTADOS = {
    duelo.GANE: "GANASTE!", duelo.PERDI: "PERDISTE", duelo.EMPATE: "EMPATE",
    duelo.TRAMPA: "TRAMPA!", duelo.HUYO: "SE RAJO!", duelo.RECHAZO: "NO QUISO",
    duelo.CANCELADO: "CANCELADO",
}

partida = None
amigo = 0                    # a quien estoy viendo en la lista
premiado = False             # ya se dio el premio del duelo que acaba de terminar


def empezar(bicho):
    global partida, amigo, premiado
    radio.encender()
    partida = duelo.Duelo(radio.mi_id(), bicho.figura())
    amigo, premiado = 0, False


def paso(bicho, ms):
    antes = partida.estado
    partida.tick(ms)
    m = radio.recibir()
    while m:
        partida.recibir(m)
        m = radio.recibir()
    _mandar()
    _revisar(bicho, antes)


def tecla(bicho, t):
    global amigo
    p = partida
    if p.estado == duelo.LIBRE:
        lista = p.lista()
        if t == "a" and lista:
            amigo = (amigo + 1) % len(lista)
        elif t == "b" and lista:
            p.retar(lista[amigo % len(lista)])
        elif t == "c":
            return True                       # salir de AMIGOS
    elif p.estado == duelo.INVITADO:
        if t == "b":
            p.aceptar()
        elif t == "c":
            p.rechazar()
    elif p.estado == duelo.ELIGIENDO:
        if t == "a":
            p.siguiente()
        elif t == "b":
            p.confirmar()
        elif t == "c":
            p.abandonar()
    elif p.estado == duelo.FIN:
        p.cerrar()
    elif t == "c":                            # retando o esperando: rajarse
        p.abandonar()
    return False


def terminar(bicho):
    partida.abandonar()
    _mandar()
    radio.apagar()


def _mandar():
    for m in partida.salida:
        radio.enviar(m)
    partida.salida = []


def _revisar(bicho, antes):
    """Sonidos y premios cuando el duelo cambia de estado."""
    global premiado
    p = partida
    if p.estado == duelo.INVITADO and antes != duelo.INVITADO:
        sonido.tocar("reto")
    if p.estado != duelo.FIN:
        premiado = False
        return
    if premiado:
        return
    premiado = True
    bicho.cambiado = True
    if p.mia:
        bicho.energia -= COSTO_ENERGIA
    r = p.resultado
    if r in (duelo.GANE, duelo.TRAMPA, duelo.HUYO):
        bicho.victorias += 1
        bicho.felicidad += PREMIO_GANAR
        sonido.tocar("ganar")
    elif r == duelo.PERDI:
        bicho.derrotas += 1
        bicho.felicidad += PREMIO_PERDER
        sonido.tocar("perder")
    elif r == duelo.EMPATE:
        bicho.felicidad += PREMIO_EMPATE


# --- Pantalla -------------------------------------------------------------------

def textos():
    """Que decir arriba: (renglon 1, renglon 2, mi mano, su mano).
    Las manos son None mientras no hay duelo (entonces se ve al bichito)."""
    p = partida
    st = p.estado
    if st == duelo.LIBRE:
        lista = p.lista()
        if not lista:
            return "BUSCANDO" + "." * (dibujo.cuadro() % 4), "C: salir", None, None
        i = amigo % len(lista)
        quien = lista[i]
        return ("AMIGO %d de %d" % (i + 1, len(lista)),
                "B: retar a %s" % quien, None, None)
    if st == duelo.RETANDO:
        return "RETASTE A " + p.rival, "ESPERANDO...", None, None
    if st == duelo.INVITADO:
        return p.rival + " TE RETA!", "B: SI   C: NO", None, None
    if st == duelo.ELIGIENDO:
        seg = max(0, (duelo.ELEGIR_MS - p._t_quieto) // 1000)
        mano = duelo.JUGADAS[p.seleccion]
        return "<%s>" % mano.upper(), "B: OK  %2d s" % seg, mano, "duda"
    if st == duelo.ESPERANDO:
        # Del rival solo conoces su huella: la ves, pero no te dice su mano.
        huella = p.su_huella[:8] if p.su_huella else "--------"
        return "ESPERANDO", "#" + huella, p.mia, "duda"
    if p.resultado == duelo.TRAMPA:
        abajo = "HUELLA FALSA"
    elif p.mia and p.suya:
        abajo = "%s vs %s" % (p.mia[:3].upper(), p.suya[:3].upper())
    else:
        abajo = ""
    return RESULTADOS.get(p.resultado, p.resultado), abajo, p.mia or "duda", p.suya or "duda"


def dibujar(fb, bicho):
    renglon1, renglon2, mia, suya = textos()
    dibujo.centrado(fb, renglon1, 2)
    dibujo.centrado(fb, renglon2, 14)
    if mia is None:
        dibujo.bichito(fb, bicho, y=30)
    else:
        fb.blit(sprites.imagen(sprites.MANOS[mia], 2), 14, 30)
        dibujo.centrado(fb, "vs", 44)
        fb.blit(sprites.imagen(sprites.MANOS[suya], 2), 94, 30)
