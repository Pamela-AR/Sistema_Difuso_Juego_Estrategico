# juego_difuso.py
# Cerebro difuso del NPC — Versión Agresiva (Mentalidad de Tiburón)
#

import json
from copy import deepcopy

from mamdani import LinguisticVar, Mamdani, trap_left, triangle, trap_right


# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────

VIDA_MAXIMA       = 100
DISTANCIA_MIN     = 0
DISTANCIA_MAX     = 100
DISTANCIA_INICIAL = 50
DANIO_JUGADOR     = 12
REDUCCION_DEFENSA = 8

DANIO_JUGADOR_MINIMO = 8   # daño a distancia máxima (40)
DANIO_JUGADOR_MAXIMO = 18  # daño pegado (distancia 0)

DISTANCIA_MIN_JUGADOR = 40;
DISTANCIA_MIN_NPC = 60;

SALTO_DISTANCIA   = 15;

# ─────────────────────────────────────────────
# VARIABLES LINGÜÍSTICAS — ENTRADAS
# ─────────────────────────────────────────────

distancia = LinguisticVar("Distancia", [0, 100], "u")
distancia.add_set("Cerca", trap_left(20, 45))       # 1 hasta 20, baja a 0 en 45
distancia.add_set("Media", triangle(25, 50, 75))    # pico en 50
distancia.add_set("Lejos", trap_right(55, 80))      # sube desde 55, plano a partir de 80

vida_npc = LinguisticVar("Vida_NPC", [0, 100], "%")
vida_npc.add_set("Baja",  trap_left(20, 40))
vida_npc.add_set("Media", triangle(25, 50, 75))
vida_npc.add_set("Alta",  trap_right(60, 80))

vida_jugador = LinguisticVar("Vida_Jugador", [0, 100], "%")
vida_jugador.add_set("Baja",  trap_left(20, 40))
vida_jugador.add_set("Media", triangle(25, 50, 75))
vida_jugador.add_set("Alta",  trap_right(60, 80))


# ─────────────────────────────────────────────
# VARIABLE LINGÜÍSTICA — SALIDA (4 acciones)
# ─────────────────────────────────────────────
# Distribución sobre [0, 100]:
#   Alejarse  → trap_left (0–25):   huir, zona estrecha
#   Defender  → triangle  (15–45):  cubrirse, zona estrecha
#   Acercarse → triangle  (38–72):  avanzar, zona central amplia
#   Atacar    → trap_right(60–100): golpear, domina el tercio superior
#
# Cruces aproximados (umbrales para interpretar_accion):
#   Alejarse  ∩ Defender  ≈ 20
#   Defender  ∩ Acercarse ≈ 42
#   Acercarse ∩ Atacar    ≈ 66

accion = LinguisticVar("Accion", [0, 100], "nivel")
accion.add_set("Alejarse",  trap_left(10, 25))
accion.add_set("Defender",  triangle(15, 30, 45))
accion.add_set("Acercarse", triangle(38, 55, 72))
accion.add_set("Atacar",    trap_right(60, 78))


# ─────────────────────────────────────────────
# SISTEMA MAMDANI + REGLAS (27 combinaciones)
# ─────────────────────────────────────────────

sistema = Mamdani(outputs=[accion], resolution=500)

# ── Distancia CERCA ───────────────────────────
# Con vida alta/media: ataca sin dudar, está en rango óptimo.
# Con vida baja: defiende solo si el jugador es fuerte; si no, golpe desesperado.
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Alta"),  (vida_jugador, "Alta")],  {accion: "Atacar"})
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Alta"),  (vida_jugador, "Media")], {accion: "Atacar"})
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Alta"),  (vida_jugador, "Baja")],  {accion: "Atacar"})
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Alta")],  {accion: "Atacar"})
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Media")], {accion: "Atacar"})
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Media"), (vida_jugador, "Baja")],  {accion: "Atacar"})
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Baja"),  (vida_jugador, "Alta")],  {accion: "Defender"})
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Baja"),  (vida_jugador, "Media")], {accion: "Atacar"})
sistema.add_rule([(distancia, "Cerca"), (vida_npc, "Baja"),  (vida_jugador, "Baja")],  {accion: "Atacar"})

# ── Distancia MEDIA ───────────────────────────
# Con vida alta/media: acercarse primero para asegurar el rango de ataque.
# Solo ataca directo si el jugador está muy débil (golpe de oportunidad).
# Con vida baja: huye si el jugador es fuerte, defiende si está equilibrado,
#                ataca si el jugador también está débil (golpe desesperado).
sistema.add_rule([(distancia, "Media"), (vida_npc, "Alta"),  (vida_jugador, "Alta")],  {accion: "Acercarse"})
sistema.add_rule([(distancia, "Media"), (vida_npc, "Alta"),  (vida_jugador, "Media")], {accion: "Acercarse"})
sistema.add_rule([(distancia, "Media"), (vida_npc, "Alta"),  (vida_jugador, "Baja")],  {accion: "Atacar"})
sistema.add_rule([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Alta")],  {accion: "Acercarse"})
sistema.add_rule([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Media")], {accion: "Acercarse"})
sistema.add_rule([(distancia, "Media"), (vida_npc, "Media"), (vida_jugador, "Baja")],  {accion: "Atacar"})
sistema.add_rule([(distancia, "Media"), (vida_npc, "Baja"),  (vida_jugador, "Alta")],  {accion: "Alejarse"})
sistema.add_rule([(distancia, "Media"), (vida_npc, "Baja"),  (vida_jugador, "Media")], {accion: "Defender"})
sistema.add_rule([(distancia, "Media"), (vida_npc, "Baja"),  (vida_jugador, "Baja")],  {accion: "Atacar"})

# ── Distancia LEJOS ───────────────────────────
# Con vida suficiente: siempre acercarse (no puede atacar desde lejos).
# Con vida baja: huye del jugador fuerte o equilibrado.
# Con vida baja y jugador débil: defiende — ambos están mal, espera cubierto
#   por si el jugador se acerca a rematar.
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Alta"),  (vida_jugador, "Alta")],  {accion: "Acercarse"})
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Alta"),  (vida_jugador, "Media")], {accion: "Acercarse"})
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Alta"),  (vida_jugador, "Baja")],  {accion: "Acercarse"})
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Media"), (vida_jugador, "Alta")],  {accion: "Acercarse"})
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Media"), (vida_jugador, "Media")], {accion: "Acercarse"})
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Media"), (vida_jugador, "Baja")],  {accion: "Acercarse"})
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Baja"),  (vida_jugador, "Alta")],  {accion: "Alejarse"})
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Baja"),  (vida_jugador, "Media")], {accion: "Alejarse"})
sistema.add_rule([(distancia, "Lejos"), (vida_npc, "Baja"),  (vida_jugador, "Baja")],  {accion: "Defender"})


# ─────────────────────────────────────────────
# ACCIONES DEL JUGADOR
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
        "turno":        1,
        "vida_jugador": VIDA_MAXIMA,
        "vida_npc":     VIDA_MAXIMA,
        "distancia":    DISTANCIA_INICIAL,
        "terminado":    False,
        "ganador":      None,
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
    Convierte el centroide [0-100] a una acción discreta.
    Umbrales alineados con los cruces matemáticos entre sets de salida.

    Retorna: (nombre_accion: str, daño_base: int)
    """
    if valor < 20:
        return "Alejarse",  0
    if valor < 42:
        return "Defender",  0
    if valor < 66:
        return "Acercarse", 0
    # Zona Atacar: daño escala de 8 a 16 según intensidad (66→100)
    intensidad = min(1.0, (valor - 66) / 34.0)
    return "Atacar", int(8 + intensidad * 8)


def calcular_danio_jugador(distancia):
    """
    Calcula el daño del jugador basado en la proximidad.
    Escala linealmente: a distancia 0 → daño máximo (20)
                        a distancia 40 → daño mínimo (8)
    """
    if distancia <= 0:
        return DANIO_JUGADOR_MAXIMO
    elif distancia >= 40:
        return DANIO_JUGADOR_MINIMO
    else:
        # Escala lineal: cuanto más cerca, más daño
        factor = 1.0 - (distancia / DISTANCIA_MIN_JUGADOR)
        return int(DANIO_JUGADOR_MINIMO + factor * (DANIO_JUGADOR_MAXIMO - DANIO_JUGADOR_MINIMO))


def _daño_en_limite(val_accion):
    """Daño cuando el NPC está pegado al jugador y no puede acercarse más."""
    intensidad = min(1.0, max(0.0, (val_accion - 66) / 34.0))
    return int(12 + intensidad * 8)


DESCRIPCIONES_NPC = {
    "Atacar":    "Bestia Difusa se lanza hacia ti con un ataque implacable.",
    "Defender":  "Bestia Difusa asume una postura defensiva firme.",
    "Acercarse": "Bestia Difusa recorta la distancia rápidamente.",
    "Alejarse":  "Bestia Difusa retrocede buscando refugio.",
}


def describir_accion_npc(accion_nombre):
    return DESCRIPCIONES_NPC.get(accion_nombre, "Bestia Difusa cambia de postura.")


# ─────────────────────────────────────────────
# TURNO DEL NPC
# ─────────────────────────────────────────────

def _extraer_datos_procesamiento(entradas, salidas):
    """Extrae datos detallados del procesamiento difuso para visualización."""
    from mamdani import _firing_strength
    
    # Fuzzificación
    fuzzificacion = {}
    for var, val in entradas.items():
        fuzzificacion[var.name] = {
            "valor": round(val, 2),
            "unidad": var.unit,
            "conjuntos": {k: round(v, 3) for k, v in var.fuzzify(val).items()},
        }
    
    # Reglas activadas (razonamiento)
    memberships = {var: var.fuzzify(val) for var, val in entradas.items()}
    reglas_activadas = []
    
    for idx, rule in enumerate(sistema.rules):
        alpha = _firing_strength(rule["ant"], rule["op"], memberships)
        if alpha > 0.001:  # Solo mostrar reglas significativas
            antecedentes_desc = []
            for clause in rule["ant"]:
                var, conj = clause[0], clause[1]
                negado = len(clause) == 3 and clause[2] == "NOT"
                antecedentes_desc.append({
                    "variable": var.name,
                    "conjunto": conj,
                    "negado": negado,
                    "valor_membresia": round(memberships[var][conj], 3),
                })
            
            consecuentes_desc = {}
            for var, conj in rule["cons"].items():
                consecuentes_desc[var.name] = conj
            
            reglas_activadas.append({
                "indice": idx,
                "antecedentes": antecedentes_desc,
                "operador": rule["op"],
                "firing_strength": round(alpha, 3),
                "consecuentes": consecuentes_desc,
            })
    
    # Agregación de salidas
    agregacion = {}
    for out_var in sistema.outputs:
        agg = sistema._infer_output(out_var, memberships)
        agregacion[out_var.name] = {
            "conjuntos": {k: round(v, 3) for k, v in agg.items()}
        }
    
    return {
        "fuzzificacion": fuzzificacion,
        "reglas_activadas": reglas_activadas,
        "agregacion": agregacion,
        "valor_salida": {var.name: round(val, 3) for var, val in salidas.items()},
    }


def turno_npc(distancia_val, vida_npc_val, vida_jugador_val):
    """
    Consulta el sistema Mamdani y decide la acción del NPC.

    Escribe un snapshot en 'estado_difuso.json' para herramientas externas
    de visualización (falla silenciosamente si el archivo está ocupado).

    Retorna: (accion_npc: str, daño_base: int, centroide: float, datos_procesamiento: dict)
    """
    entradas = {
        distancia:    distancia_val,
        vida_npc:     vida_npc_val,
        vida_jugador: vida_jugador_val,
    }
    salidas           = sistema.compute(entradas)
    valor_centroide   = salidas[accion]
    accion_npc, danio = interpretar_accion(valor_centroide)

    # Extraer datos de procesamiento
    datos_proc = _extraer_datos_procesamiento(entradas, salidas)

    try:
        with open("estado_difuso.json", "w") as f:
            json.dump(datos_proc, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

    return accion_npc, danio, valor_centroide, datos_proc


# ─────────────────────────────────────────────
# TURNO COMPLETO
# ─────────────────────────────────────────────

def resolver_turno(estado, accion_jugador):
    """
    Procesa un turno: acción del jugador → respuesta del NPC.

    Retorna dict con:
        estado   : estado actualizado del juego
        registro : lista de mensajes narrativos del turno
        jugador  : dict con acción, daño y mensaje del jugador
        npc      : dict con acción, daños y centroide del NPC
    """
    estado_actual = _normalizar_estado(estado)
    accion_jug    = ACCIONES_JUGADOR.get(str(accion_jugador), accion_jugador)

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
        if estado_actual["distancia"] <= DISTANCIA_MIN_JUGADOR:
            danio_jugador = calcular_danio_jugador(estado_actual["distancia"])
            estado_actual["vida_npc"] = limitar(
                estado_actual["vida_npc"] - danio_jugador, 0, VIDA_MAXIMA
            )
            jugador["danio"]   = danio_jugador
            jugador["mensaje"] = f"Tu ataque impacta con fuerza ({danio_jugador} pts de daño)."
        else:
            jugador["mensaje"] = f"Tu ataque falla porque el rival está muy lejos (necesitas dist ≤ {DISTANCIA_MIN_JUGADOR})."

    elif accion_jug == "defender":
        defensa            = True
        jugador["mensaje"] = "Te preparas para resistir el próximo golpe."

    elif accion_jug == "acercarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] - SALTO_DISTANCIA, DISTANCIA_MIN, DISTANCIA_MAX
        )
        jugador["mensaje"] = "Avanzas para cerrar la distancia."

    elif accion_jug == "alejarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] + SALTO_DISTANCIA, DISTANCIA_MIN, DISTANCIA_MAX
        )
        jugador["mensaje"] = "Retrocedes para ganar espacio."

    registro.append(jugador["mensaje"])

    # ¿El jugador mató al NPC?
    if estado_actual["vida_npc"] <= 0:
        estado_actual.update({"terminado": True, "ganador": "Jugador"})
        registro.append("¡La Bestia Difusa cae derrotada!")
        return {"estado": estado_actual, "registro": registro, "jugador": jugador, "npc": {}, "procesamiento_difuso": None}

    # ── Turno del NPC ─────────────────────────
    acc_npc, danio, val_accion, datos_proc = turno_npc(
        estado_actual["distancia"],
        estado_actual["vida_npc"],
        estado_actual["vida_jugador"],
    )

    # Redirigir si el NPC alcanzó un límite de distancia
    dist_min = estado_actual["distancia"] <= DISTANCIA_MIN + 5
    dist_max = estado_actual["distancia"] >= DISTANCIA_MAX - 5

    if acc_npc == "Acercarse" and dist_min:
        acc_npc = "Atacar"                  # pegado al jugador → muerde
        danio   = _daño_en_limite(val_accion)
    elif acc_npc == "Alejarse" and dist_max:
        acc_npc = "Defender"                # no puede huir más → se cubre
        danio   = 0

    npc = {
        "accion":         acc_npc,
        "danio_base":     danio,
        "valor_accion":   round(val_accion, 2),
        "danio_aplicado": 0,
        "ataque_conecto": False,
    }

    registro.append(describir_accion_npc(acc_npc))

    # Movimiento del NPC
    if acc_npc == "Acercarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] - 10, DISTANCIA_MIN, DISTANCIA_MAX
        )
    elif acc_npc == "Alejarse":
        estado_actual["distancia"] = limitar(
            estado_actual["distancia"] + 10, DISTANCIA_MIN, DISTANCIA_MAX
        )

    # Ataque del NPC (requiere dist ≤ 70)
    if acc_npc == "Atacar":
        if estado_actual["distancia"] <= DISTANCIA_MIN_NPC:
            danio_real = max(0, danio - REDUCCION_DEFENSA) if defensa else danio

            npc["danio_aplicado"] = danio_real
            npc["ataque_conecto"] = danio_real > 0
            estado_actual["vida_jugador"] = limitar(
                estado_actual["vida_jugador"] - danio_real, 0, VIDA_MAXIMA
            )

            if danio_real == 0:
                registro.append("Tu defensa neutraliza por completo la embestida.")
            elif defensa:
                registro.append(f"Tu guardia mitiga el impacto, pero recibes {danio_real} de daño.")
            else:
                registro.append(f"El ataque enemigo te desgarra y recibes {danio_real} de daño.")
        else:
            registro.append("El ataque de la Bestia se queda corto en el aire.")

    # ¿El NPC mató al jugador?
    if estado_actual["vida_jugador"] <= 0:
        estado_actual.update({"terminado": True, "ganador": "NPC"})
        registro.append("Tu barra de vida llega a cero...")
    else:
        estado_actual["turno"] += 1

    return {
        "estado":   estado_actual,
        "registro": registro,
        "jugador":  jugador,
        "npc":      npc,
        "procesamiento_difuso": datos_proc,
    }


# ─────────────────────────────────────────────
# BUCLE DE JUEGO — MODO CONSOLA
# ─────────────────────────────────────────────

def turno_jugador():
    print("\n  Acciones disponibles:")
    print("    1. Atacar    (requiere dist ≤ 60)")
    print("    2. Defender  (absorbe 8 pt de daño)")
    print(f"    3. Acercarse (-{SALTO_DISTANCIA} u.)")
    print(f"    4. Alejarse  (+{SALTO_DISTANCIA} u.)")
    return input("  Elige (1-4): ").strip()


def jugar():
    estado = crear_estado_inicial()
    print("═" * 50)
    print("   COMBATE DIFUSO — MODO DEPREDADOR ACTIVO")
    print("═" * 50)

    while not estado["terminado"]:
        print(f"\n{'─'*50}")
        print(f"  Turno {estado['turno']:>3}  │  "
              f"Tú: {estado['vida_jugador']:>3}%  │  "
              f"Bestia: {estado['vida_npc']:>3}%  │  "
              f"Dist: {estado['distancia']:>3}")
        print(f"{'─'*50}")

        accion_input = turno_jugador()
        try:
            resultado = resolver_turno(estado, accion_input)
        except ValueError:
            print("  ✗ Acción inválida. Ingresa 1, 2, 3 o 4.")
            continue

        estado = resultado["estado"]

        print()
        for evento in resultado["registro"][1:]:
            print(f"  › {evento}")

        npc_info = resultado["npc"]
        if npc_info:
            detalle = (f"  (daño base: {npc_info['danio_base']})"
                       if npc_info["accion"] == "Atacar" else "")
            print(f"  [difuso] centroide={npc_info['valor_accion']:.1f} "
                  f"→ {npc_info['accion']}{detalle}")

    print(f"\n{'═'*50}")
    if estado["ganador"] == "Jugador":
        print("  ¡VICTORIA! Sobreviviste al ataque de la Bestia.")
    else:
        print("  DERROTA. Has sido cazado.")
    print(f"{'═'*50}\n")


if __name__ == "__main__":
    jugar()