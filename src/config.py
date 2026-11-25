# config.py — todo lo que cambia de una placa a otra vive aqui.
# El resto del codigo solo lee estas constantes.

# --- Tiempo ----------------------------------------------------------------
ESCALA = 60            # 1 s real = ESCALA s en la vida del bichito.
                       #   60 -> 1 minuto por segundo: hace caca cada 90 s y,
                       #         si lo abandonas, muere en unos 8 minutos.
                       #   1  -> tiempo real: una mascota de verdad.
TICK_MS = 50           # cada cuanto avanza el juego (20 veces por segundo)
DIBUJAR_MS = 50        # cada cuanto se redibuja la pantalla (20 fps)
GUARDAR_CADA_S = 60    # autoguardado en la flash
ARCHIVO = "bicho.json"

# --- Intro ------------------------------------------------------------------
INTRO_AL_PRENDER = False   # True: al prender sale el INTRO (Hola!, guino y video)
                           # y luego el menu. Tambien esta en el menu: INTRO.

# --- Pantalla OLED SSD1306 128x64 por I2C ----------------------------------
PIN_SDA = 3            # protoboard de 170 puntos: la OLED va directo sobre G3/G4
PIN_SCL = 4
OLED_FREQ = 800000     # si ves basura en la pantalla, baja a 400000
OLED_GIRADA = True     # True si la pantalla quedo de cabeza (pines hacia abajo)

# --- Botones: (tecla, GPIO). Cada boton une su pin con GND -----------------
BOTONES = (
    ("a", 0),          # A: abrir menu / siguiente
    ("b", 1),          # B: aceptar
    ("c", 10),         # C: cancelar (tercer boton de la protoboard). Sin el
                       # tercer boton, usa 9: el boton BOOT de la placa.
)

# --- Piezo ------------------------------------------------------------------
PIN_PIEZO = 7          # None = sin sonido

# --- Radio para los duelos (ESP-NOW) ---------------------------------------
CANAL = 1              # todos los bichitos del salon en el mismo canal
TXPOWER = 8.5          # dBm. La C3 SuperMini se reinicia a plena potencia.

# --- Protoboard de 170 puntos (docs/cableado_protoboard170.md) -------------
# Ahi la OLED se enchufa directo sobre las tiras del C3. Para esa placa usa:
#   PIN_SDA, PIN_SCL = 3, 4
#   OLED_GIRADA = True
#   BOTONES = (("a", 0), ("b", 1), ("c", 10))
#   PIN_PIEZO = 7
#
# Pines de la ESP32-C3 SuperMini: evita el 2, 8 y 9 para cosas nuevas (el chip
# los lee al arrancar; el 9 ya trae el boton BOOT y el 8 el LED azul).
