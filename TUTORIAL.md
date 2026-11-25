# Taller: Bichito — una mascota virtual en MicroPython con ESP32-C3

> Material del taller universitario. Duración: una sesión de 3 h. Nivel: sabes
> programar en Python; no hace falta experiencia con microcontroladores.

---

## 0. Qué vamos a construir

Una mascota virtual estilo Tamagotchi que vive dentro de una ESP32-C3. Es un
fantasmita de sábana que nace de un huevo, tiene hambre, se aburre, se cansa,
hace caca, se enferma, crece y, si lo descuidas, se muere. Según cómo lo críes,
de adulto se convierte en **bicho**, **ángel**, **diablo** o, si además es buen
duelista, en **hacker**. Puedes jugar Pong con él y retar a los bichitos de tus
compañeros a piedra, papel o tijera por radio.

Se dibuja en una OLED de 128×64 píxeles y se controla con tres botones:

```
 H [████░░]  F [█████░]  E [███░░░]     <- barras: hambre, felicidad, energía

          !      ▄███▄       Zz         <- "!" = pide algo · "Zz" = dormido
                ███████
                █ ▀ ▀ █                 <- el fantasmita (de adulto, al doble)
                ███████          ▄  ▄
                █▀█▀█▀█         ██▄ ██▄ <- cacas pendientes (hasta 3)
 ┌──────────────────────────────────┐
 │             <COMER>              │   <- en el menú: la opción elegida
 └──────────────────────────────────┘
```

Lo importante del taller no es el hardware. La pantalla y los botones son la
excusa para aprender ideas que aparecen en cualquier sistema embebido serio:

| Concepto | Dónde se ve |
|---|---|
| **Módulos con un contrato** | `apartados/`: cada opción del menú es un archivo que cumple unas reglas |
| Bucle principal **no bloqueante** | `tama.py`: nada se queda esperando, todo se reparte por tiempo |
| **Máquinas de estados** | `juego.py` (pantallas), `bicho.py` (etapas de vida), `duelo.py` (el duelo) |
| **Separar la lógica del hardware** | `bicho.py`, `juego.py` y `duelo.py` no tocan pines: se prueban en la PC |
| **Persistencia con escritura atómica** | `memoria.py`: si se va la luz, nunca queda un archivo a medias |
| **Esquema de compromiso** (commit-reveal) | `duelo.py`: nadie puede ver tu mano antes de mostrar la suya |

Y uno transversal: **probar la lógica en la PC sin placa** (`tests/`).

### Plan de la sesión (3 h)

| Tiempo | Qué se hace | Secciones |
|---|---|---|
| 0:00 – 0:30 | conectar Thonny, armar el circuito, autodiagnóstico | 1 a 4 |
| 0:30 – 1:00 | subir el código, jugar, el mapa del código | 5 y 6 |
| 1:00 – 1:45 | apartados: **ejercicio 1** y **ejercicio 2** | 7 y 8 |
| 1:45 – 2:30 | duelos por radio con commit-reveal | 13 |
| 2:30 – 3:00 | autoarranque, tu propio video, retos | 5, 15 |

Las secciones 9 a 12 y 14 (el modelo, las pantallas, el bucle, la persistencia
y las pruebas) son para seguir en casa.

---|---|---|
| 1. Hardware | armar, instalar MicroPython, autodiagnóstico, jugar, **ejercicio 1** | 1 a 7.3 |
| 2. Lógica | apartados, dibujo, el modelo y la crianza, pantallas, bucle, pruebas, **ejercicio 2** | 7.4 a 11, 14 |
| 3. Ciberseguridad y cierre | persistencia, duelos con commit-reveal, autoarranque, retos | 12, 13, 15 |

---

## 1. Materiales

El kit (es tuyo):

- ESP32-C3 SuperMini (USB-C), ya con MicroPython.
- Pantalla OLED 0.96" SSD1306 de 128×64, I²C (4 pines).
- Protoboard de 170 puntos.
- 3 pulsadores.
- Un piezo (zumbador pasivo).
- Cables puente.

Lo que traes tú:

- Una laptop con Windows, macOS o Linux y [Thonny](https://thonny.org).
- Un cable USB-C **de datos** (muchos cables baratos solo cargan). Si con ese
  cable puedes pasar archivos de tu celular a la laptop, sirve.

No hace falta ninguna resistencia: los botones usan el pull-up interno del
microcontrolador.

---

## 2. Preparar la computadora

### Opción A: Thonny (la del taller)

1. Instala [Thonny](https://thonny.org).
2. Conecta la placa por USB.
3. **Herramientas → Opciones → Intérprete** (*Tools → Options → Interpreter*):
   elige **MicroPython (ESP32)** y el puerto de la placa (`COM3`… en Windows,
   `/dev/cu.usbmodem…` en macOS, `/dev/ttyACM0` en Linux).
4. En la consola de abajo debe salir `>>>`. Si no, aprieta **Stop**.
5. Abre **Ver → Archivos** (*View → Files*): arriba ves tu computadora y abajo
   la placa.

Con Thonny:

| Para | Haz |
|---|---|
| subir código | selecciona los `.py` de `src/` y la carpeta `apartados`, clic derecho → **Subir a /** |
| correr un archivo | ábrelo y dale **Ejecutar** (F5) |
| pararlo | **Stop** (Ctrl+F2) |
| borrar un archivo de la placa | clic derecho sobre él (abajo) → **Borrar** |

En el resto de la guía los comandos vienen en la versión de terminal
(`mpremote`, opción B). En Thonny, cada uno tiene su equivalente en la tabla.

### Opción B: terminal (`mpremote`)

```bash
pipx install esptool mpremote
```

(si no tienes `pipx`: `pip install --user esptool mpremote`)

En Linux, tu usuario necesita permiso para usar el puerto serie:

```bash
sudo usermod -aG dialout $USER
```

y luego **cierra sesión y vuelve a entrar** para que aplique.

Comprueba que las herramientas responden:

```bash
esptool version
```

```bash
mpremote --version
```

---

## 3. Instalar MicroPython

> **En el taller tu placa ya viene con MicroPython.** Esta sección es para el
> staff o para una placa nueva.

Las placas vienen **sin firmware**. Si conectas una nueva, el puerto escupe
`invalid header: 0xffffffff` y `mpremote` falla con `Errno 5` aunque
`mpremote devs` sí la liste. No es el cableado: falta MicroPython.

Conecta la placa. En Linux aparece como `/dev/ttyACM0` (la C3 usa USB nativo,
no un chip USB-serie). Si no aparece nada, prueba otro cable: casi siempre es
el cable. Luego, desde la carpeta del proyecto:

```bash
./flashear.sh
```

El script descarga el firmware si no está (`ESP32_GENERIC_C3-20260824-v1.29.0.bin`),
borra la flash, graba MicroPython, verifica que responde y sube el proyecto.
Si tienes varias placas conectadas, pásale el puerto: `./flashear.sh /dev/ttyACM1`.

Si `esptool` no detecta la placa, ponla en modo de descarga: **mantén apretado
BOOT, toca RESET y suelta BOOT** (o conecta el USB con BOOT apretado).

> Lo que hace el script, a mano (la dirección es `0x0`; `0x1000` es del ESP32
> clásico):
>
> ```bash
> esptool --chip esp32c3 --port /dev/ttyACM0 erase-flash
> esptool --chip esp32c3 --port /dev/ttyACM0 --baud 460800 write-flash 0x0 ESP32_GENERIC_C3-20260824-v1.29.0.bin
> ```

---

## 4. Conectar el hardware y probarlo

Sigue el diagrama de [docs/cableado_protoboard170.md](docs/cableado_protoboard170.md).
La OLED se enchufa directo sobre la placa, sin cables, y la imagen se voltea
por software (`OLED_GIRADA = True`). Los pines viven en `src/config.py`:

| Componente | Pin del componente | GPIO de la C3 |
|---|---|---|
| OLED | SDA | 3 |
| OLED | SCL | 4 |
| OLED | VCC | 3V3 |
| OLED | GND | GND |
| Botón A | une el GPIO con GND | 0 |
| Botón B | ídem | 1 |
| Botón C | ídem | 10 |
| Piezo | una pata al GPIO, la otra a GND | 7 |

**No uses los GPIO 2, 8 ni 9 para cosas nuevas.** Son *strapping pins*: el
chip los lee al arrancar para decidir cómo arranca. El 9 ya trae el botón BOOT
(por eso, si lo mantienes apretado al conectar el USB, la placa entra en modo
de descarga y parece muerta) y el 8 trae el LED azul.

### El autodiagnóstico: `prueba.py`

Antes de jugar, revisa que todo esté bien conectado. `prueba.py` importa
`config.py`, `pantalla.py`, `botones.py` y `sonido.py` **de la placa**, así que
primero sube el código (si usaste `flashear.sh`, ya está arriba):

```bash
./subir.sh
```

```bash
mpremote run src/prueba.py
```

Va paso a paso:

1. **Pantalla.** La consola imprime los dispositivos I²C que encontró (debe
   salir `0x3c`) y la OLED muestra "HOLA". Si falla, te dice qué GPIO revisar y
   que, si SDA y SCL están al revés, los intercambies en `config.py`.
2. **Piezo.** Suena una escala. Si no suena, revisa el cable al GPIO 7 y a GND.
3. **Botones.** Primero avisa si algún botón se lee apretado sin tocarlo (está
   girado 90° o hay un corto a GND). Luego la pantalla te pide cada botón y
   espera sin prisa a que lo aprietes; cada vez que lo detecta, pita.

Al final sale "TODO BIEN!".

---

## 5. Subir el código y jugar

### Subir

```bash
./subir.sh
```

`subir.sh` encuentra el puerto `/dev/ttyACM*` solo (o se lo dices:
`./subir.sh /dev/ttyACM1`), borra los `.py` que había en la placa (menos
`boot.py` y `main.py`), copia `src/*.py` y la carpeta `src/apartados/`, y
reinicia la placa. **No borra la mascota guardada** (`bicho.json`).

Cada vez que cambies algo, vuelve a correr `./subir.sh`. Antes, corre las
pruebas en la PC (sección 14): ahorran viajes a la placa.

Cierra cualquier monitor serie (Arduino IDE, VS Code) antes de subir: solo un
programa puede usar el puerto a la vez.

### Correr

Desde la PC (así ves los `print` y lo cortas con `Ctrl-C`):

```bash
mpremote run src/tama.py
```

### Cómo se juega

| Dónde estás | A | B | C |
|---|---|---|---|
| Casa | abre el menú | — | — |
| Menú | siguiente opción | elegir | volver a casa |
| Dentro de una opción | depende de la opción | depende | casi siempre sale |
| Un aviso abajo | lo quita | lo quita | lo quita |
| Muerto (R.I.P.) | — | huevo nuevo | — |

El menú:

| Opción | Qué hace |
|---|---|
| COMER | hambre +30 ("NAM NAM"; si ya está lleno, "LLENO!") |
| LIMPIAR | recoge las cacas |
| CURAR | si está enfermo lo cura, pero la medicina sabe feo: felicidad −10 |
| JUGAR | Pong contra la CPU (necesita energía ≥ 15) |
| AMIGOS | duelos de piedra, papel o tijera por radio |
| SALUDAR | **ejercicio 1** |
| *(vacío)* | **ejercicio 2**: la opción sin nombre |
| LUZ | apagar la luz lo duerme; se puede usar aunque esté dormido |
| ESTADO | sus números, en dos páginas (A pasa de página) |
| VIDEO | tu propio video (sección 15); sin video dice "SIN VIDEO" |
| INTRO | "Hola!" en grande y el fantasmita guiñando el ojo |

Con el bichito en el huevo, el menú responde "AUN NO NACE"; dormido, responde
"ZZZ...". Solo LUZ y ESTADO funcionan siempre.

Con `ESCALA = 60` (el valor del taller), un segundo real es un minuto en la
vida del bichito: nace a los 30 s, hace caca cada 90 s, se vuelve adulto a los
24 min y, si lo abandonas, muere en unos 6 min. Mientras estás dentro de una
opción del menú, su tiempo se detiene.

### Que arranque solo al encender

Cuando tu bichito esté terminado:

```bash
mpremote cp autoarranque/main.py :
```

MicroPython ejecuta `main.py` al encender, y `main.py` solo hace `import tama`.
Para volver a desarrollar:

```bash
mpremote rm :main.py
```

### Empezar con un huevo nuevo

```bash
mpremote rm :bicho.json
```

---

## 6. El mapa del código

```
src/
├── tama.py          punto de entrada: prende el hardware y corre el bucle
├── config.py        lo que cambia de placa a placa: pines, escala de tiempo, radio
│
├── bicho.py         EL MODELO: necesidades, etapas de vida, crianza
├── juego.py         las pantallas (CASA / MENU / APARTADO) y a dónde lleva cada botón
├── menu.py          qué apartados hay en el menú y en qué orden
├── apartados/       una opción del menú = un archivo
│   ├── __init__.py  el contrato: qué puede tener un apartado
│   ├── comer.py  limpiar.py  curar.py  luz.py      acciones rápidas
│   ├── estado.py    los números del bichito
│   ├── jugar.py     Pong contra la CPU
│   ├── amigos.py    duelos por radio
│   ├── saludar.py   EJERCICIO 1
│   └── sin_nombre.py EJERCICIO 2
├── dibujo.py        atajos para dibujar: texto centrado, barras, el bichito, la casa
├── sprites.py       los dibujos, hechos con texto ('#' y '.')
├── duelo.py         el protocolo del duelo, con commit-reveal
│
├── pantalla.py      la OLED SSD1306 por I²C
├── botones.py       A, B y C con antirrebote, sin bloquear
├── sonido.py        melodías en el piezo, sin bloquear
├── radio.py         ESP-NOW (solo encendida dentro de AMIGOS)
├── memoria.py       guardar y cargar en la flash con escritura atómica
└── prueba.py        autodiagnóstico del hardware

tests/               pruebas en la PC, sin placa
autoarranque/main.py hace que el bichito arranque solo al encender
```

Son tres capas:

- **Hardware**: `pantalla.py`, `botones.py`, `sonido.py`, `radio.py` y
  `memoria.py`. Son los únicos que hablan con pines, radio o flash.
- **Lógica**: `bicho.py`, `juego.py`, `duelo.py`, `dibujo.py`, `sprites.py` y
  los apartados. No prenden nada. Por eso corren en la PC.
- **Pegamento**: `tama.py` prende el hardware y en cada vuelta del bucle le
  pasa a la lógica lo que pasó.

`juego.py` expone solo cuatro funciones, y `tama.py` no necesita más:

```python
juego.empezar(guardado)   # arranca con lo guardado, o con un huevo nuevo si es None
juego.tecla(t)            # se apreto "a", "b" o "c"
juego.paso(ms)            # pasaron ms milisegundos
juego.dibujar(fb)         # pinta la pantalla en un FrameBuffer de 128x64
```

El camino de los datos:

```
 botones.revisar() ──▶ juego.tecla(t) ──▶ apartado.tecla(bicho, t)
                       juego.paso(ms) ──▶ bicho.vivir(minutos)   (en casa o en el menú)
                                      └─▶ apartado.paso(bicho, ms) (dentro de un apartado)

 pantalla.mostrar() ◀── juego.dibujar(fb) ◀── dibujo.casa(...) o apartado.dibujar(fb, bicho)

 memoria.guardar(bicho.para_guardar())   cuando algo cambió
```

> **¿Y el sonido?** `bicho.py` llama `sonido.tocar("nacer")`, pero eso no toca
> hardware: `tocar()` solo deja la melodía en una fila. El PWM se crea en
> `sonido.iniciar()`, que solo llama `tama.py`. En la PC nadie lo llama, así que
> no suena nada, y `sonido.ultima` recuerda qué se pidió para que las pruebas lo
> revisen.

---

## 7. Los apartados: cada opción del menú es un archivo

Esta es la parte del código que vas a tocar. Cada opción del menú es un archivo
en `src/apartados/`, y `menu.py` es solo la lista:

```python
from apartados import comer, limpiar, curar, jugar, amigos, saludar, sin_nombre, luz, estado

MENU = (
    comer,
    limpiar,
    curar,
    jugar,
    amigos,
    saludar,
    sin_nombre,
    luz,
    estado,
)
```

Agregar una opción no obliga a tocar `juego.py`: basta con escribir un archivo
que cumpla el contrato y ponerlo en la lista.

### 7.1 El contrato

Está escrito en `apartados/__init__.py`. Un apartado es un módulo que puede
tener estas cosas (solo `NOMBRE` y `empezar` son obligatorias):

| Qué | Para qué |
|---|---|
| `NOMBRE = "COMER"` | lo que sale en el menú (máximo 13 letras) |
| `SIEMPRE = True` | también funciona con el bichito dormido o en el huevo |
| `empezar(bicho)` | se llama al elegirlo. Si **devuelve un texto**, el texto sale abajo un momento y listo (acción rápida). Si **no devuelve nada**, el apartado se queda en pantalla |
| `tecla(bicho, t)` | se apretó un botón (`"a"`, `"b"` o `"c"`). Devuelve `True` para salir. Si no la escribes, C te saca |
| `paso(bicho, ms)` | se llama 20 veces por segundo; `ms` es el tiempo que pasó. Devuelve `True` para salir |
| `dibujar(fb, bicho)` | pinta la pantalla (ya viene borrada). Si no la escribes, sale el bichito con el `NOMBRE` abajo |
| `terminar(bicho)` | se llama al salir, para dejar todo en orden. Si devuelve un texto, sale abajo un momento |

`bicho` es el bichito (sección 9): `bicho.hambre`, `bicho.felicidad`,
`bicho.energia` y `bicho.salud` van de 0 a 100, `bicho.caca` de 0 a 3, y hay
`bicho.enfermo`, `bicho.luz`, etc. Puedes cambiarlos directamente: si te pasas
de 100 o de 0, se corrige solo.

Así usan el contrato los apartados que ya vienen:

| Archivo | NOMBRE | Tipo | Funciones |
|---|---|---|---|
| `comer.py`, `limpiar.py`, `curar.py` | COMER, LIMPIAR, CURAR | acción rápida | `empezar` |
| `luz.py` | LUZ | acción rápida, `SIEMPRE` | `empezar` |
| `estado.py` | ESTADO | se queda, `SIEMPRE` | `empezar`, `tecla`, `dibujar` |
| `saludar.py` | SALUDAR | se queda | `empezar`, `tecla`, `dibujar` |
| `sin_nombre.py` | *(vacío)* | se queda | `empezar`, `paso`, `tecla`, `dibujar` |
| `jugar.py` | JUGAR | se queda (o "CANSADO..." si no tiene energía) | todas |
| `amigos.py` | AMIGOS | se queda | `empezar`, `paso`, `tecla`, `terminar`, `dibujar` |

### 7.2 Una acción rápida: `comer.py`

El apartado más chico posible:

```python
# comer.py — una accion rapida: cambia al bichito y devuelve un texto.
import sonido

NOMBRE = "COMER"


def empezar(bicho):
    if bicho.hambre >= 100:
        return "LLENO!"
    bicho.hambre += 30
    sonido.tocar("comer")
    return "NAM NAM"
```

Si el hambre estaba en 95, después de `+= 30` queda en 125, pero `juego.py`
llama `bicho.limitar()` justo después y la deja en 100. El apartado no tiene
que preocuparse por eso.

### 7.3 Ejercicio 1: `saludar.py`

Así viene: al elegir SALUDAR, abajo de la pantalla sale "Saludando" y no se
quita hasta que aprietas C.

```python
import dibujo

NOMBRE = "SALUDAR"


def empezar(bicho):
    pass                        # no devuelve texto: se queda en pantalla


def tecla(bicho, t):
    return t == "c"             # True = salir. Solo C lo quita.


def dibujar(fb, bicho):
    dibujo.casa(fb, bicho, "Saludando")
```

Tres funciones, tres decisiones:

- `empezar` no devuelve nada, así que el apartado **se queda** en pantalla (si
  devolviera `"HOLA"`, sería una acción rápida como COMER).
- `tecla` devuelve `True` solo con C. A y B no hacen nada.
- `dibujar` reutiliza la pantalla de casa (`dibujo.casa`) con otro texto abajo.

Primero comprueba que funciona en la PC:

```bash
python3 -m unittest discover -s tests -k Saludar -v
```

Las tres pruebas de `class Saludar` en `tests/test_juego.py` revisan
exactamente lo que dice el ejercicio: que sale "Saludando", que A y B no lo
quitan y que C sí.

Luego hazlo tuyo. Ideas (vienen en el archivo):

- Que salude con un sonido al empezar: `sonido.tocar("nacer")`.
- Que saludar lo ponga contento: `bicho.felicidad += 10`.
- Que ponga cara feliz mientras saluda: `dibujo.bichito(fb, bicho, "feliz")`.
- Que A cambie el texto por otro saludo ("Hola!", "Que onda!"...).
- Que se canse si saluda mucho rato (usa `paso(bicho, ms)` para contar).

Para cada idea, piensa primero **en qué función va**: lo que pasa una vez al
entrar va en `empezar`, lo que responde a un botón en `tecla`, lo que depende
del tiempo en `paso` y lo que se ve en `dibujar`.

### 7.4 Ejercicio 2: `sin_nombre.py`

Este apartado es tuyo. Así viene: el bichito sale sonriendo y abajo aparecen
tres puntos que se van llenando ( .  ..  ... ), como si estuviera pensando. C
lo quita. En el menú sale vacío (`<>`), porque todavía no tiene nombre.

```python
import dibujo

NOMBRE = ""

PUNTOS_MS = 400                 # cada cuanto aparece un punto mas

tiempo = 0                      # ms que lleva abierto este apartado


def empezar(bicho):
    global tiempo
    tiempo = 0                  # no devuelve texto: se queda en pantalla


def paso(bicho, ms):
    global tiempo
    tiempo += ms


def tecla(bicho, t):
    return t == "c"


def dibujar(fb, bicho):
    dibujo.bichito(fb, bicho, "feliz")
    puntos = (tiempo // PUNTOS_MS) % 4          # 0, 1, 2, 3, 0, 1, 2, 3...
    for i in range(puntos):
        fb.fill_rect(54 + i * 8, 54, 4, 4, 1)  # cuadritos de 4x4 en fila
```

Lo nuevo respecto a SALUDAR es `paso`: el apartado lleva su propio reloj
(`tiempo`) y `dibujar` decide qué mostrar según ese reloj. Así se anima algo
**sin `sleep()`**: `dibujar` nunca espera, solo pregunta "¿cuánto tiempo
llevo?" y pinta lo que toca. Es la misma idea que el bucle principal (sección
11) en chiquito.

Para empezar:

1. Ponle nombre: `NOMBRE = "PENSAR"`.
2. Decide qué hace. Ideas:
   - Que piense un número al azar y tú lo adivines con A y B.
   - Que cuente cuántas veces apretaste A.
   - Que los puntos vayan más rápido o más lento (cambia `PUNTOS_MS`).
   - Que al terminar de pensar diga algo con `sonido.tocar(...)`.

Las pruebas de `class SinNombre` en `tests/test_juego.py` describen el punto
de partida: nombre en blanco, bichito sonriendo y puntos que cuentan
0, 1, 2, 3, 0, 1, 2, 3. **Cuando le pongas nombre, `test_el_nombre_esta_en_blanco`
va a fallar, y es lo esperado**: cambiaste el comportamiento, así que cambia
también la prueba para que diga lo que ahora hace tu apartado (sección 14).

```bash
python3 -m unittest discover -s tests -k SinNombre -v
```

### 7.5 Crear un apartado nuevo

1. Copia `apartados/sin_nombre.py` con otro nombre, por ejemplo `bailar.py`, y
   ponle su `NOMBRE`.
2. Agrégalo a `menu.py`: en el `import` y en la lista `MENU`, en el lugar
   donde quieras que salga.
3. Corre las pruebas:

   ```bash
   python3 -m unittest discover -s tests
   ```

   La prueba `Contrato` de `tests/test_juego.py` recorre **todos** los
   apartados del menú: revisa que `NOMBRE` sea texto de 13 letras o menos, que
   se abra, que aguante medio segundo de `paso` sin tronar, que se dibuje y que
   C lo saque. Si tu apartado no cumple, el mensaje dice cuál es.
4. `./subir.sh` y pruébalo en la placa.

### 7.6 Lo que `juego.py` hace por ti

Para que los apartados sean cortos, `juego.py` se encarga de lo que se repite:

- **Al abrir** (`_abrir`): si el apartado no tiene `SIEMPRE = True`, no lo deja
  entrar con el bichito en el huevo ("AUN NO NACE") ni dormido ("ZZZ..."). Luego
  llama `empezar`; si devolvió texto, lo muestra y se queda en el menú.
- **Después de cada llamada** (`_llamar`): corrige las barras con
  `bicho.limitar()`, y si el bichito murió, cierra el apartado. Después de
  `empezar` y de `tecla` marca `bicho.cambiado = True` para que se guarde;
  después de `paso` no (se llama 20 veces por segundo). Si cambias al bichito
  dentro de `paso`, pon tú `bicho.cambiado = True`, como hace `amigos.py`.
- **Al cerrar** (`_cerrar`): llama `terminar` si existe, muestra su texto y
  regresa al menú.
- **El tiempo se detiene** dentro de un apartado: mientras estás ahí,
  `juego.paso` no llama `bicho.vivir`. Con `ESCALA = 60`, un Pong de dos minutos
  serían dos horas de hambre.

### 7.7 Un apartado completo: `jugar.py`

`jugar.py` usa todo el contrato. Sirve de ejemplo para algo más grande:

- `empezar` decide: si la energía es menor que 15, devuelve "CANSADO..." (y
  entonces se comporta como acción rápida); si no, crea la partida.
- `paso` mueve la física. Lee `botones.apretados` (los botones que **siguen**
  apretados) para mover la paleta mientras mantienes A o B, y sale si alguien
  llegó a 5 puntos o si mantuviste B 5 segundos.
- `terminar` da los premios y el costo: felicidad +5 por cada punto que
  metiste, +10 si ganaste, energía −10 y hambre −5.
- `dibujar` pinta el marcador, la red, las paletas y la bola.

La física está en píxeles por segundo, no por llamada: `s = ms / 1000` y
`self.bx += self.vx * s`. Así no cambia si mañana `paso` se llama más seguido.
La paleta de la CPU es más rápida cuanto más feliz está el bichito
(`Pong(nivel=bicho.felicidad)`).

---

## 8. Dibujar: `dibujo.py` y `sprites.py`

### Un framebuffer es solo memoria

Todo lo que se ve va a parar a un `bytearray` de 1024 bytes que vive en la RAM:
128 × 64 píxeles ÷ 8 píxeles por byte. `framebuf.FrameBuffer` da funciones para
dibujar en él, y `pantalla.mostrar()` manda esos 1024 bytes a la OLED de un
jalón. Dibujar en RAM es rápido; mandar por I²C tarda unos 14 ms, por eso se
hace una sola vez por cuadro.

El formato es `MONO_VLSB`: cada byte es una columna vertical de 8 píxeles, con
el bit 0 arriba. Es el formato nativo del controlador SSD1306, así que el
buffer viaja tal cual, sin conversión.

Lo básico de MicroPython (el `fb` que recibe `dibujar`):

```python
fb.fill(0)                    # borrar todo
fb.text("HOLA", x, y)         # texto (cada letra mide 8x8 pixeles)
fb.pixel(x, y, 1)             # un pixel
fb.rect(x, y, ancho, alto, 1) # rectangulo (fill_rect: relleno)
fb.blit(imagen, x, y)         # pegar un sprite
```

Las coordenadas empiezan arriba a la izquierda, en (0, 0). La pantalla mide 128
de ancho por 64 de alto, así que caben 16 letras por renglón y 8 renglones.

### Los atajos de `dibujo.py`

| Función | Qué hace |
|---|---|
| `dibujo.centrado(fb, texto, y)` | texto centrado a lo ancho |
| `dibujo.barra(fb, x, y, ancho, porcentaje)` | una barra como las de arriba |
| `dibujo.bichito(fb, bicho, cara=None, x=None, y=None)` | el bichito; sin `cara` pone la de su ánimo, sin `x` ni `y` queda centrado; de adulto sale al doble |
| `dibujo.casa(fb, bicho, abajo=None, recuadro=False)` | la pantalla normal completa, con un texto abajo |
| `dibujo.cuadro()` | un contador que sube cada 450 ms: sirve para animar |

`dibujo.bichito` ya anima solo: el bichito flota (sube y baja), a ratos
parpadea y el huevo se tambalea. Todo sale de `cuadro()`, que a su vez
sale de `dibujo.reloj`, que avanza `juego.paso`.

### Sprites como texto (`sprites.py`)

Dibujar bitmaps en hexadecimal es una tortura. En cambio, esto lo lee
cualquiera:

```python
"bebe": """
...............
...............
......###......
....#######....
...#########...
...#########...
..###########..
..###########..
.#############.
..###########..
..###########..
..###########..
..##.##.##.##..
..#..#...#..#..
...............
...............
""",
```

`'#'` es un píxel encendido y `'.'` uno apagado. El bichito se arma con dos
piezas:

- Un **cuerpo** de 15×16 en `CUERPOS`, uno por forma: `bebe`, `bicho`, `angel`
  (aureola y alitas), `diablo` (cuernitos y colita) y `hacker` (capucha).
- Una **cara** de 5×5 en `CARAS`, una por ánimo: `normal`, `parpadeo`, `feliz`,
  `triste` y `dormido`. La cara va en las columnas 5 a 9 y los renglones 3 a 7
  del cuerpo, y se pinta **invirtiendo** píxeles (`'x'`): sobre la sábana hace
  hoyos y dentro de la capucha del hacker se enciende.

`sprites.imagen(arte, escala, cara)` convierte el texto en un `FrameBuffer`
listo para `fb.blit`. Cada combinación se calcula una sola vez y se guarda, así
que llamarla en cada cuadro no cuesta nada. Trade-off clásico: un poco de
memoria a cambio de no recalcular.

También están `HUEVO`, `TUMBA`, `CACA` y las manos del duelo (`MANOS`:
piedra, papel, tijera y "duda").

**Ejercicio:** dibuja una cara nueva (por ejemplo `"enojado"`) y úsala desde un
apartado con `dibujo.bichito(fb, bicho, "enojado")`. Si una fila tiene un
carácter de más, `imagen()` te avisa con un `ValueError` que dice qué fila.
Para revisar todas las combinaciones en la PC:

```bash
python3 -c "import sys; sys.path[:0]=['tests/stubs','src']; import sprites; [sprites.bichito(f, c) for f in sprites.CUERPOS for c in sprites.CARAS]; print('ok')"
```

---

## 9. El modelo: `bicho.py`

`bicho.py` sabe qué necesita el bichito y cómo cambia con el tiempo. No toca la
pantalla ni los botones.

### 9.1 Lo que se guarda

Todo el estado del bichito está en un diccionario, `INICIO`, con su valor al
nacer:

```python
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
```

`Bicho(guardado)` copia esos campos como atributos y, si hay algo guardado,
lo pone encima. Un guardado viejo al que le falte un campo nuevo simplemente
**hereda el valor inicial**. Así puedes agregar campos sin romper las mascotas
que ya existen. `bicho.para_guardar()` hace el viaje de regreso: un diccionario
plano de números, booleanos y textos, que se guarda tal cual con `json.dump`.

Lo que no se guarda se calcula: `dormido()`, `animo()` (qué cara poner),
`pide_atencion()` (el "!") y `figura()` (qué cuerpo dibujar).

### 9.2 Las necesidades y el tiempo de juego

La decisión importante es **en qué unidad se expresan las tasas**:

```python
# Cuanto baja cada barra por minuto de juego
BAJA = {
    "hambre":    100 / 240,   # de lleno a vacio en 4 h
    "felicidad": 100 / 180,   # 3 h
    "energia":   100 / 480,   # 8 h despierto
}
```

Por minuto **de juego**, no por vuelta del bucle. Si mañana cambias `TICK_MS`
de 50 a 20, el bichito no pasa más hambre. La conversión de tiempo real a
tiempo de juego está en un solo lugar, `juego.paso`:

```python
aviso = bicho.vivir(ms / 1000 * config.ESCALA / 60)
```

`bicho.vivir(minutos)` avanza la vida y, si pasó algo que contar ("NACIO!",
"R.I.P.", "ES ANGEL!"), lo devuelve para que salga en la pantalla. Lo que hace
cada minuto:

- Las barras bajan. **Dormido**, bajan a la mitad y la energía se recarga (de 0
  a 100 en 2 h).
- Despierto, hace **caca** cada 90 minutos (hasta 3). Con 3 cacas durante 30
  minutos, **se enferma**.
- La **salud** baja si algo está en estado crítico (una barra en 0, enfermo o
  con 3 cacas) y se recupera si no. Con salud en 0, muere.

### 9.3 Las etapas de vida: una máquina de estados

```
  HUEVO ──(edad ≥ 30 min)──▶ BEBE ──(edad ≥ 24 h)──▶ ADULTO
                               │                       │
                               └────(salud = 0)────────┴──▶ MUERTO ──(B)──▶ HUEVO nuevo
```

El estado vive en `bicho.etapa` porque se guarda: si desconectas la placa, al
volver sigue en la misma etapa. En el huevo no le da hambre; muerto, ya no
cambia nada.

### 9.4 La crianza: en qué se convierte

Mientras es bebé, `bicho.py` cuenta los **errores de cuidado**. Un error es
dejarlo pidiendo algo (el "!": hambre o felicidad bajo 20, cansado, enfermo o
con 3 cacas) más de 15 minutos de juego seguidos. Cada llamada ignorada cuenta
**una sola vez**, aunque lo dejes así una hora.

Al cumplir 24 horas, `forma_adulta()` decide:

```python
def forma_adulta(self):
    """La evolucion: en que se convierte segun como lo criaste."""
    if self.errores <= ERRORES_BICHO and self.victorias >= VICTORIAS_HACKER:
        return "hacker"
    if self.errores <= ERRORES_ANGEL:
        return "angel"
    if self.errores <= ERRORES_BICHO:
        return "bicho"
    return "diablo"
```

| Forma | Cómo se consigue |
|---|---|
| hacker | 4 errores o menos **y** 5 duelos ganados o más (forma secreta) |
| ángel | 0 o 1 error |
| bicho | de 2 a 4 errores |
| diablo | 5 errores o más |

El orden de los `if` importa: hacker va primero, así que un bichito perfecto
que además ganó 5 duelos se vuelve hacker, no ángel. Como las victorias cuentan
desde bebé, la sesión de duelos (sección 13) cambia en qué se convierte.

**Ejercicio:** inventa una forma nueva. Necesitas un cuerpo en
`sprites.CUERPOS`, una regla en `forma_adulta()` y una prueba en
`tests/test_bicho.py` (mira `test_formas_adultas`).

---

## 10. Las pantallas: `juego.py`

Las pantallas también son una máquina de estados:

```
  CASA ──A──▶ MENU ──B──▶ APARTADO ──(el apartado dice que terminó)──▶ MENU
                │  ▲
                │  └──A── (siguiente opción)
                └──C──▶ CASA
```

Encima de eso hay un **aviso**: un texto que sale abajo durante 1,5 s
(`AVISO_MS`) y que cualquier tecla quita. Con el bichito muerto, B pone un
huevo nuevo.

`tecla()` es literalmente esa tabla escrita con `if`:

```python
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
```

La ventaja: lo que hace cada botón depende de **en qué pantalla estás**, sin
banderas sueltas tipo `menu_abierto = True`. Cuando alguien pregunta "¿y si
aprieto B en la casa?", la respuesta está en una sola función.

La pantalla actual vive en `juego.pantalla` y **no se guarda**: al encender,
siempre arranca en CASA. La etapa de vida sí se guarda. Distinguir qué estado
es del modelo (se guarda) y qué estado es de la interfaz (no) es una de las
decisiones de diseño más útiles del taller.

---

## 11. El bucle no bloqueante: `tama.py`

Esto es lo más importante del taller. El bucle **nunca se detiene a esperar**:

```python
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
```

Varias tareas con ritmos distintos conviven sin hilos y sin `sleep` largos:
el juego a 20 Hz (`TICK_MS = 50`), el dibujo a 20 cuadros por segundo
(`DIBUJAR_MS = 50`), el guardado cuando algo cambió y el sonido en cada vuelta.
Cada una pregunta "¿ya me toca?" y, si no, deja pasar a la siguiente.

Detalles que valen una discusión en clase:

- **`ticks_ms()` da la vuelta** cada ~12 días. Por eso se compara con
  `ticks_diff()` y no con `ahora - antes`: la resta cruda da negativo al pasar
  el límite.
- **`juego.paso(config.TICK_MS)`** le dice al juego que pasaron 50 ms, aunque
  esa vuelta haya tardado más. Si una vuelta tarda 120 ms, el bichito vive 50:
  su tiempo se atrasa un poco. ¿Cómo lo arreglarías? (pista: `ticks_add`, o
  pasarle el tiempo que de verdad pasó).
- **Guardar se gasta.** La flash aguanta un número limitado de escrituras. Por
  eso se guarda solo si algo cambió y nunca más de una vez cada 2 s, más un
  autoguardado cada minuto por si acaso.
- **`sleep_ms(2)`** al final le da aire al sistema (la radio corre en otra
  tarea y necesita que Python suelte el procesador de vez en cuando).

### Los botones (`botones.py`)

`revisar()` devuelve la tecla que **se acaba de apretar** (el flanco), o
`None`, y deja en `botones.apretados` las que siguen apretadas (el Pong lo usa
para mover la paleta). Nunca espera.

Un botón mecánico **rebota**: al apretarlo, el metal tiembla y la señal cambia
varias veces en pocos milisegundos. Sin cuidado, un solo apretón abriría y
cerraría el menú tres veces. Por eso un cambio solo cuenta si pasaron
`REBOTE_MS` (30 ms) desde el anterior:

```python
abajo = pin.value() == 0
if abajo != (tecla in apretados) and ticks_diff(ahora, _t_cambio[tecla]) > REBOTE_MS:
```

`pin.value() == 0` es "apretado" porque el pin tiene el pull-up interno: suelto
lee 1 y, al apretar, el botón lo une a GND.

### El sonido (`sonido.py`)

El mismo truco: `sonido.tocar("comer")` solo deja la melodía en una fila, y
`sonido.atender()`, que el bucle llama en cada vuelta, cambia de nota cuando ya
pasó la duración de la anterior. Una melodía de un segundo nunca detiene al
bichito. Las melodías son listas de `(frecuencia en Hz, duración en ms)` en
`MELODIAS`; frecuencia 0 es silencio.

**Anti-ejercicio:** pon `import time` y `time.sleep(1)` dentro del `paso()` de
tu apartado de la sección 7.4. Súbelo y entra. Los botones tardan en responder,
la animación brinca y el sonido se corta. Eso pasa cuando algo bloquea.
(Luego quítalo.)

---

## 12. Persistencia atómica: `memoria.py`

Una mascota que se olvida de todo al reiniciar no es una mascota. Guardamos el
bichito en la flash, en `bicho.json`. Pero la flash es lenta y una escritura se
puede interrumpir (se desconecta el USB) a la mitad: quedaría un JSON cortado y
la mascota nacería corrupta.

```python
def guardar(est):
    tmp = config.ARCHIVO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(est, f)
    try:
        os.rename(tmp, config.ARCHIVO)        # atomico en littlefs
    except OSError:                                  # FAT no pisa archivos:
        os.remove(config.ARCHIVO)             # borrar y renombrar
        os.rename(tmp, config.ARCHIVO)
```

Primero se escribe un archivo temporal completo y luego se **renombra** encima
del bueno. `rename` es atómico en littlefs (el sistema de archivos de
MicroPython en la ESP32): o queda el archivo viejo entero o el nuevo entero,
nunca uno a medias. Es la misma técnica que usan las bases de datos.

Y `cargar()` trata cualquier error como "no hay nada guardado":

```python
def cargar():
    """Devuelve el dict guardado, o None si no hay nada o esta corrupto."""
    try:
        with open(config.ARCHIVO) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None
```

En `tama.py`: `juego.empezar(memoria.cargar())`. Si no hay nada, `None` da un
huevo nuevo.

**Ejercicios:**

- En un sistema FAT, `rename` no pisa archivos y el código cae al `except`:
  borra y luego renombra. Entre esas dos líneas no hay `bicho.json`. ¿Qué pasa
  si se va la luz justo ahí? ¿Cómo lo arreglarías en `cargar()`? (pista: el
  `.tmp` sigue ahí).
- ¿Qué pasa con el tiempo que la placa estuvo apagada? Ahora, nada: el bichito
  "se congela". Diseña cómo descontarlo. La C3 no tiene reloj cuando está
  apagada: ¿qué podrías guardar? ¿Qué límite le pondrías para no matarlo de
  golpe?

---

## 13. Duelos por radio: `radio.py`, `duelo.py` y `apartados/amigos.py`

En AMIGOS, tu bichito busca a los de tus compañeros y los puede retar a
piedra, papel o tijera. Ganar alegra y suma victorias (que cuentan para la
forma hacker).

### 13.1 La radio (`radio.py`)

ESP-NOW es un protocolo de Espressif: las ESP32 se mandan paquetes cortos
directamente, sin router ni Wi-Fi. Se usa **difusión** (a `FF:FF:FF:FF:FF:FF`):
todos los bichitos en el mismo canal (`config.CANAL = 1`) oyen todo, y nadie
confirma que un paquete llegó.

- La radio **solo se prende dentro de AMIGOS** (`empezar` la enciende y
  `terminar` la apaga): escuchar todo el tiempo gasta batería.
- `config.TXPOWER = 8.5`: la C3 SuperMini se reinicia si transmite a plena
  potencia (su regulador no aguanta el pico de corriente).
- El nombre de cada bichito (`radio.mi_id()`) son los últimos 2 bytes de su
  identificador único en hexadecimal, por ejemplo `6EEC`: corto y casi único en
  un salón.

### 13.2 El problema: ¿quién muestra primero?

En persona, los dos muestran la mano al mismo tiempo. Por radio no se puede: si
yo te mando "PIEDRA" y tú contestas después, ya sabes lo que elegí y puedes
mandar "PAPEL".

### 13.3 La solución: un esquema de compromiso (commit-reveal)

Es el mismo truco que usan las subastas en línea y algunos protocolos de
blockchain:

1. Cada quien elige y manda solo una **huella**: `sha256(jugada + sal)`. La
   huella no deja adivinar la jugada, pero te **amarra** a ella.
2. Cuando ya tienes la huella del otro, revelas tu jugada y tu sal.
3. Cada quien recalcula la huella del rival. Si no coincide: **TRAMPA**.

```python
def huella(jugada, sal):
    """El compromiso: 16 caracteres hex del sha256 de la jugada con su sal."""
    h = hashlib.sha256((jugada + ":" + sal).encode()).digest()
    return binascii.hexlify(h[:8]).decode()
```

¿Por qué la **sal**? Sin ella, la huella de "piedra" sería siempre la misma: el
rival calcularía las 3 huellas posibles y sabría tu jugada al instante. La sal
es un número al azar (`os.urandom(4)`) distinto en cada duelo.

Una partida, vista desde los dos lados:

```
  Ana (A1B2)                                         Beto (C3D4)

  elige PIEDRA, sal = 9f3a1c2b
  HUELLA de "piedra:9f3a1c2b"  ──────────────────▶   la guarda; no sabe qué es
                                                     elige PAPEL, sal = 07c15e9d
                               ◀──────────────────   HUELLA de "papel:07c15e9d"
                               ◀──────────────────   REVELO papel 07c15e9d
                                                     (ya tenía la huella de Ana)
  ya tiene la huella de Beto:
  REVELO piedra 9f3a1c2b       ──────────────────▶   recalcula la huella de Ana: coincide
  recalcula la de Beto: coincide
  resultado: PERDI                                   resultado: GANE
```

Beto revela primero porque, cuando confirma su mano, ya tiene la huella de Ana.
Ana recibe la revelación de Beto, pero solo la mira después de mandar la suya.

Las reglas que lo hacen seguro (y que `tests/test_duelo.py` comprueba en
`class Seguridad`):

- **Nadie revela antes de tener la huella del otro.** Una revelación que llega
  antes de tiempo se ignora.
- Si la revelación no coincide con la huella: **TRAMPA**.
- Si el rival cambia su huella a media partida: **TRAMPA**.
- Si el rival ya vio mi mano y nunca revela la suya (porque iba a perder),
  después de 20 s sin avances: **HUYO**.

En la pantalla, mientras esperas, ves `#` y los primeros 8 caracteres de la
huella del rival: sabes que ya eligió, pero no qué.

### 13.4 Los mensajes

Texto plano, a propósito: se puede leer (y falsificar):

```
T1|de|para|tipo|datos...
```

`para = "*"` es para todos. Los tipos:

| Tipo | Ejemplo | Para qué |
|---|---|---|
| HOLA | `T1\|A1B2\|*\|HOLA\|bebe` | "aquí estoy", cada segundo, con tu forma |
| RETO | `T1\|A1B2\|C3D4\|RETO\|5e2f` | te reto; `5e2f` es el id de este duelo |
| SI / NO | `T1\|C3D4\|A1B2\|SI\|5e2f` | acepto / no quiero, o me rajo |
| HUELLA | `T1\|A1B2\|C3D4\|HUELLA\|5e2f\|<16 hex>` | mi compromiso |
| REVELO | `T1\|A1B2\|C3D4\|REVELO\|5e2f\|piedra\|9f3a1c2b` | mi jugada y mi sal |

Como la difusión no confirma nada, los mensajes importantes (RETO, HUELLA,
REVELO) se **repiten cada 400 ms** hasta que la partida avanza. Un amigo que no
se oye en 4 s desaparece de la lista. Después de terminar, el bichito sigue
contestando 3 s más, por si al rival le faltó nuestra revelación. Con todo eso,
un duelo termina aunque se pierda un tercio de los paquetes (lo prueba
`class RadioMala`).

`duelo.py` es **lógica pura**: no toca la radio. Deja en `partida.salida` los
mensajes que hay que mandar y recibe los que llegan con `partida.recibir()`.
Por eso se prueba en la PC conectando dos `Duelo` entre sí.

### 13.5 La máquina de estados del duelo

```
           retar (B)                  llega SI                confirmar (B)
  LIBRE ─────────────▶ RETANDO ─────────────────▶ ELIGIENDO ─────────────▶ ESPERANDO ──▶ FIN
    │                                                ▲                    (huellas y
    │  llega RETO                 aceptar (B)        │                    revelaciones)
    └────────────▶ INVITADO ─────────────────────────┘
                      └──rechazar (C)──▶ LIBRE
```

Y las salidas de emergencia:

- C en RETANDO, ELIGIENDO o ESPERANDO: abandonas (manda NO) y vuelves a LIBRE.
- Si no eliges en 15 s, va la mano que tengas seleccionada.
- Si en 20 s no avanza nada: CANCELADO (o HUYO, si tú ya habías revelado).
- Si los dos se retan al mismo tiempo, cede el de id menor.
- Si alguien te reta mientras estás en otro duelo, le contestas NO.
- En FIN, cualquier tecla regresa a LIBRE.

### 13.6 El apartado AMIGOS (`amigos.py`)

`amigos.py` solo conecta: la radio, los botones y la pantalla. En cada `paso`
avanza el duelo, le pasa los mensajes que llegaron, manda los que salieron y
revisa si cambió de estado (para sonar y dar premios).

| Pantalla | A | B | C |
|---|---|---|---|
| Buscando amigos | siguiente amigo | retarlo | salir de AMIGOS |
| Te retan | — | aceptar | rechazar |
| Eligiendo mano | otra mano | confirmar | rendirse |
| Retando o esperando | — | — | rajarse |
| Resultado | cualquier tecla sigue | | |

| Resultado | Felicidad | Cuenta como |
|---|---|---|
| GANASTE, TRAMPA (del otro), SE RAJO | +25 | victoria |
| EMPATE | +10 | — |
| PERDISTE | +5 (jugar siempre alegra un poco) | derrota |

Si llegaste a elegir mano, el duelo cuesta 5 de energía.

### 13.7 Lo que todavía no protege: el reto del taller

El commit-reveal impide que el rival vea tu mano antes de tiempo. Pero **no
hay autenticación**: cualquiera puede mandar un mensaje diciendo que es otro
bichito. Por ejemplo, un tercero que manda `T1|C3D4|A1B2|NO|5e2f` cancela el
duelo de Ana fingiendo ser Beto, y un HOLA falso con cualquier id hace aparecer
"amigos" que no existen.

Preguntas para pensar:

- ¿Cómo probarías que un mensaje viene de quien dice? (pista: una clave
  compartida y un HMAC).
- Si la clave está en el firmware, cualquiera con la placa la puede leer. ¿Qué
  tan grave es eso aquí?
- ¿Qué pasa si alguien graba un mensaje viejo y lo vuelve a mandar
  (*replay*)? ¿Ayuda el id del duelo?

---

## 14. Pruebas en la PC: `tests/`

La lógica no toca hardware, así que corre en CPython... salvo por `machine`,
`framebuf` y los relojes en milisegundos, que solo existen en MicroPython.
`tests/comun.py` lo resuelve: pone en la ruta `tests/stubs/` (versiones de
mentira de `machine`, `framebuf` y `micropython`), agrega `time.ticks_ms` y
compañía, y trae dos ayudas:

- `comun.Pantalla`: un FrameBuffer de 128×64 que además anota qué textos,
  imágenes y rectángulos rellenos se dibujaron, para que una prueba pueda
  preguntar "¿salió Saludando?".
- `comun.RadioFalsa`: reemplaza a `radio.py`; lo que manda el bichito le llega
  a un `Duelo` rival y al revés.

```bash
python3 -m unittest discover -s tests
```

Son 65 pruebas y corren en menos de un segundo. Compáralo con "subir a la
placa, esperar y mirar la pantalla".

| Archivo | Qué prueba |
|---|---|
| `test_bicho.py` | etapas, necesidades, crianza y guardado |
| `test_juego.py` | el menú, los avisos, los dos ejercicios (`Saludar`, `SinNombre`) y el `Contrato` de todos los apartados |
| `test_jugar.py` | la física del Pong y cómo se juega desde el menú |
| `test_duelo.py` | el protocolo: descubrimiento, partidas, radio que pierde paquetes y seguridad |
| `test_amigos.py` | el apartado AMIGOS contra un rival simulado |

Para correr solo unas, usa `-k` con el nombre de la clase o de la prueba:

```bash
python3 -m unittest discover -s tests -k Contrato -v
```

El truco para no esperar horas de juego: `test_bicho.py` llama
`bicho.vivir(minutos)` directamente, y `test_juego.py` fija `config.ESCALA = 60`
para que cada segundo simulado sea un minuto.

### Escribe la prueba de tu apartado

`tests/test_juego.py` ya trae ayudas: `bebe()` (un bichito recién nacido),
`abrir(apartado)` (navega el menú hasta él y lo elige, como un jugador),
`pantalla()` (dibuja y te da la `comun.Pantalla`) y `esperar(ms)`. Para un
apartado `bailar.py`, agrega arriba `from apartados import bailar` y una clase
como esta:

```python
class Bailar(unittest.TestCase):
    def setUp(self):
        bebe()
        abrir(bailar)

    def test_dice_bailando(self):
        self.assertIn("Bailando", pantalla().todo())

    def test_c_lo_quita(self):
        juego.tecla("c")
        self.assertEqual(juego.pantalla, juego.MENU)
```

Ojo: `abrir()` recorre el menú buscando tu apartado. Si no lo agregaste a
`menu.py`, la prueba da vueltas para siempre (córtala con `Ctrl-C`).

**Ejercicio:** escribe la prueba **antes** de programar tu apartado. Hazla
fallar y después hazla pasar.

---

## 15. Ejercicios y extensiones (por dificultad)

**Fáciles (un rato):**

- **Tu propio video** en el apartado VIDEO. Graba algo con tu celular y
  conviértelo (necesitas `pip install opencv-python numpy`):

  ```bash
  python3 herramientas/video_a_oled.py mi_video.mp4 --inicio 2 --segundos 8
  ```

  Sube `src/apartados/video_cuadros.bin` a `/apartados` en la placa. Después
  ponle música: la melodía está en `MELODIA`, dentro de `apartados/video.py`.
  Usa solo videos que sean tuyos o que tengas permiso de usar.

- Las ideas de `saludar.py` (sección 7.3).
- Bautiza `sin_nombre.py` y dale un comportamiento: adivinar un número con A y
  B, contar apretones, puntos más rápidos (sección 7.4).
- Una melodía nueva en `sonido.MELODIAS` y úsala desde un apartado.
- Una acción rápida nueva, por ejemplo un premio que sube la felicidad pero
  baja el hambre.
- Cambia `ESCALA` y mira cómo cambia el ritmo de vida.

**Medias (una tarde):**

- Una cara nueva en `sprites.CARAS` (sección 8).
- Una forma adulta nueva, con su prueba (sección 9.4).
- Una tercera página en ESTADO.
- Un Pong más difícil, o con dos bolas.
- Que el tiempo del bucle no se atrase (sección 11).
- Descontar el tiempo que la placa estuvo apagada (sección 12).

**Difíciles (proyecto final):**

- **Autenticar los mensajes del duelo** (sección 13.7).
- **Bitácora anti-trampa:** guardar junto al bichito un hash encadenado de sus
  cambios, para que si alguien edita `bicho.json` a mano, el bichito lo note
  ("INTEGRIDAD ROTA").
- **Deep sleep:** dormir la placa y despertarla con un botón. En la C3 solo los
  GPIO 0 a 5 la despiertan: A (GPIO 0) y B (GPIO 1) sirven, C (GPIO 10) no. Al
  despertar, descontar el tiempo dormido.

---

## 16. Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| Thonny no encuentra la placa / no aparece `/dev/ttyACM0` | cable solo de carga | cambiar el cable (prueba pasar archivos del celular con él) |
| Thonny no muestra `>>>` | el bichito está corriendo (`main.py`) | **Stop** en Thonny |
| `invalid header: 0xffffffff`, `Errno 5` | la placa no tiene MicroPython | `./flashear.sh` |
| `esptool` no detecta la placa | no está en modo de descarga | BOOT apretado + RESET |
| `Permission denied` en el puerto | usuario sin el grupo `dialout` | `usermod -aG dialout` y volver a entrar |
| `in use by another program` | otro programa tiene el puerto (Arduino IDE, VS Code, otra terminal con `mpremote`) | cerrarlo |
| La pantalla se queda congelada después de conectar `mpremote` | `mpremote` detuvo el `main.py` que corría | desconectar y conectar el USB, o `./subir.sh` (reinicia al final) |
| `prueba.py` dice `ImportError` | el código no está en la placa | `./subir.sh` primero |
| La consola dice `I2C: []` | la OLED no responde | revisar SDA, SCL, VCC a 3V3 y GND; probar SDA y SCL al revés en `config.py` |
| Basura en la pantalla | I²C demasiado rápido para tu módulo | `OLED_FREQ = 400000` en `config.py` |
| La imagen sale de cabeza | la OLED quedó montada al revés | `OLED_GIRADA = True` |
| Un botón se lee apretado sin tocarlo | botón girado 90° o corto a GND | girarlo; las patas deben quedar a ambos lados del canal |
| El menú salta de dos en dos | rebote del botón | subir `REBOTE_MS` en `botones.py` |
| La placa "murió" después de cablear | algo conectado al GPIO 2, 8 o 9 | moverlo a otro GPIO |
| La placa se reinicia al entrar a AMIGOS | pico de corriente de la radio | `TXPOWER = 8.5`; capacitor de 100 µF entre 5V y GND; otro cable |
| AMIGOS no encuentra a nadie | el otro no está en AMIGOS, o están en canales distintos | los dos dentro de AMIGOS, mismo `CANAL` |
| "AUN NO NACE" | sigue en el huevo | esperar 30 s (con `ESCALA = 60`) |
| "ZZZ..." | la luz está apagada | LUZ |
| Falla la prueba `Contrato` | un apartado no cumple el contrato | el mensaje dice cuál; revisa `NOMBRE` y que C lo saque |

---

## 17. Referencias

- Documentación de MicroPython: <https://docs.micropython.org/>
  - `framebuf`: <https://docs.micropython.org/en/latest/library/framebuf.html>
  - `espnow`: <https://docs.micropython.org/en/latest/library/espnow.html>
  - Guía de la ESP32: <https://docs.micropython.org/en/latest/esp32/quickref.html>
  - `mpremote`: <https://docs.micropython.org/en/latest/reference/mpremote.html>
- Firmware ESP32-C3: <https://micropython.org/download/ESP32_GENERIC_C3/>
- Problemas de la radio en la C3 SuperMini:
  <https://hackaday.io/project/205906-esp32-c3-super-mini-wifi-fix-3-methods-that-work>
- Datasheet del SSD1306 (mapa de memoria, sección 8.7): buscar "SSD1306 datasheet".
- Esquemas de compromiso (commit-reveal): <https://en.wikipedia.org/wiki/Commitment_scheme>

"Tamagotchi" es marca registrada de Bandai. Este material no está asociado con
Bandai.
