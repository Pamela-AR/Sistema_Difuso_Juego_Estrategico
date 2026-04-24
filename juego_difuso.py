# juego_difuso.py
# Cerebro difuso del NPC — VERSIÓN AGRESIVA (Mentalidad de Tiburón)

import json 
from copy import deepcopy
from mamdani import VariableLinguistica, Mamdani, trapecio_izquierdo, triangulo, trapecio_derecho

VIDA_MAXIMA        = 100
DISTANCIA_MIN      = 0
DISTANCIA_MAX      = 100
DISTANCIA_INICIAL  = 50
DANIO_JUGADOR      = 12
REDUCCION_DEFENSA  = 8

# ─────────────────────────────────────────────
# VARIABLES LINGÜÍSTICAS — ENTRADAS
# ─────────────────────────────────────────────

distancia = VariableLinguistica("Distancia", [0, 100], "u")
distancia.agregar_conjunto("Cerca", trapecio_izquierdo(20, 45))          
distancia.agregar_conjunto("Media", triangulo(25, 50, 75))       
distancia.agregar_conjunto("Lejos", trapecio_derecho(55, 80))        

vida_npc = VariableLinguistica("Vida_NPC", [0, 100], "%")
vida_npc.agregar_conjunto("Baja",  trapecio_izquierdo(20, 40))
vida_npc.agregar_conjunto("Media", triangulo(25, 50, 75))
vida_npc.agregar_conjunto("Alta",  trapecio_derecho(60, 80))

vida_jugador = VariableLinguistica("Vida_Jugador", [0, 100], "%")
vida_jugador.agregar_conjunto("Baja",  trapecio_izquierdo(20, 40))
vida_jugador.agregar_conjunto("Media", triangulo(25, 50, 75))
vida_jugador.agregar_conjunto("Alta",  trapecio_derecho(60, 80))

# ─────────────────────────────────────────────
# VARIABLE LINGÜÍSTICA — SALIDA (Mentalidad de Tiburón Real)
# ─────────────────────────────────────────────
accion = VariableLinguistica("Accion", [0, 100], "nivel")

# Alejarse: Cae rapidísimo. Solo ocupa del 0 al 30.
accion.agregar_conjunto("Alejarse",  trapecio_izquierdo(15, 30))

# Defender: Muy estrecho (20 a 50). Solo cae aquí si está 100% seguro de defender.
accion.agregar_conjunto("Defender",  triangulo(20, 35, 50))

# Acercarse: Gigantesco (40 a 80). Se traga todo el centro de indecisión.
accion.agregar_conjunto("Acercarse", triangulo(40, 60, 80))

# Atacar: Empieza desde el 70. Ocupa todo el tercio final.
accion.agregar_conjunto("Atacar",    trapecio_derecho(70, 85))

# ─────────────────────────────────────────────
# SISTEMA MAMDANI (27 Reglas Explícitas)
# ─────────────────────────────────────────────
# Nota: La librería actualizada usa 'salidas' en lugar de 'outputs'
sistema = Mamdani(salidas=[accion], resolucion=500)

# ── Reglas: Distancia CERCA (9 reglas) ───────────────────
sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Alta"), (vida_jugador, "Alta")], {accion: "Atacar"})
sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Alta"), (vida_jugador, "Media")], {accion: "Atacar"})
sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Alta"), (vida_jugador, "Baja")], {accion: "Atacar"})

sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Alta")], {accion: "Atacar"})
sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Media")], {accion: "Atacar"})
sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Baja")], {accion: "Atacar"})

sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Baja"), (vida_jugador, "Alta")], {accion: "Defender"})
sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Baja"), (vida_jugador, "Media")], {accion: "Atacar"})
sistema.agregar_regla([(distancia, "Cerca"), (vida_npc, "Baja"), (vida_jugador, "Baja")], {accion: "Atacar"})

# ── Reglas: Distancia MEDIA (9 reglas) ───────────────────
sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Alta"), (vida_jugador, "Alta")], {accion: "Atacar"})
sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Alta"), (vida_jugador, "Media")], {accion: "Atacar"})
sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Alta"), (vida_jugador, "Baja")], {accion: "Atacar"})

sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Alta")], {accion: "Atacar"}) 
sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Media")], {accion: "Atacar"})
sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Baja")], {accion: "Atacar"})

sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Baja"), (vida_jugador, "Alta")], {accion: "Alejarse"})
sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Baja"), (vida_jugador, "Media")], {accion: "Defender"})
sistema.agregar_regla([(distancia, "Media"), (vida_npc, "Baja"), (vida_jugador, "Baja")], {accion: "Atacar"})

# ── Reglas: Distancia LEJOS (9 reglas) ───────────────────
sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Alta"), (vida_jugador, "Alta")], {accion: "Acercarse"})
sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Alta"), (vida_jugador, "Media")], {accion: "Acercarse"})
sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Alta"), (vida_jugador, "Baja")], {accion: "Acercarse"})

sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Media"), (vida_jugador, "Alta")], {accion: "Acercarse"}) 
sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Media"), (vida_jugador, "Media")], {accion: "Acercarse"})
sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Media"), (vida_jugador, "Baja")], {accion: "Acercarse"})

sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Baja"), (vida_jugador, "Alta")], {accion: "Alejarse"})
sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Baja"), (vida_jugador, "Media")], {accion: "Alejarse"})
sistema.agregar_regla([(distancia, "Lejos"), (vida_npc, "Baja"), (vida_jugador, "Baja")], {accion: "Defender"})

# ─────────────────────────────────────────────
# CONSTANTES DE JUEGO
# ─────────────────────────────────────────────

ACCIONES_JUGADOR = {
    "1": "atacar",
    "2": "defender",
    "3": "acercarse",
    "4": "alejarse",
}

ACCIONES_DISPONIBLES = {
    "atacar":    {"nombre": "Atacar",    "descripcion": "Golpea si estás a rango medio o corto."},
    "defender":  {"nombre": "Defender",  "descripcion": "Reduce parte del daño recibido este turno."},
    "acercarse": {"nombre": "Acercarse", "descripcion": "Reduce la distancia para entrar en rango."},
    "alejarse":  {"nombre": "Alejarse",  "descripcion": "Aumenta la distancia para forzar al NPC a moverse."},
}

# ─────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────

def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))

def crear_estado_inicial():
    return {
        "turno":         1,
        "vida_jugador":  VIDA_MAXIMA,
        "vida_npc":      VIDA_MAXIMA,
        "distancia":     DISTANCIA_INICIAL,
        "terminado":     False,
        "ganador":       None,
    }

def _normalizar_estado(estado):
    base = crear_estado_inicial()
    base.update(deepcopy(estado or {}))
    base["turno"]        = max(1, int(base["turno"]))
    base["vida_jugador"] = limitar(int(base["vida_jugador"]), 0, VIDA_MAXIMA)
    base["vida_npc"]     = limitar(int(base["vida_npc"]),     0, VIDA_MAXIMA)
    base["distancia"]    = limitar(int(base["distancia"]),    DISTANCIA_MIN, DISTANCIA_MAX)
    base["terminado"]    = bool(base["terminado"])
    base["ganador"]      = base["ganador"] if base["ganador"] in {"Jugador", "NPC"} else None
    return base

# ─────────────────────────────────────────────
# INTERPRETACIÓN DE SALIDA DIFUSA
# ─────────────────────────────────────────────

def interpretar_accion(valor):
    """
    Umbrales agresivos basados en los cruces matemáticos:
    Alejarse ∩ Defender ≈ 25
    Defender ∩ Acercarse ≈ 45
    Acercarse ∩ Atacar ≈ 75
    """
    if valor < 25:
        return "Alejarse",  0
    elif valor < 45:
        return "Defender",  0
    elif valor < 75:
        return "Acercarse", 0
    else:
        intensidad = min(1.0, (valor - 75) / 25.0)
        danio = int(8 + intensidad * 8)
        return "Atacar", danio

def describir_accion_npc(accion_nombre):
    descripciones = {
        "Atacar":    "Bestia Difusa se lanza hacia ti con un ataque implacable.",
        "Defender":  "Bestia Difusa asume una postura defensiva firme.",
        "Acercarse": "Bestia Difusa recorta la distancia rápidamente.",
        "Alejarse":  "Bestia Difusa retrocede buscando refugio.",
    }
    return descripciones.get(accion_nombre, "Bestia Difusa cambia de postura.")


# ─────────────────────────────────────────────
# LÓGICA DE TURNO DEL NPC
# ─────────────────────────────────────────────

def turno_npc(distancia_val, vida_npc_val, vida_jugador_val):
    entradas = {
        distancia:    distancia_val,
        vida_npc:     vida_npc_val,
        vida_jugador: vida_jugador_val,
    }
    # Ahora usamos .calcular() en lugar de .compute()
    salidas_difusas = sistema.calcular(entradas)
    valor_centroide = salidas_difusas[accion]
    accion_npc, danio = interpretar_accion(valor_centroide)
    
    try:
        with open("estado_difuso.json", "w") as f:
            json.dump({
                "distancia": distancia_val,
                "vida_npc": vida_npc_val,
                "vida_jugador": vida_jugador_val,
                "accion_valor": valor_centroide,
                "accion_nombre": accion_npc
            }, f)
    except:
        pass

    return accion_npc, danio, valor_centroide

# ─────────────────────────────────────────────
# LÓGICA DE TURNO COMPLETO
# ─────────────────────────────────────────────

def resolver_turno(estado, accion_jugador):
    estado_actual = _normalizar_estado(estado)
    accion_jug = ACCIONES_JUGADOR.get(str(accion_jugador), accion_jugador)

    if accion_jug not in ACCIONES_DISPONIBLES:
        raise ValueError("Acción no válida.")

    if estado_actual["terminado"]:
        return {
            "estado":   estado_actual,
            "registro": ["La partida ya terminó. Reinicia para volver a jugar."],
            "jugador":  {},
            "npc":      {},
        }

    registro = [f"Turno {estado_actual['turno']}"]
    defensa  = False
    jugador  = {"accion": accion_jug, "danio": 0, "mensaje": ""}

    # ── Acción del jugador ────────────────────
    if accion_jug == "atacar":
        if estado_actual["distancia"] <= 60:
            estado_actual["vida_npc"] = limitar(
                estado_actual["vida_npc"] - DANIO_JUGADOR, 0, VIDA_MAXIMA
            )
            jugador["danio"]   = DANIO_JUGADOR
            jugador["mensaje"] = "Tu ataque impacta con fuerza."
        else:
            jugador["mensaje"] = "Tu ataque falla porque el rival está muy lejos (necesitas <= 60)."

    elif accion_jug == "defender":
        defensa          = True
        jugador["mensaje"] = "Te preparas para resistir el próximo golpe."

    elif accion_jug == "acercarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] - 15, DISTANCIA_MIN, DISTANCIA_MAX
        )
        jugador["mensaje"] = "Avanzas para cerrar la distancia."

    elif accion_jug == "alejarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] + 15, DISTANCIA_MIN, DISTANCIA_MAX
        )
        jugador["mensaje"] = "Retrocedes para ganar espacio."

    registro.append(jugador["mensaje"])

    if estado_actual["vida_npc"] <= 0:
        estado_actual["terminado"] = True
        estado_actual["ganador"]   = "Jugador"
        registro.append("¡La Bestia Difusa cae derrotada!")
        return {"estado": estado_actual, "registro": registro, "jugador": jugador, "npc": {}}

    # ── Turno del NPC ─────────────────────────
    acc_npc, danio, val_accion = turno_npc(
        estado_actual["distancia"],
        estado_actual["vida_npc"],
        estado_actual["vida_jugador"],
    )

    dist_min_alcanzada = estado_actual["distancia"] <= DISTANCIA_MIN + 5
    dist_max_alcanzada = estado_actual["distancia"] >= DISTANCIA_MAX - 5

    # Si el NPC quiere acercarse pero ya está al límite mínimo → Atacar
    # Si el NPC quiere alejarse pero ya está al límite máximo → Defender
    if acc_npc == "Acercarse" and dist_min_alcanzada:
        acc_npc = "Atacar"
        danio   = int(12 + ((val_accion - 74) / 26.0) * 8)
    elif acc_npc == "Alejarse" and dist_max_alcanzada:
        acc_npc = "Defender"
        danio   = 0

    npc = {
        "accion":         acc_npc,
        "danio_base":     danio,
        "valor_accion":   round(val_accion, 2),
        "danio_aplicado": 0,
        "ataque_conecto": False,
    }

    registro.append(describir_accion_npc(acc_npc))

    # Movimiento NPC
    if acc_npc == "Acercarse":
        estado_actual["distancia"] = limitar(estado_actual["distancia"] - 10, DISTANCIA_MIN, DISTANCIA_MAX)
    elif acc_npc == "Alejarse":
        estado_actual["distancia"] = limitar(estado_actual["distancia"] + 10, DISTANCIA_MIN, DISTANCIA_MAX)

    # Ataque NPC
    if acc_npc == "Atacar":
        if estado_actual["distancia"] <= 70:
            danio_real = max(0, danio - REDUCCION_DEFENSA) if defensa else danio

            npc["danio_aplicado"] = danio_real
            npc["ataque_conecto"] = danio_real > 0
            estado_actual["vida_jugador"] = limitar(
                estado_actual["vida_jugador"] - danio_real, 0, VIDA_MAXIMA
            )

            if danio_real > 0:
                if defensa:
                    registro.append(f"Tu guardia mitiga el impacto, pero recibes {danio_real} de daño.")
                else:
                    registro.append(f"El ataque enemigo te desgarra y recibes {danio_real} de daño.")
            else:
                registro.append("Tu defensa neutraliza por completo la embestida.")
        else:
            registro.append("El ataque de la Bestia se queda corto en el aire.")

    if estado_actual["vida_jugador"] <= 0:
        estado_actual["terminado"] = True
        estado_actual["ganador"]   = "NPC"
        registro.append("Tu barra de vida llega a cero...")
    else:
        estado_actual["turno"] += 1

    return {
        "estado":   estado_actual,
        "registro": registro,
        "jugador":  jugador,
        "npc":      npc,
    }

# ─────────────────────────────────────────────
# BUCLE DE JUEGO (modo consola)
# ─────────────────────────────────────────────

def turno_jugador():
    print("\nAcciones del jugador:")
    print("  1. Atacar    (requiere dist <= 60)")
    print("  2. Defender  (absorbe 8 pt de daño)")
    print("  3. Acercarse (-15m)")
    print("  4. Alejarse  (+15m)")
    return input("Elige (1-4): ").strip()

def jugar():
    estado = crear_estado_inicial()
    print("═" * 50)
    print("   COMBATE DIFUSO — MODO DEPREDADOR ACTIVO")
    print("═" * 50)

    while not estado["terminado"]:
        print(f"\n{'─'*50}")
        print(f" Turno {estado['turno']:>3}  |  "
              f"Tú: {estado['vida_jugador']:>3}%  |  "
              f"Bestia: {estado['vida_npc']:>3}%  |  "
              f"Dist: {estado['distancia']:>3}m")
        print(f"{'─'*50}")

        accion = turno_jugador()
        try:
            resultado = resolver_turno(estado, accion)
        except ValueError:
            print("  ✗ Acción inválida. Ingresa 1, 2, 3 o 4.")
            continue

        estado = resultado["estado"]

        print()
        for evento in resultado["registro"][1:]:
            print(f"  › {evento}")

        npc_info = resultado["npc"]
        if npc_info:
            print(f"  [difuso] centroide={npc_info['valor_accion']:.1f} "
                  f"→ {npc_info['accion']}"
                  + (f" (Daño base: {npc_info['danio_base']})" if npc_info["accion"] == "Atacar" else ""))

    print(f"\n{'═'*50}")
    if estado["ganador"] == "Jugador":
        print("  ¡VICTORIA! Sobreviviste al ataque de la Bestia.")
    else:
        print("  DERROTA. Has sido cazado.")
    print(f"{'═'*50}\n")

if __name__ == "__main__":
    jugar()