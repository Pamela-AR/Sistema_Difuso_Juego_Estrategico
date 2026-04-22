# mamdani.py — Librería básica de lógica difusa Mamdani
#              Soporta n entradas, m salidas, AND / OR / NOT en antecedentes


# ─────────────────────────────────────────────
# FUNCIONES DE MEMBRESÍA
# ─────────────────────────────────────────────

def trap_left(a, b):
    """Trapecio izquierdo: 1 si x <= a, decrece linealmente hasta 0 en b."""
    def f(x):
        if x <= a: return 1.0
        if x < b:  return (b - x) / (b - a)
        return 0.0
    return f

def trapezoid(a, b, c, d):
    """Trapecio general: sube de a→b, plano b→c, baja c→d."""
    def f(x):
        if x <= a or x >= d: return 0.0
        if x < b:  return (x - a) / (b - a)
        if x <= c: return 1.0
        return (d - x) / (d - c)
    return f

def triangle(a, b, c):
    """Triángulo: sube de a a b, baja de b a c."""
    def f(x):
        if x <= a or x >= c: return 0.0
        if x < b:  return (x - a) / (b - a)
        if x == b: return 1.0
        return (c - x) / (c - b)
    return f

def trap_right(a, b):
    """Trapecio derecho: crece desde a, 1 si x >= b."""
    def f(x):
        if x >= b: return 1.0
        if x > a:  return (x - a) / (b - a)
        return 0.0
    return f


# ─────────────────────────────────────────────
# VARIABLE LINGÜÍSTICA
# ─────────────────────────────────────────────

class LinguisticVar:
    def __init__(self, name, universe, unit=""):
        self.name     = name
        self.universe = universe   # [min, max]
        self.unit     = unit
        self.sets     = {}         # nombre -> función de membresía

    def add_set(self, name, fn):
        self.sets[name] = fn
        return self

    def fuzzify(self, x):
        """Devuelve {conjunto: grado} para el valor crisp x."""
        return {name: fn(x) for name, fn in self.sets.items()}

    def __repr__(self):
        return f"LinguisticVar({self.name}, sets={list(self.sets)})"


# ─────────────────────────────────────────────
# ANTECEDENTES COMPUESTOS
#
# Un antecedente es una lista de "cláusulas".
# Cada cláusula es una tupla:
#
#   (LinguisticVar, "conjunto")          ← positivo
#   (LinguisticVar, "conjunto", "NOT")   ← negado
#
# Las cláusulas se combinan con el operador global: "AND" | "OR"
#
# Ejemplos:
#   AND:  [ (dist,"Close"), (hp,"Healthy"), (edge,"Center") ]
#   OR:   [ (hp,"Critical"), (edge,"Danger_Zone") ]
#   NOT:  [ (dist,"Far_Away","NOT"), (edge,"Danger_Zone") ]  ← AND con un NOT
# ─────────────────────────────────────────────

def _eval_clause(clause, memberships):
    """Evalúa una cláusula y devuelve su grado de membresía."""
    var, conj = clause[0], clause[1]
    negated   = len(clause) == 3 and clause[2] == "NOT"
    mu = memberships[var][conj]
    return 1.0 - mu if negated else mu

def _firing_strength(antecedents, op, memberships):
    """
    antecedents : lista de cláusulas  [ (var, conj) | (var, conj, "NOT") ]
    op          : "AND" → min  |  "OR" → max
    """
    values = [_eval_clause(c, memberships) for c in antecedents]
    return min(values) if op == "AND" else max(values)


# ─────────────────────────────────────────────
# SISTEMA MAMDANI  (n entradas, m salidas)
# ─────────────────────────────────────────────

class Mamdani:
    """
    Sistema Mamdani genérico con soporte AND / OR / NOT.

    add_rule(antecedents, consequents, op)
    ───────────────────────────────────────
    antecedents : lista de cláusulas
        [ (LinguisticVar, "set") ]               ← AND positivo simple
        [ (LinguisticVar, "set", "NOT") ]        ← negación
    consequents : {LinguisticVar: "set", ...}    ← m salidas
                  str  (atajo si hay 1 salida)
    op          : "AND" (default) | "OR"

    compute(inputs) → {LinguisticVar: valor_crisp}
    """

    def __init__(self, outputs, resolution=1000):
        self.outputs    = outputs if isinstance(outputs, list) else [outputs]
        self.resolution = resolution
        self.rules      = []

    def add_rule(self, antecedents: list, consequents, op="AND"):
        if isinstance(consequents, str):
            consequents = {self.outputs[0]: consequents}
        self.rules.append({"ant": antecedents, "cons": consequents, "op": op})

    # ── Razonamiento ──────────────────────────

    def _infer_output(self, output_var, memberships):
        """Agrega alfas (máximo) de todas las reglas relevantes a output_var."""
        aggregated = {name: 0.0 for name in output_var.sets}
        for rule in self.rules:
            if output_var not in rule["cons"]:
                continue
            alpha = _firing_strength(rule["ant"], rule["op"], memberships)
            conj  = rule["cons"][output_var]
            aggregated[conj] = max(aggregated[conj], alpha)
        return aggregated

    # ── Defusificación (centroide) ─────────────

    def _defuzzify(self, output_var, aggregated):
        lo, hi = output_var.universe
        step   = (hi - lo) / self.resolution
        num = den = 0.0
        x = lo
        while x <= hi:
            mu = max(
                min(alpha, output_var.sets[name](x))
                for name, alpha in aggregated.items()
            )
            num += x * mu
            den += mu
            x   += step
        return num / den if den != 0 else (lo + hi) / 2

    # ── API pública ───────────────────────────

    def compute(self, inputs: dict, verbose=False):
        """
        inputs  : {LinguisticVar: valor_crisp, ...}
        verbose : muestra fuzzificación y razonamiento
        Retorna : {LinguisticVar: valor_crisp}
        """
        memberships = {var: var.fuzzify(val) for var, val in inputs.items()}

        if verbose:
            print("[1] FUZZIFICACIÓN")
            for var, mu in memberships.items():
                print(f"  {var.name:20s} → { {k: round(v,3) for k,v in mu.items()} }")

        results = {}
        for out_var in self.outputs:
            aggregated = self._infer_output(out_var, memberships)

            if verbose:
                print(f"\n[2] RAZONAMIENTO → {out_var.name}")
                for conj, alpha in aggregated.items():
                    bar = "█" * int(alpha * 20)
                    print(f"  {conj:20s} α={round(alpha,3):.3f}  {bar}")

            crisp = self._defuzzify(out_var, aggregated)
            results[out_var] = crisp

            if verbose:
                print(f"[3] DEFUSIFICACIÓN → {round(crisp,3)} {out_var.unit}")

        return results