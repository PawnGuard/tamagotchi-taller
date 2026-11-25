# duelo.py — piedra, papel o tijera por radio... sin que nadie pueda hacer trampa.
#
# El problema: si yo te mando "PIEDRA" y tu me contestas despues, tu ya sabes
# lo que elegi y puedes mandar "PAPEL". Por radio no hay forma de mostrar la
# mano "al mismo tiempo".
#
# La solucion es un ESQUEMA DE COMPROMISO (commit-reveal), el mismo truco que
# usan las subastas en linea y algunos protocolos de blockchain:
#
#   1. Cada quien elige y manda solo una HUELLA: sha256(jugada + sal).
#      La huella no deja adivinar la jugada (la sal es un numero al azar,
#      sin ella bastaria probar las 3 jugadas), pero te AMARRA a ella.
#   2. Cuando ya tienes la huella del otro, revelas tu jugada y tu sal.
#   3. Cada quien recalcula la huella del rival. Si no coincide: TRAMPA.
#
# Este modulo es logica pura: no toca la radio. Deja en `salida` los mensajes
# que hay que mandar y recibe los que llegan con recibir(). Asi se prueba en
# la PC con dos Duelo conectados entre si (ver tests/test_duelo.py).
#
# Ojo: cualquiera puede mandar un mensaje diciendo que es otro bichito. Aqui
# NO hay autenticacion. Ese es justo el siguiente reto del taller.
import hashlib
import binascii
import os

VERSION = "T1"
JUGADAS = ("piedra", "papel", "tijera")
LE_GANA_A = {"piedra": "tijera", "papel": "piedra", "tijera": "papel"}

HOLA_MS = 1000          # cada cuanto avisas "aqui estoy"
REPITE_MS = 400         # ESP-NOW por difusion no confirma: se repite hasta avanzar
OLVIDO_MS = 4000        # un amigo que no se oye en este tiempo ya se fue
PACIENCIA_MS = 20000    # sin avances en este tiempo, el duelo se cancela
ELEGIR_MS = 15000       # si no eliges a tiempo, va lo que tengas seleccionado
ECO_MS = 3000           # despues de terminar, seguir contestando un rato

# Estados del duelo (maquina de estados)
LIBRE = "libre"            # buscando amigos
RETANDO = "retando"        # mande un reto, espero respuesta
INVITADO = "invitado"      # me retaron, el jugador decide
ELIGIENDO = "eligiendo"    # el jugador escoge su mano
ESPERANDO = "esperando"    # ya me comprometi; espero huella y revelacion del otro
FIN = "fin"                # hay resultado

# Resultados
GANE, PERDI, EMPATE = "gane", "perdi", "empate"
TRAMPA = "trampa"          # su revelacion no coincide con su huella
HUYO = "huyo"              # vio mi jugada y nunca revelo la suya
RECHAZO = "rechazo"        # no quiso jugar
CANCELADO = "cancelado"    # alguien abandono o se perdio la senal


def huella(jugada, sal):
    """El compromiso: 16 caracteres hex del sha256 de la jugada con su sal."""
    h = hashlib.sha256((jugada + ":" + sal).encode()).digest()
    return binascii.hexlify(h[:8]).decode()


def _azar():
    return binascii.hexlify(os.urandom(4)).decode()


def quien_gana(mia, suya):
    if mia == suya:
        return EMPATE
    return GANE if LE_GANA_A[mia] == suya else PERDI


class Duelo:
    def __init__(self, yo, forma="bebe", azar=_azar):
        self.yo = yo                # id corto del bichito, p. ej. "6EEC"
        self.forma = forma          # se anuncia en el HOLA para que te reconozcan
        self.azar = azar
        self.amigos = {}            # id -> [forma, ms desde que lo oimos]
        self.salida = []            # mensajes (bytes) por mandar
        self._t_hola = HOLA_MS      # el primer HOLA sale de inmediato
        self._eco = None            # el ultimo duelo terminado, para contestar tarde
        self._t_eco = 0
        self._reiniciar()

    def _reiniciar(self):
        self.estado = LIBRE
        self.rival = None
        self.sid = None             # id del duelo, lo inventa quien reta
        self.seleccion = 0          # indice en JUGADAS mientras eliges
        self.mia = None
        self.sal = None
        self.su_huella = None
        self.suya = None
        self.resultado = None
        self._t_rep = 0
        self._t_quieto = 0          # ms sin avances
        self._revele = False

    # --- lo que hace el jugador ------------------------------------------------

    def lista(self):
        return sorted(self.amigos)

    def retar(self, amigo):
        if self.estado != LIBRE or amigo not in self.amigos:
            return
        self.rival = amigo
        self.sid = self.azar()[:4]
        self.estado = RETANDO
        self._t_quieto = 0
        self._mandar("RETO")

    def aceptar(self):
        if self.estado == INVITADO:
            self._mandar("SI")
            self._a_elegir()

    def rechazar(self):
        if self.estado == INVITADO:
            self._mandar("NO")
            self._reiniciar()

    def siguiente(self):
        if self.estado == ELIGIENDO:
            self.seleccion = (self.seleccion + 1) % len(JUGADAS)

    def confirmar(self):
        """Fija la jugada y manda SOLO la huella. La jugada sigue en secreto."""
        if self.estado != ELIGIENDO:
            return
        self.mia = JUGADAS[self.seleccion]
        self.sal = self.azar()
        self.estado = ESPERANDO
        self._t_quieto = 0
        self._mandar("HUELLA", huella(self.mia, self.sal))
        if self.su_huella:
            self._revelar()

    def abandonar(self):
        if self.estado in (RETANDO, ELIGIENDO, ESPERANDO):
            self._mandar("NO")
        self._reiniciar()

    def cerrar(self):
        """Salir de la pantalla de resultado. Se recuerda el duelo un rato por
        si al rival le falto nuestra revelacion."""
        if self.estado == FIN and self.mia and self._revele:
            self._eco = (self.rival, self.sid, self.mia, self.sal)
            self._t_eco = 0
        self._reiniciar()

    # --- el paso del tiempo ----------------------------------------------------

    def tick(self, dt):
        for amigo in list(self.amigos):
            self.amigos[amigo][1] += dt
            if self.amigos[amigo][1] > OLVIDO_MS:
                del self.amigos[amigo]

        self._t_hola += dt
        if self._t_hola >= HOLA_MS:
            self._t_hola = 0
            self.salida.append(self._armar("*", "HOLA", self.forma))

        if self._eco:
            self._t_eco += dt
            if self._t_eco > ECO_MS:
                self._eco = None

        if self.estado in (LIBRE, INVITADO, FIN):
            return

        self._t_quieto += dt
        if self.estado == ELIGIENDO and self.mia is None and self._t_quieto >= ELEGIR_MS:
            self.confirmar()                    # se acabo el tiempo para elegir
        elif self._t_quieto >= PACIENCIA_MS:
            # Si ya revele y el otro nunca lo hizo, vio mi mano y se rajo.
            self._terminar(HUYO if self._revele else CANCELADO)
            return

        self._t_rep += dt
        if self._t_rep >= REPITE_MS:
            self._t_rep = 0
            if self.estado == RETANDO:
                self._mandar("RETO")
            elif self.estado == ESPERANDO:
                self._mandar("HUELLA", huella(self.mia, self.sal))
                if self._revele:
                    self._mandar("REVELO", self.mia, self.sal)

    # --- mensajes --------------------------------------------------------------
    #
    # Formato (texto plano, a proposito: se puede leer y falsificar):
    #     T1|de|para|tipo|datos...
    # para = "*" es para todos.

    def _armar(self, para, tipo, *datos):
        return "|".join((VERSION, self.yo, para, tipo) + datos).encode()

    def _mandar(self, tipo, *datos):
        self.salida.append(self._armar(self.rival, tipo, self.sid, *datos))

    def recibir(self, datos):
        try:
            partes = datos.decode().split("|")
        except (UnicodeError, AttributeError):
            return
        if len(partes) < 4 or partes[0] != VERSION:
            return
        de, para, tipo, resto = partes[1], partes[2], partes[3], partes[4:]
        if de == self.yo or para not in (self.yo, "*"):
            return

        if tipo == "HOLA":
            self.amigos[de] = [resto[0] if resto else "?", 0]
            return
        if de in self.amigos:
            self.amigos[de][1] = 0
        if not resto:
            return
        sid = resto[0]

        # Un duelo que ya cerramos: si el rival sigue preguntando, le
        # volvemos a dar nuestra revelacion para que el tambien termine.
        if self._eco and self._eco[0] == de and self._eco[1] == sid:
            if tipo in ("HUELLA", "REVELO"):
                _, _, mia, sal = self._eco
                self.salida.append(self._armar(de, "REVELO", sid, mia, sal))
            return

        if tipo == "RETO":
            self._llega_reto(de, sid)
            return
        if de != self.rival or sid != self.sid:
            return                              # no es nuestro duelo
        if self.estado == FIN:
            if self._revele and tipo in ("HUELLA", "REVELO"):
                self._mandar("REVELO", self.mia, self.sal)
            return

        if tipo == "SI":
            if self.estado == RETANDO:
                self._a_elegir()
        elif tipo == "NO":
            if self.estado not in (FIN, LIBRE):
                self._terminar(RECHAZO if self.estado == RETANDO else CANCELADO)
        elif tipo == "HUELLA" and len(resto) > 1:
            self._llega_huella(resto[1])
        elif tipo == "REVELO" and len(resto) > 2:
            self._llega_revelacion(resto[1], resto[2])

    def _llega_reto(self, de, sid):
        if self.estado == LIBRE:
            self.estado = INVITADO
            self.rival, self.sid = de, sid
            self._t_quieto = 0
        elif self.estado == RETANDO and de == self.rival:
            # Nos retamos al mismo tiempo. Desempate: cede el id menor.
            if self.yo < de:
                self.sid = sid
                self._mandar("SI")
                self._a_elegir()
        elif de == self.rival and sid == self.sid:
            if self.estado in (ELIGIENDO, ESPERANDO):
                self._mandar("SI")              # mi SI se perdio: lo repito
        else:
            # Ocupado en otro duelo: le digo que no, con SU id de duelo.
            self.salida.append(self._armar(de, "NO", sid))

    def _llega_huella(self, h):
        if self.estado == RETANDO:              # el SI se perdio pero ya juega
            self._a_elegir()
        if self.estado not in (ELIGIENDO, ESPERANDO):
            return
        if self.su_huella is None:
            self.su_huella = h
            self._t_quieto = 0
            if self.estado == ESPERANDO:
                self._revelar()
        elif self.su_huella != h:
            self._terminar(TRAMPA)              # cambio su compromiso a medio juego

    def _llega_revelacion(self, jugada, sal):
        # Solo cuenta si ya teniamos su huella y ya elegimos: antes no se mira.
        if self.estado != ESPERANDO or self.su_huella is None or not self._revele:
            return
        if jugada not in JUGADAS or huella(jugada, sal) != self.su_huella:
            self.suya = jugada if jugada in JUGADAS else None
            self._terminar(TRAMPA)
            return
        self.suya = jugada
        self._terminar(quien_gana(self.mia, jugada))

    def _a_elegir(self):
        self.estado = ELIGIENDO
        self._t_quieto = 0

    def _revelar(self):
        self._revele = True
        self._t_quieto = 0
        self._mandar("REVELO", self.mia, self.sal)

    def _terminar(self, resultado):
        self.resultado = resultado
        self.estado = FIN
