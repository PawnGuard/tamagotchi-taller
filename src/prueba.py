# prueba.py — revisa que el hardware este bien conectado, paso a paso.
#
#   mpremote run src/prueba.py
#
# 1. La pantalla: si ves "HOLA", la OLED y el I2C funcionan.
# 2. El piezo: suena una escala.
# 3. Los botones: la pantalla te pide cada uno y espera (sin prisa) a que
#    lo aprietes. Cada vez que detecta uno, pita.
# Si algo falla, el mensaje en la consola dice que revisar.
from machine import Pin
from time import sleep_ms
import config
import pantalla
import botones
import sonido

fb = pantalla.fb


def mostrar(*renglones):
    fb.fill(0)
    for i, r in enumerate(renglones):
        fb.text(r, 0, i * 12)
    pantalla.mostrar()


def tocar_y_esperar(nombre):
    sonido.tocar(nombre)
    for _ in range(300):
        sonido.atender()
        sleep_ms(5)


print("1) Pantalla")
try:
    pantalla.iniciar()
    mostrar("HOLA", "", "La pantalla", "funciona :)")
    print("   OK: si ves HOLA en la OLED, el I2C funciona")
except OSError as e:
    print("   FALLA:", e)
    print("   Revisa SDA=GPIO%d, SCL=GPIO%d, VCC a 3V3 y GND." % (config.PIN_SDA, config.PIN_SCL))
    print("   Si SDA y SCL estan al reves, intercambialos en config.py.")
    raise SystemExit

print("2) Piezo")
sonido.iniciar()
mostrar("Escuchas una", "escala?", "", "(piezo en GPIO%d)" % config.PIN_PIEZO)
tocar_y_esperar("ganar")
print("   Si no sono: revisa el cable del piezo al GPIO%d y a GND." % config.PIN_PIEZO)

print("3) Botones")
botones.iniciar()
for tecla, gpio in config.BOTONES:
    if Pin(gpio, Pin.IN, Pin.PULL_UP).value() == 0:
        print("   OJO: %s (GPIO%d) se lee apretado sin tocarlo:" % (tecla.upper(), gpio))
        print("        el boton esta girado 90 grados o hay un corto a GND.")
for tecla, gpio in config.BOTONES:
    mostrar("Aprieta el", "boton %s" % tecla.upper(), "", "(GPIO%d)" % gpio)
    print("   Esperando el boton %s (GPIO%d)..." % (tecla.upper(), gpio))
    while botones.revisar() != tecla:
        sleep_ms(10)
    print("   OK:", tecla.upper())
    tocar_y_esperar("comer")

mostrar("TODO BIEN!", "", "Ahora corre:", "tama.py")
tocar_y_esperar("nacer")
print("Listo: todo el hardware responde.")
