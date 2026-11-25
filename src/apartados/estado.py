# estado.py — los numeros del bichito, en dos paginas. A cambia de pagina.
NOMBRE = "ESTADO"
SIEMPRE = True

pagina = 0


def empezar(bicho):
    global pagina
    pagina = 0


def tecla(bicho, t):
    global pagina
    if t == "a" and pagina == 0:
        pagina = 1
        return False
    return True                 # cualquier otra tecla sale


def dibujar(fb, bicho):
    if pagina == 0:
        fb.text("HAMBRE    %3d" % int(bicho.hambre), 0, 0)
        fb.text("FELICIDAD %3d" % int(bicho.felicidad), 0, 10)
        fb.text("ENERGIA   %3d" % int(bicho.energia), 0, 20)
        fb.text("SALUD     %3d" % int(bicho.salud), 0, 30)
        fb.text("EDAD %dd %dh" % (int(bicho.edad // 1440), int(bicho.edad // 60) % 24), 0, 40)
        fb.text("A: mas", 0, 54)
    else:
        fb.text("ETAPA " + bicho.etapa.upper(), 0, 0)
        fb.text("FORMA " + bicho.figura().upper(), 0, 10)
        fb.text("ENFERMO" if bicho.enfermo else "SANO", 0, 20)
        fb.text("ERRORES %d" % bicho.errores, 0, 30)
        fb.text("DUELOS %d-%d" % (bicho.victorias, bicho.derrotas), 0, 40)
        fb.text("C: salir", 0, 54)
