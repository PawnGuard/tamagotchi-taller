# apartados/ — cada opcion del menu del bichito es un archivo de esta carpeta.
#
# Para crear uno nuevo:
#   1. Copia apartados/sin_nombre.py con otro nombre (por ejemplo bailar.py).
#   2. Agregalo a la lista de menu.py.
#
# Un apartado puede tener estas cosas (solo NOMBRE y empezar son obligatorias):
#
#   NOMBRE = "COMER"        lo que sale en el menu (maximo 13 letras)
#   SIEMPRE = True          tambien funciona con el bichito dormido o en el huevo
#
#   def empezar(bicho):     se llama al elegirlo en el menu.
#       - Si devuelve un texto, ese texto sale abajo un momento y listo.
#         Asi son las acciones rapidas (comer.py, limpiar.py).
#       - Si no devuelve nada, el apartado se queda en pantalla y desde ahi
#         se usan las de abajo (saludar.py, jugar.py).
#
#   def tecla(bicho, t):    se apreto un boton: t es "a", "b" o "c".
#                           Devuelve True para salir. (Si no la escribes,
#                           C te saca.)
#   def paso(bicho, ms):    se llama 20 veces por segundo; ms = tiempo que paso.
#                           Devuelve True para salir.
#   def dibujar(fb, bicho): pinta la pantalla (ya viene borrada). Ver dibujo.py.
#                           Si no la escribes, sale el bichito y el NOMBRE.
#   def terminar(bicho):    se llama al salir, para dejar todo en orden. Si
#                           devuelve un texto, sale abajo un momento.
#
# `bicho` es el bichito (ver bicho.py): bicho.hambre, bicho.felicidad,
# bicho.energia, bicho.salud (de 0 a 100), bicho.caca (0 a 3), bicho.enfermo,
# bicho.luz... Puedes cambiarlos: si te pasas de 100 o de 0, se corrige solo.
