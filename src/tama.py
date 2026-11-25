# tama.py — el punto de entrada: prende el hardware y corre el bucle.
#
#   mpremote run src/tama.py        (o, con main.py en la placa, arranca solo)
#
# El bucle NUNCA se detiene a esperar: en cada vuelta revisa si ya toca
# avanzar el juego, dibujar o guardar, y si no, sigue. Asi los botones
# responden al instante aunque la pantalla tarde en refrescarse.
from time import ticks_ms, ticks_diff, sleep_ms
import config
import pantalla
import botones
import sonido
import memoria
import juego

pantalla.iniciar()
botones.iniciar()
sonido.iniciar()
juego.empezar(memoria.cargar())
if config.INTRO_AL_PRENDER:
    from apartados import intro
    juego.abrir(intro)
print("Bichito listo")

t_juego = t_dibujo = t_guardado = ticks_ms()

while True:
    ahora = ticks_ms()

    if ticks_diff(ahora, t_juego) >= config.TICK_MS:
        t_juego = ahora
        t = botones.revisar()
        if t:
            juego.tecla(t)
        juego.paso(config.TICK_MS)

    if ticks_diff(ahora, t_dibujo) >= config.DIBUJAR_MS:
        t_dibujo = ahora
        juego.dibujar(pantalla.fb)
        pantalla.mostrar()

    # Guardar cuando algo cambio (pero no mas de una vez cada 2 s: la flash
    # se gasta) y de todos modos cada GUARDAR_CADA_S.
    desde = ticks_diff(ahora, t_guardado)
    if (juego.bicho.cambiado and desde > 2000) or desde > config.GUARDAR_CADA_S * 1000:
        t_guardado = ahora
        juego.bicho.cambiado = False
        memoria.guardar(juego.bicho.para_guardar())

    sonido.atender()
    sleep_ms(2)               # dejar respirar al sistema
