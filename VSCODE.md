# Usar VS Code en vez de Thonny

Thonny es lo más rápido para el taller porque ya trae todo. Si prefieres
VS Code, también funciona. La diferencia es que VS Code no habla con la placa
por sí solo: usa **mpremote**, una herramienta oficial de MicroPython, desde
botones ya preparados en este repositorio.

**Haz los pasos 1 a 3 antes del taller**, en tu casa y con internet. El paso 4
ya es con la placa.

## 1. Instala Python y VS Code

- **Python 3.10 o más nuevo**
  - Windows: descárgalo de [python.org](https://www.python.org/downloads/).
    En la primera pantalla del instalador marca **Add python.exe to PATH**.
  - macOS: el instalador de [python.org](https://www.python.org/downloads/)
    o `brew install python`.
  - Linux: ya viene. En Ubuntu o Debian instala también
    `sudo apt install python3-venv`.
- **[VS Code](https://code.visualstudio.com)** con la extensión **Python** de
  Microsoft. Al abrir el repositorio, VS Code te la ofrece sola.

## 2. Abre el repositorio

Descarga o clona este repositorio y en VS Code usa **File → Open Folder**
sobre la carpeta `tamagotchi-taller`. Abre la carpeta completa, no solo un
archivo, o los botones del paso 4 no aparecen.

## 3. Crea el entorno de Python

1. `Ctrl+Shift+P` (en macOS `Cmd+Shift+P`) → **Python: Create Environment**.
2. Elige **Venv** y luego tu versión de Python.
3. Marca **requirements.txt** y acepta.

VS Code crea la carpeta `.venv` con mpremote dentro y la deja seleccionada.
Para comprobarlo, abre una terminal (**Terminal → New Terminal**) y escribe:

```bash
python -m mpremote version
```

Si sale un número de versión, ya quedó.

Por si en el taller tu placa necesita MicroPython de nuevo, baja también el
firmware ahora que tienes internet (no toca la placa):

```bash
python herramientas/flashear.py --descargar
```

## 4. Sube el código y juega

**Cierra Thonny** si lo tienes abierto: solo un programa a la vez puede usar
la placa.

1. Conecta la placa por USB.
2. `Ctrl+Shift+B` sube todo el código de `src/` a la placa.
3. **Terminal → Run Task… → Jugar** corre al bichito.

`Ctrl+C` en la terminal solo cierra la conexión: el bichito sigue vivo en la
placa. No pasa nada, porque la siguiente tarea que corras lo detiene sola.
Si quieres pararlo ya, abre **Consola de la placa (REPL)** y aprieta `Ctrl+C`.

Cada vez que cambies un archivo, repite 2 y 3.

### Todas las tareas

Están en **Terminal → Run Task…**:

| Tarea | Qué hace |
|---|---|
| Subir codigo | Copia `src/` a la placa. Atajo: `Ctrl+Shift+B` |
| Jugar | Corre `tama.py` |
| Prueba de hardware | Corre `prueba.py`: pantalla, escala y botones |
| Consola de la placa (REPL) | Escribe Python directo en la placa. `Ctrl+]` para salir |
| Ver archivos de la placa | Lista lo que hay guardado en la placa |
| Huevo nuevo | Borra `bicho.json` para empezar otra mascota |
| Ver placas conectadas | Muestra los puertos que ve tu computadora |
| Flashear MicroPython | Borra la placa, le graba MicroPython y sube el código |
| Pruebas en la PC | Prueba la lógica sin placa |

Si prefieres escribir los comandos, en la terminal de VS Code funcionan igual:

```bash
python herramientas/subir.py
```

```bash
python -m mpremote run src/tama.py
```

## Si tu placa no tiene MicroPython

Pasa si la placa viene sin firmware o si le subiste un programa de Arduino:
`subir.py` dice que la placa no contesta como MicroPython. Con la placa
conectada, usa la tarea **Flashear MicroPython** o:

```bash
python herramientas/flashear.py
```

Busca la placa sola, te pregunta antes de borrar, graba MicroPython 1.29.0
(lo descarga si no lo tienes) y sube el código. **Borra todo lo que tenga la
placa**, tu mascota incluida. Si no logra grabar, te pide apretar BOOT al
conectarla y lo vuelve a intentar.

## Si algo falla

| Síntoma | Solución |
|---|---|
| `failed to access` o `could not enter raw repl` | Thonny u otro monitor serie tiene el puerto: ciérralo. Si le diste un puerto a mano, revisa que sea el correcto. |
| Se queda esperando y no dice nada, o dice `no contesta como MicroPython` | La placa no tiene MicroPython o tiene otro programa (por ejemplo, de Arduino). Desconéctala y conéctala; si sigue igual, flashéala con `python herramientas/flashear.py`. |
| `no device found` | Revisa el cable (debe ser de datos) y usa **Ver placas conectadas**. |
| Tienes varias placas o la elige mal | `python herramientas/subir.py COM5` (o `/dev/ttyACM0`, `/dev/cu.usbmodem…`). Para jugar: `python -m mpremote connect COM5 run src/tama.py` |
| Linux: `Permission denied` en el puerto | `sudo usermod -aG dialout $USER` y cierra sesión. |
| Las tareas no aparecen | Abriste un archivo suelto. Usa **File → Open Folder** sobre la carpeta del repositorio. |
| `No module named mpremote` | VS Code no está usando `.venv`. `Ctrl+Shift+P` → **Python: Select Interpreter** → elige el que dice `.venv`. |
| `import machine` subrayado en amarillo | Es el mismo caso: selecciona el intérprete de `.venv`, que trae el autocompletado de MicroPython. |

## Tu propio video

La herramienta de video usa el mismo entorno. En la terminal de VS Code:

```bash
python -m pip install opencv-python numpy
```

```bash
python herramientas/video_a_oled.py mi_video.mp4 --inicio 2 --segundos 8
```

Después usa **Subir codigo**: la carpeta `apartados` se sube completa, con
el video incluido.
