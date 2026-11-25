# bicho.py — el modelo: que necesita el bichito y como cambia con el tiempo.
#
# Logica pura: no toca pantalla ni botones, asi que se prueba en la PC.
# Todas las barras van de 0 a 100. El tiempo se mide en MINUTOS DE JUEGO
# (config.ESCALA decide cuantos pasan por cada segundo real).
import sonido

# Etapas de la vida:  HUEVO -> BEBE -> ADULTO -> MUERTO
HUEVO, BEBE, ADULTO, MUERTO = "huevo", "bebe", "adulto", "muerto"

# Cuanto baja cada barra por minuto de juego
BAJA = {
    "hambre":    100 / 240,   # de lleno a vacio en 4 h
    "felicidad": 100 / 180,   # 3 h
    "energia":   100 / 480,   # 8 h despierto
}
RECUPERA_ENERGIA = 100 / 120  # durmiendo se recarga en 2 h
SALUD_BAJA = 100 / 180        # con algo critico, muere en 3 h
SALUD_SUBE = 100 / 240        # bien cuidado, se recupera en 4 h
CACA_CADA = 90                # minutos entre cacas
SUCIO_ENFERMA = 30            # minutos con 3 cacas antes de enfermarse
NACE = 30                     # minutos dentro del huevo
CRECE = 24 * 60               # minutos de bebe antes de ser adulto

# Crianza: los ERRORES de cuidado de bebe deciden en que se convierte.
# Un error es dejarlo pidiendo algo (el "!") mas de LLAMADA minutos.
LLAMADA = 15
ERRORES_ANGEL = 1             # con tan pocos errores: angel
ERRORES_BICHO = 4             # hasta aqui: bicho comun; mas: diablo
VICTORIAS_HACKER = 5          # forma secreta: bien cuidado y buen duelista

# Lo que se guarda en la flash (y su valor al nacer)
INICIO = {
    "etapa": HUEVO,
    "edad": 0.0,          # minutos de juego
    "hambre": 80.0,       # 100 = lleno
    "felicidad": 80.0,
    "energia": 80.0,
    "salud": 100.0,
    "caca": 0,            # 0..3
    "enfermo": False,
    "luz": True,          # luz apagada = duerme
    "forma": "bebe",      # de adulto: bicho, angel, diablo o hacker
    "errores": 0,         # errores de cuidado mientras fue bebe
    "victorias": 0,       # duelos de piedra, papel o tijera
    "derrotas": 0,
    "t_caca": 0.0,        # minutos desde la ultima caca
    "t_sucio": 0.0,       # minutos seguidos con 3 cacas
    "t_llamada": 0.0,     # minutos seguidos pidiendo atencion
}


class Bicho:
    def __init__(self, guardado=None):
        for campo, valor in INICIO.items():
            setattr(self, campo, valor)
        if guardado:
            for campo in INICIO:
                if campo in guardado:          # un guardado viejo hereda lo nuevo
                    setattr(self, campo, guardado[campo])
        self.cambiado = False                  # True = vale la pena guardar

    def para_guardar(self):
        return {campo: getattr(self, campo) for campo in INICIO}

    def limitar(self):
        """Deja las barras entre 0 y 100 (por si alguien se paso)."""
        for b in ("hambre", "felicidad", "energia", "salud"):
            setattr(self, b, max(0.0, min(100.0, float(getattr(self, b)))))
        self.caca = max(0, min(3, int(self.caca)))

    # --- Lo que se calcula (no se guarda) ------------------------------------

    def dormido(self):
        return not self.luz

    def figura(self):
        """Que cuerpo dibujar."""
        if self.etapa in (HUEVO, MUERTO):
            return self.etapa
        return "bebe" if self.etapa == BEBE else self.forma

    def animo(self):
        """Que cara poner."""
        if self.dormido():
            return "dormido"
        if self.enfermo or self.hambre < 30 or self.felicidad < 30:
            return "triste"
        if self.felicidad > 70 and self.hambre > 50:
            return "feliz"
        return "normal"

    def pide_atencion(self):
        """El "!" de la pantalla. Dormido, el cansancio no cuenta."""
        if self.etapa not in (BEBE, ADULTO):
            return False
        cansado = self.energia < 20 and not self.dormido()
        return (self.enfermo or self.caca >= 3 or self.hambre < 20
                or self.felicidad < 20 or cansado)

    def forma_adulta(self):
        """La evolucion: en que se convierte segun como lo criaste."""
        if self.errores <= ERRORES_BICHO and self.victorias >= VICTORIAS_HACKER:
            return "hacker"
        if self.errores <= ERRORES_ANGEL:
            return "angel"
        if self.errores <= ERRORES_BICHO:
            return "bicho"
        return "diablo"

    # --- El paso del tiempo ---------------------------------------------------

    def vivir(self, minutos):
        """Avanza la vida. Devuelve un aviso para la pantalla, o None."""
        if self.etapa == MUERTO:
            return None
        self.edad += minutos
        if self.etapa == HUEVO:
            if self.edad >= NACE:
                self.etapa = BEBE
                self.cambiado = True
                sonido.tocar("nacer")
                return "NACIO!"
            return None

        # las barras bajan (dormido, a la mitad) y dormir recarga energia
        lento = 0.5 if self.dormido() else 1.0
        for barra, tasa in BAJA.items():
            setattr(self, barra, max(0.0, getattr(self, barra) - tasa * minutos * lento))
        if self.dormido():
            self.energia = min(100.0, self.energia + RECUPERA_ENERGIA * minutos)

        # caca, y si se acumula, enfermedad
        if not self.dormido():
            self.t_caca += minutos
            if self.t_caca >= CACA_CADA:
                self.t_caca = 0.0
                self.caca = min(3, self.caca + 1)
                self.cambiado = True
        if self.caca >= 3:
            self.t_sucio += minutos
            if self.t_sucio >= SUCIO_ENFERMA and not self.enfermo:
                self.enfermo = True
                self.cambiado = True
        else:
            self.t_sucio = 0.0

        # salud: baja si algo esta en estado critico, si no, se recupera
        critico = (self.hambre <= 0 or self.felicidad <= 0 or self.energia <= 0
                   or self.enfermo or self.caca >= 3)
        cambio = -SALUD_BAJA if critico else SALUD_SUBE
        self.salud = max(0.0, min(100.0, self.salud + cambio * minutos))

        if self.etapa == BEBE:
            self._vigilar_llamada(minutos)

        if self.salud <= 0:
            self.etapa = MUERTO
            self.cambiado = True
            sonido.tocar("muerte")
            return "R.I.P."
        if self.etapa == BEBE and self.edad >= CRECE:
            self.etapa = ADULTO
            self.forma = self.forma_adulta()
            self.cambiado = True
            sonido.tocar("nacer")
            return "ES %s!" % self.forma.upper()
        return None

    def _vigilar_llamada(self, minutos):
        if not self.pide_atencion():
            self.t_llamada = 0.0
            return
        antes = self.t_llamada
        self.t_llamada += minutos
        if antes < LLAMADA <= self.t_llamada:
            self.errores += 1          # una llamada ignorada = un error, una sola vez
            self.cambiado = True
