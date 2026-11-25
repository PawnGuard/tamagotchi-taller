# video_a_oled.py — convierte un video TUYO (grabado con el celular, por
# ejemplo) en cuadros para la pantalla OLED de 128x64 del Tamagotchi.
#
#   python3 herramientas/video_a_oled.py mi_video.mp4
#   python3 herramientas/video_a_oled.py mi_video.mp4 --inicio 2 --segundos 8 --fps 12
#   python3 herramientas/video_a_oled.py mi_video.mp4 --ver      # ademas guarda una vista previa
#
# Guarda src/apartados/video_cuadros.bin; el apartado VIDEO lo reproduce.
# Con --salida src/apartados/intro_cuadros.bin es el video del INTRO.
# Luego: ./subir.sh
#
# Usa solo videos que sean tuyos o que tengas permiso de usar.
#
# Como se hace un video para una pantalla de 1 bit:
#   1. Se toman FPS cuadros por segundo (no todos los del video).
#   2. Cada cuadro se reduce a 128x64. Si el video es vertical se AJUSTA (con
#      franjas negras a los lados); si es horizontal se RECORTA el centro.
#   3. Se pasa a grises y se estira el contraste.
#   4. TRAMADO (dithering, Floyd-Steinberg): la pantalla solo prende o apaga
#      cada pixel, asi que los grises se simulan con puntitos. El error de
#      redondear cada pixel se reparte entre sus vecinos.
#   5. Se empaqueta en MONO_VLSB: el formato que la pantalla entiende directo.
#
# Formato del archivo: "VID1", fps (1 byte), numero de cuadros (2 bytes),
# ancho y alto (1 byte cada uno), y luego cada cuadro de 1024 bytes.
import argparse
import os
import struct
import sys

import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "..", "src", "apartados", "video_cuadros.bin")
ANCHO, ALTO = 128, 64


def a_128x64(cuadro, recorte):
    """Reduce un cuadro BGR a 128x64 en grises, recortando o ajustando."""
    gris = cv2.cvtColor(cuadro, cv2.COLOR_BGR2GRAY)
    h, w = gris.shape
    if recorte == "auto":
        recorte = "ajustar" if h > w else "llenar"
    if recorte == "llenar":                       # recorta el centro a 2:1
        if w / h > ANCHO / ALTO:
            nuevo_w = int(h * ANCHO / ALTO)
            x = (w - nuevo_w) // 2
            gris = gris[:, x:x + nuevo_w]
        else:
            nuevo_h = int(w * ALTO / ANCHO)
            y = (h - nuevo_h) // 2
            gris = gris[y:y + nuevo_h, :]
        return cv2.resize(gris, (ANCHO, ALTO), interpolation=cv2.INTER_AREA)
    escala = min(ANCHO / w, ALTO / h)              # cabe entero, con franjas
    chico = cv2.resize(gris, (max(1, int(w * escala)), max(1, int(h * escala))),
                       interpolation=cv2.INTER_AREA)
    lienzo = np.zeros((ALTO, ANCHO), np.uint8)
    y, x = (ALTO - chico.shape[0]) // 2, (ANCHO - chico.shape[1]) // 2
    lienzo[y:y + chico.shape[0], x:x + chico.shape[1]] = chico
    return lienzo


def contraste(gris):
    """Estira los grises para que lo mas oscuro sea negro y lo mas claro blanco."""
    bajo, alto = np.percentile(gris, (2, 98))
    if alto - bajo < 10:
        return gris
    return np.clip((gris.astype(np.float32) - bajo) * 255 / (alto - bajo), 0, 255)


def tramado(gris):
    """Floyd-Steinberg: grises -> blanco o negro, repartiendo el error."""
    img = gris.astype(np.float32).copy()
    salida = np.zeros(img.shape, np.uint8)
    for y in range(ALTO):
        for x in range(ANCHO):
            viejo = img[y, x]
            nuevo = 255.0 if viejo >= 128 else 0.0
            salida[y, x] = 1 if nuevo else 0
            err = viejo - nuevo
            if x + 1 < ANCHO:
                img[y, x + 1] += err * 7 / 16
            if y + 1 < ALTO:
                if x > 0:
                    img[y + 1, x - 1] += err * 3 / 16
                img[y + 1, x] += err * 5 / 16
                if x + 1 < ANCHO:
                    img[y + 1, x + 1] += err * 1 / 16
    return salida


def a_vlsb(bits):
    """Matriz 64x128 de 0/1 -> 1024 bytes MONO_VLSB (8 pixeles por columna)."""
    datos = bytearray(ANCHO * ALTO // 8)
    for pagina in range(ALTO // 8):
        bloque = bits[pagina * 8:(pagina + 1) * 8, :]            # 8 x 128
        for bit in range(8):
            fila = bloque[bit]
            for x in np.nonzero(fila)[0]:
                datos[pagina * ANCHO + x] |= 1 << bit
    return bytes(datos)


def convertir(ruta, fps=10, inicio=0.0, segundos=10.0, recorte="auto", invertir=False,
              modo="tramado"):
    """Devuelve la lista de cuadros (matrices 64x128 de 0/1)."""
    video = cv2.VideoCapture(ruta)
    if not video.isOpened():
        sys.exit("No pude abrir %s. Si es .mov de iPhone (HEVC), conviertelo a .mp4 (H.264)." % ruta)
    fps_video = video.get(cv2.CAP_PROP_FPS) or 30
    cuadros = []
    t = inicio
    while t < inicio + segundos:
        video.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, cuadro = video.read()
        if not ok:
            break
        gris = contraste(a_128x64(cuadro, recorte))
        if invertir:
            gris = 255 - gris
        bits = tramado(gris) if modo == "tramado" else (gris >= 128).astype(np.uint8)
        cuadros.append(bits)
        t += 1 / fps
    video.release()
    if not cuadros:
        sys.exit("El video no tiene cuadros en ese rango (revisa --inicio).")
    print("video a %.0f fps -> %d cuadros a %d fps" % (fps_video, len(cuadros), fps))
    return cuadros


def guardar(cuadros, fps, ruta=SALIDA):
    with open(ruta, "wb") as f:
        f.write(b"VID1" + struct.pack("<BHBB", fps, len(cuadros), ANCHO, ALTO))
        for c in cuadros:
            f.write(a_vlsb(c))
    print("guardado %s (%d KB)" % (os.path.normpath(ruta), os.path.getsize(ruta) // 1024))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Convierte un video a cuadros para la OLED 128x64.")
    ap.add_argument("video")
    ap.add_argument("--fps", type=int, default=10, help="cuadros por segundo (10 a 15 va bien)")
    ap.add_argument("--inicio", type=float, default=0, help="segundo donde empieza")
    ap.add_argument("--segundos", type=float, default=10, help="cuanto dura (maximo ~60)")
    ap.add_argument("--recorte", choices=("auto", "llenar", "ajustar"), default="auto",
                    help="llenar = recorta el centro; ajustar = cabe entero con franjas")
    ap.add_argument("--modo", choices=("tramado", "umbral"), default="tramado",
                    help="tramado simula grises con puntitos; umbral = solo blanco y negro")
    ap.add_argument("--invertir", action="store_true", help="cambia blanco por negro")
    ap.add_argument("--ver", action="store_true", help="guarda herramientas/video.png con algunos cuadros")
    ap.add_argument("--salida", default=SALIDA,
                    help="donde guardarlo (por defecto el del apartado VIDEO; para el INTRO usa "
                         "src/apartados/intro_cuadros.bin)")
    a = ap.parse_args()
    if a.fps * a.segundos > 900:
        sys.exit("Demasiados cuadros (%d): baja --fps o --segundos (900 cuadros = 900 KB)." % (a.fps * a.segundos))
    cuadros = convertir(a.video, a.fps, a.inicio, a.segundos, a.recorte, a.invertir, a.modo)
    guardar(cuadros, a.fps, a.salida)
    if a.ver:
        muestra = cuadros[:: max(1, len(cuadros) // 6)][:6]
        hoja = np.zeros((ALTO * 2 + 4, (ANCHO + 4) * 3), np.uint8)
        for i, c in enumerate(muestra):
            y, x = (i // 3) * (ALTO + 4), (i % 3) * (ANCHO + 4)
            hoja[y:y + ALTO, x:x + ANCHO] = c * 255
        cv2.imwrite(os.path.join(AQUI, "video.png"),
                    cv2.resize(hoja, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST))
        print("vista previa: herramientas/video.png")
