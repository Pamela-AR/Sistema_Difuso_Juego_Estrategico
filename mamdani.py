# mamdani.py — Librería básica de lógica difusa Mamdani
#              Soporta n entradas, m salidas, AND / OR / NOT en antecedentes

# ─────────────────────────────────────────────
# FUNCIONES DE MEMBRESÍA
# ─────────────────────────────────────────────

def trapecio_izquierdo(a, b):
    """Trapecio izquierdo: 1 si x <= a, decrece linealmente hasta 0 en b."""
    def f(x):
        if x <= a: return 1.0
        if x < b:  return (b - x) / (b - a)
        return 0.0
    return f

def trapecio(a, b, c, d):
    """Trapecio general: sube de a→b, plano b→c, baja c→d."""
    def f(x):
        if x <= a or x >= d: return 0.0
        if x < b:  return (x - a) / (b - a)
        if x <= c: return 1.0
        return (d - x) / (d - c)
    return f

def triangulo(a, b, c):
    """Triángulo: sube de a a b, baja de b a c."""
    def f(x):
        if x <= a or x >= c: return 0.0
        if x < b:  return (x - a) / (b - a)
        if x == b: return 1.0
        return (c - x) / (c - b)
    return f

def trapecio_derecho(a, b):
    """Trapecio derecho: crece desde a, 1 si x >= b."""
    def f(x):
        if x >= b: return 1.0
        if x > a:  return (x - a) / (b - a)
        return 0.0
    return f


# ─────────────────────────────────────────────
# VARIABLE LINGÜÍSTICA
# ─────────────────────────────────────────────

class VariableLinguistica:
    def __init__(self, nombre, universo, unidad=""):
        self.nombre    = nombre
        self.universo  = universo   # [min, max]
        self.unidad    = unidad
        self.conjuntos = {}         # nombre -> función de membresía

    def agregar_conjunto(self, nombre, fn):
        self.conjuntos[nombre] = fn
        return self

    def fusificar(self, x):
        """Devuelve {conjunto: grado} para el valor nítido x."""
        return {nombre: fn(x) for nombre, fn in self.conjuntos.items()}

    def __repr__(self):
        return f"VariableLinguistica({self.nombre}, conjuntos={list(self.conjuntos)})"


# ─────────────────────────────────────────────
# ANTECEDENTES COMPUESTOS
#
# Un antecedente es una lista de "cláusulas".
# Cada cláusula es una tupla:
#
#   (VariableLinguistica, "conjunto")          ← positivo
#   (VariableLinguistica, "conjunto", "NOT")   ← negado
#
# Las cláusulas se combinan con el operador global: "AND" | "OR"
#
# Ejemplos:
#   AND:  [ (distancia,"Cerca"), (hp,"Sano"), (borde,"Centro") ]
#   OR:   [ (hp,"Critico"), (borde,"Zona_Peligro") ]
#   NOT:  [ (distancia,"Lejos","NOT"), (borde,"Zona_Peligro") ]  ← AND con un NOT
# ─────────────────────────────────────────────

def _evaluar_clausula(clausula, membresias):
    """Evalúa una cláusula y devuelve su grado de membresía."""
    var, conj = clausula[0], clausula[1]
    negado    = len(clausula) == 3 and clausula[2] == "NOT"
    mu = membresias[var][conj]
    return 1.0 - mu if negado else mu

def _fuerza_activacion(antecedentes, op, membresias):
    """
    antecedentes : lista de cláusulas  [ (var, conj) | (var, conj, "NOT") ]
    op           : "AND" → min  |  "OR" → max
    """
    valores = [_evaluar_clausula(c, membresias) for c in antecedentes]
    return min(valores) if op == "AND" else max(valores)


# ─────────────────────────────────────────────
# SISTEMA MAMDANI  (n entradas, m salidas)
# ─────────────────────────────────────────────

class Mamdani:
    """
    Sistema Mamdani genérico con soporte AND / OR / NOT.

    agregar_regla(antecedentes, consecuentes, op)
    ───────────────────────────────────────
    antecedentes : lista de cláusulas
        [ (VariableLinguistica, "conjunto") ]              ← AND positivo simple
        [ (VariableLinguistica, "conjunto", "NOT") ]       ← negación
    consecuentes : {VariableLinguistica: "conjunto", ...}  ← m salidas
                 str  (atajo si hay 1 salida)
    op           : "AND" (por defecto) | "OR"

    calcular(entradas) → {VariableLinguistica: valor_nitido}
    """

    def __init__(self, salidas, resolucion=1000):
        self.salidas    = salidas if isinstance(salidas, list) else [salidas]
        self.resolucion = resolucion
        self.reglas     = []

    def agregar_regla(self, antecedentes: list, consecuentes, op="AND"):
        if isinstance(consecuentes, str):
            consecuentes = {self.salidas[0]: consecuentes}
        self.reglas.append({"ant": antecedentes, "cons": consecuentes, "op": op})

    # ── Razonamiento ──────────────────────────

    def _inferir_salida(self, var_salida, membresias):
        """Agrega alfas (máximo) de todas las reglas relevantes a var_salida."""
        agregados = {nombre: 0.0 for nombre in var_salida.conjuntos}
        for regla in self.reglas:
            if var_salida not in regla["cons"]:
                continue
            alpha = _fuerza_activacion(regla["ant"], regla["op"], membresias)
            conj  = regla["cons"][var_salida]
            agregados[conj] = max(agregados[conj], alpha)
        return agregados

    # ── Defusificación (centroide) ─────────────

    def _defusificar(self, var_salida, agregados):
        inf, sup = var_salida.universo
        paso   = (sup - inf) / self.resolucion
        num = den = 0.0
        x = inf
        while x <= sup:
            mu = max(
                min(alpha, var_salida.conjuntos[nombre](x))
                for nombre, alpha in agregados.items()
            )
            num += x * mu
            den += mu
            x   += paso
        return num / den if den != 0 else (inf + sup) / 2

    # ── API pública ───────────────────────────

    def calcular(self, entradas: dict, verboso=False):
        """
        entradas : {VariableLinguistica: valor_nitido, ...}
        verboso  : muestra fusificación y razonamiento en consola
        Retorna  : {VariableLinguistica: valor_nitido}
        """
        membresias = {var: var.fusificar(val) for var, val in entradas.items()}

        if verboso:
            print("[1] FUSIFICACIÓN")
            for var, mu in membresias.items():
                print(f"  {var.nombre:20s} → { {k: round(v,3) for k,v in mu.items()} }")

        resultados = {}
        for var_salida in self.salidas:
            agregados = self._inferir_salida(var_salida, membresias)

            if verboso:
                print(f"\n[2] RAZONAMIENTO → {var_salida.nombre}")
                for conj, alpha in agregados.items():
                    barra = "█" * int(alpha * 20)
                    print(f"  {conj:20s} α={round(alpha,3):.3f}  {barra}")

            valor_nitido = self._defusificar(var_salida, agregados)
            resultados[var_salida] = valor_nitido

            if verboso:
                print(f"[3] DEFUSIFICACIÓN → {round(valor_nitido,3)} {var_salida.unidad}")

        return resultados