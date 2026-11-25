# luz.py — apagar la luz lo duerme: gasta la mitad y recupera energia.
NOMBRE = "LUZ"
SIEMPRE = True          # dormido tambien se puede prender la luz


def empezar(bicho):
    bicho.luz = not bicho.luz
    return "LUZ ON" if bicho.luz else "SHHH..."
