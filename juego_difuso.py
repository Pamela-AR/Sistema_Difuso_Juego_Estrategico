# Importando la librería de lógica difusa Mamdani
from copy import deepcopy

from mamdani import LinguisticVar, Mamdani, trap_left, triangle, trap_right


VIDA_MAXIMA = 100
DISTANCIA_MIN = 0
DISTANCIA_MAX = 100
DISTANCIA_INICIAL = 50
DANIO_JUGADOR = 12
REDUCCION_DEFENSA = 8


# Definiendo las variables lingüísticas para el juego estratégico
# Entradas
distancia = LinguisticVar("Distancia", [0, 100], "u")
distancia.add_set("Cerca", trap_left(20, 40))
distancia.add_set("Media", triangle(30, 50, 70))
distancia.add_set("Lejos", trap_right(60, 80))

vida_npc = LinguisticVar("Vida_NPC", [0, 100], "%")
vida_npc.add_set("Baja", trap_left(25, 45))
vida_npc.add_set("Media", triangle(30, 50, 70))
vida_npc.add_set("Alta", trap_right(55, 75))

vida_jugador = LinguisticVar("Vida_Jugador", [0, 100], "%")
vida_jugador.add_set("Baja", trap_left(25, 45))
vida_jugador.add_set("Media", triangle(30, 50, 70))
vida_jugador.add_set("Alta", trap_right(55, 75))

# Salidas
ataque = LinguisticVar("Ataque", [0, 100], "nivel")
ataque.add_set("Muy_Bajo", trap_left(10, 20))
ataque.add_set("Bajo", triangle(15, 30, 45))
ataque.add_set("Medio", triangle(35, 50, 65))
ataque.add_set("Alto", triangle(55, 70, 85))
ataque.add_set("Muy_Alto", trap_right(80, 90))

movimiento = LinguisticVar("Movimiento", [0, 100], "nivel")
movimiento.add_set("Retroceder", trap_left(20, 35))
movimiento.add_set("Mantener", triangle(30, 50, 70))
movimiento.add_set("Acercarse", trap_right(65, 80))

# Creando el sistema difuso Mamdani
sistema = Mamdani(outputs=[ataque, movimiento], resolution=500)

# Definiendo las reglas difusas
# Distancia cerca
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Alta"), (vida_jugador, "Baja")],
                 {ataque: "Muy_Alto", movimiento: "Mantener"})

sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Alta"), (vida_jugador, "Media")],
                 {ataque: "Alto", movimiento: "Mantener"})

sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Alta"), (vida_jugador, "Alta")],
                 {ataque: "Alto", movimiento: "Mantener"})

sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Baja")],
                 {ataque: "Alto", movimiento: "Mantener"})

sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Media")],
                 {ataque: "Medio", movimiento: "Mantener"})

sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Alta")],
                 {ataque: "Bajo", movimiento: "Retroceder"})

sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Baja"), (vida_jugador, "Baja")],
                 {ataque: "Medio", movimiento: "Retroceder"})

sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Baja"), (vida_jugador, "Media")],
                 {ataque: "Bajo", movimiento: "Retroceder"})

sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Baja"), (vida_jugador, "Alta")],
                 {ataque: "Muy_Bajo", movimiento: "Retroceder"})

# Distancia media
sistema.add_rule([(distancia, "Media"), (vida_npc, "Alta"), (vida_jugador, "Baja")],
                 {ataque: "Alto", movimiento: "Acercarse"})

sistema.add_rule([(distancia, "Media"), (vida_npc, "Alta"), (vida_jugador, "Media")],
                 {ataque: "Alto", movimiento: "Acercarse"})

sistema.add_rule([(distancia, "Media"), (vida_npc, "Alta"), (vida_jugador, "Alta")],
                 {ataque: "Medio", movimiento: "Mantener"})

sistema.add_rule([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Baja")],
                 {ataque: "Alto", movimiento: "Acercarse"})

sistema.add_rule([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Media")],
                 {ataque: "Medio", movimiento: "Mantener"})

sistema.add_rule([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Alta")],
                 {ataque: "Bajo", movimiento: "Retroceder"})

sistema.add_rule([(distancia, "Media"), (vida_npc, "Baja"), (vida_jugador, "Baja")],
                 {ataque: "Medio", movimiento: "Mantener"})

sistema.add_rule([(distancia, "Media"), (vida_npc, "Baja"), (vida_jugador, "Media")],
                 {ataque: "Bajo", movimiento: "Retroceder"})

# Distancia lejos
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Alta"), (vida_jugador, "Baja")],
                 {ataque: "Medio", movimiento: "Acercarse"})

sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Media"), (vida_jugador, "Media")],
                 {ataque: "Bajo", movimiento: "Acercarse"})

sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Baja"), (vida_jugador, "Alta")],
                 {ataque: "Muy_Bajo", movimiento: "Retroceder"})


ACCIONES_JUGADOR = {
    "1": "atacar",
    "2": "defender",
    "3": "acercarse",
    "4": "alejarse",
}

ACCIONES_DISPONIBLES = {
    "atacar": {"nombre": "Atacar", "descripcion": "Golpea si estás a rango medio o corto."},
    "defender": {"nombre": "Defender", "descripcion": "Reduce parte del daño recibido este turno."},
    "acercarse": {"nombre": "Acercarse", "descripcion": "Reduce la distancia para entrar en rango."},
    "alejarse": {"nombre": "Alejarse", "descripcion": "Aumenta la distancia para forzar al NPC a moverse."},
}


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


def crear_estado_inicial():
    return {
        "turno": 1,
        "vida_jugador": VIDA_MAXIMA,
        "vida_npc": VIDA_MAXIMA,
        "distancia": DISTANCIA_INICIAL,
        "terminado": False,
        "ganador": None,
    }


def _normalizar_estado(estado):
    base = crear_estado_inicial()
    base.update(deepcopy(estado or {}))
    base["turno"] = max(1, int(base["turno"]))
    base["vida_jugador"] = limitar(int(base["vida_jugador"]), 0, VIDA_MAXIMA)
    base["vida_npc"] = limitar(int(base["vida_npc"]), 0, VIDA_MAXIMA)
    base["distancia"] = limitar(int(base["distancia"]), DISTANCIA_MIN, DISTANCIA_MAX)
    base["terminado"] = bool(base["terminado"])
    base["ganador"] = base["ganador"] if base["ganador"] in {"Jugador", "NPC"} else None
    return base


# Funciones auxiliares para interpretar los resultados de las salidas difusas en acciones concretas del juego
def interpretar_ataque(valor):
    if valor <= 20:
        return "Huir", 0
    elif valor <= 40:
        return "Defender", 5
    elif valor <= 60:
        return "Ataque_Normal", 10
    elif valor <= 80:
        return "Ataque_Fuerte", 18
    else:
        return "Ataque_Especial", 25


def interpretar_movimiento(valor):
    if valor <= 33:
        return "Retroceder"
    elif valor <= 66:
        return "Mantener"
    else:
        return "Acercarse"


def describir_ataque_npc(accion):
    nombres = {
        "Huir": "Retirada",
        "Defender": "Guardia",
        "Ataque_Normal": "Golpe",
        "Ataque_Fuerte": "Impacto Fuerte",
        "Ataque_Especial": "Pulso Especial",
    }
    return nombres.get(accion, accion)


def describir_movimiento_npc(accion):
    textos = {
        "Retroceder": "Bestia Difusa retrocede y busca espacio.",
        "Mantener": "Bestia Difusa mantiene la posición.",
        "Acercarse": "Bestia Difusa se lanza hacia adelante.",
    }
    return textos.get(accion, "Bestia Difusa cambia de postura.")


# Función del enemigo
def turno_npc(distancia_val, vida_npc_val, vida_jugador_val):
    entradas = {
        distancia: distancia_val,
        vida_npc: vida_npc_val,
        vida_jugador: vida_jugador_val
    }

    salidas = sistema.compute(entradas)

    valor_ataque = salidas[ataque]
    valor_mov = salidas[movimiento]

    accion_ataque, danio = interpretar_ataque(valor_ataque)
    accion_mov = interpretar_movimiento(valor_mov)

    return accion_ataque, danio, accion_mov, valor_ataque, valor_mov


def resolver_turno(estado, accion_jugador):
    estado_actual = _normalizar_estado(estado)
    accion = ACCIONES_JUGADOR.get(str(accion_jugador), accion_jugador)

    if accion not in ACCIONES_DISPONIBLES:
        raise ValueError("Acción no válida.")

    if estado_actual["terminado"]:
        return {
            "estado": estado_actual,
            "registro": ["La partida ya terminó. Reinicia para volver a jugar."],
            "jugador": {},
            "npc": {},
        }

    registro = [f"Turno {estado_actual['turno']}"]
    defensa = False
    jugador = {
        "accion": accion,
        "danio": 0,
        "mensaje": "",
    }

    if accion == "atacar":
        if estado_actual["distancia"] <= 60:
            estado_actual["vida_npc"] = limitar(
                estado_actual["vida_npc"] - DANIO_JUGADOR, 0, VIDA_MAXIMA
            )
            jugador["danio"] = DANIO_JUGADOR
            jugador["mensaje"] = "Tu ataque impacta con fuerza."
        else:
            jugador["mensaje"] = "Tu ataque falla porque el rival está muy lejos."
    elif accion == "defender":
        defensa = True
        jugador["mensaje"] = "Te preparas para resistir el próximo golpe."
    elif accion == "acercarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] - 15, DISTANCIA_MIN, DISTANCIA_MAX
        )
        jugador["mensaje"] = "Avanzas para cerrar la distancia."
    elif accion == "alejarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] + 15, DISTANCIA_MIN, DISTANCIA_MAX
        )
        jugador["mensaje"] = "Retrocedes para ganar espacio."

    registro.append(jugador["mensaje"])

    if estado_actual["vida_npc"] <= 0:
        estado_actual["terminado"] = True
        estado_actual["ganador"] = "Jugador"
        registro.append("Bestia Difusa cae derrotada.")
        return {
            "estado": estado_actual,
            "registro": registro,
            "jugador": jugador,
            "npc": {},
        }

    acc_atq, danio, acc_mov, val_atq, val_mov = turno_npc(
        estado_actual["distancia"],
        estado_actual["vida_npc"],
        estado_actual["vida_jugador"],
    )

    npc = {
        "accion_ataque": acc_atq,
        "danio_base": danio,
        "movimiento": acc_mov,
        "valor_ataque": round(val_atq, 2),
        "valor_movimiento": round(val_mov, 2),
        "danio_aplicado": 0,
        "defensa_activada": acc_atq == "Defender",
        "ataque_conecto": False,
    }

    registro.append(f"Bestia Difusa usa {describir_ataque_npc(acc_atq)}.")
    registro.append(describir_movimiento_npc(acc_mov))

    if acc_mov == "Acercarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] - 10, DISTANCIA_MIN, DISTANCIA_MAX
        )
    elif acc_mov == "Retroceder":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] + 10, DISTANCIA_MIN, DISTANCIA_MAX
        )

    if acc_atq not in {"Huir", "Defender"}:
        if estado_actual["distancia"] <= 70:
            danio_real = danio
            if defensa:
                danio_real = max(0, danio_real - REDUCCION_DEFENSA)

            npc["danio_aplicado"] = danio_real
            npc["ataque_conecto"] = danio_real > 0
            estado_actual["vida_jugador"] = limitar(
                estado_actual["vida_jugador"] - danio_real, 0, VIDA_MAXIMA
            )

            if danio_real > 0:
                if defensa:
                    registro.append(
                        f"Tu defensa amortigua el ataque, pero recibes {danio_real} de daño."
                    )
                else:
                    registro.append(f"El impacto enemigo te causa {danio_real} de daño.")
            else:
                registro.append("Tu defensa neutraliza por completo el golpe enemigo.")
        else:
            registro.append("El ataque enemigo no alcanza la distancia necesaria.")
    elif acc_atq == "Defender":
        registro.append("Bestia Difusa se cubre y espera tu siguiente movimiento.")
    else:
        registro.append("Bestia Difusa rompe el intercambio y toma distancia.")

    if estado_actual["vida_jugador"] <= 0:
        estado_actual["terminado"] = True
        estado_actual["ganador"] = "NPC"
        registro.append("Tu equipo cae en combate.")
    else:
        estado_actual["turno"] += 1

    return {
        "estado": estado_actual,
        "registro": registro,
        "jugador": jugador,
        "npc": npc,
    }


# Función del jugador
def turno_jugador():
    print("\nAcciones del jugador:")
    print("1. Atacar")
    print("2. Defender")
    print("3. Acercarse")
    print("4. Alejarse")
    return input("Elige: ")


# Bucle principal del juego
def jugar():
    estado = crear_estado_inicial()

    while not estado["terminado"]:
        print(f"\n--- TURNO {estado['turno']} ---")
        print(f"Vida jugador: {estado['vida_jugador']}")
        print(f"Vida NPC: {estado['vida_npc']}")
        print(f"Distancia: {estado['distancia']}")

        accion = turno_jugador()
        try:
            resultado = resolver_turno(estado, accion)
        except ValueError:
            print("Acción inválida. Usa 1, 2, 3 o 4.")
            continue

        estado = resultado["estado"]

        print("\nResumen:")
        for evento in resultado["registro"][1:]:
            print("-", evento)

        npc = resultado["npc"]
        if npc:
            print(
                f"Lectura difusa NPC -> ataque: {npc['valor_ataque']:.2f}, "
                f"movimiento: {npc['valor_movimiento']:.2f}"
            )

    if estado["ganador"] == "Jugador":
        print("\nGanaste")
    else:
        print("\nPerdiste")


# Ejecutar el juego
if __name__ == "__main__":
    jugar()
