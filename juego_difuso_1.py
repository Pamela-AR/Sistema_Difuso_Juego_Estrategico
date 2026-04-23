#Importando la librería de lógica difusa Mamdani
from mamdani import LinguisticVar, Mamdani, trap_left, triangle, trap_right
#Definiendo las variables lingüísticas para el juego estratégico
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

#Funciones auxiliares para interpretar los resultados de las salidas difusas en acciones concretas del juego    
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
    vida_j = 100
    vida_e = 100
    dist = 50
    turno = 1

    while vida_j > 0 and vida_e > 0:
        print(f"\n--- TURNO {turno} ---")
        print(f"Vida jugador: {vida_j}")
        print(f"Vida NPC: {vida_e}")
        print(f"Distancia: {dist}")

        accion = turno_jugador()
        defensa = False

        if accion == "1":
            if dist <= 60:
                vida_e -= 12
                print("Atacaste al NPC")
            else:
                print("Muy lejos")
        elif accion == "2":
            defensa = True
            print("Defensa activada")
        elif accion == "3":
            dist = max(0, dist - 15)
            print("Te acercas")
        elif accion == "4":
            dist = min(100, dist + 15)
            print("Te alejas")

        if vida_e <= 0:
            break

        acc_atq, danio, acc_mov, val_atq, val_mov = turno_npc(dist, vida_e, vida_j)

        print("\nNPC:")
        print("Ataque:", acc_atq, f"{val_atq:.2f}")
        print("Movimiento:", acc_mov, f"{val_mov:.2f}")

        if acc_mov == "Acercarse":
            dist = max(0, dist - 10)
        elif acc_mov == "Retroceder":
            dist = min(100, dist + 10)

        if acc_atq not in ["Huir", "Defender"]:
            if dist <= 70:
                if defensa:
                    danio = max(0, danio - 8)
                vida_j -= danio
                print("NPC daño:", danio)
        elif acc_atq == "Defender":
            print("NPC se defiende")

        vida_j = max(0, vida_j)
        vida_e = max(0, vida_e)
        turno += 1

    if vida_j <= 0:
        print("\nPerdiste")
    else:
        print("\nGanaste")

# Ejecutar el juego
if __name__ == "__main__":
    jugar()