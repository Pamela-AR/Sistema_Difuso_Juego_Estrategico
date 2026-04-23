# Documentación técnica — `juego_difuso.py`
Motor de IA para combate por turnos con lógica difusa Mamdani

---

## 1. Visión general

El juego es un combate por turnos entre el **Jugador** y la **Bestia Difusa**. Ambos tienen 100 PS. Cada turno el jugador elige una acción, luego la Bestia responde con una decisión tomada por un sistema de lógica difusa Mamdani en tiempo real.

```
Jugador elige acción
        ↓
Se aplica el efecto del jugador (daño, movimiento, guardia)
        ↓
Motor Mamdani evalúa el estado actual → devuelve un centroide [0–100]
        ↓
El centroide se interpreta como una acción discreta del NPC
        ↓
Se aplica la acción del NPC (daño, movimiento)
        ↓
Se actualiza el estado para el turno siguiente
```

---

## 2. Estado del juego

Cada turno se representa como un diccionario con estos campos:

| Campo | Tipo | Descripción |
|---|---|---|
| `turno` | int | Número de turno actual (empieza en 1) |
| `vida_jugador` | int | PS del jugador [0–100] |
| `vida_npc` | int | PS de la Bestia [0–100] |
| `distancia` | int | Separación entre ambos combatientes [0–100] |
| `terminado` | bool | `True` cuando uno de los dos llega a 0 PS |
| `ganador` | str\|None | `"Jugador"`, `"NPC"`, o `None` |

La distancia inicial es **50 u**. El tablero va de 0 (pegados) a 100 (máximo alejamiento).

---

## 3. Acciones del jugador

El jugador elige exactamente una acción por turno. Siempre actúa **antes** que el NPC — si el jugador mata a la Bestia, el NPC no llega a responder.

| Tecla | Acción | Efecto |
|---|---|---|
| `1` | **Atacar** | Inflige daño si `distancia ≤ 40`. El daño escala con la proximidad. |
| `2` | **Defender** | No inflige daño. Reduce en 8 pts el próximo golpe del NPC. |
| `3` | **Acercarse** | Reduce la distancia en **−15 u**. |
| `4` | **Alejarse** | Aumenta la distancia en **+15 u**. |

### Daño del jugador por distancia

El daño no es fijo — escala linealmente entre el mínimo y el máximo según qué tan cerca está el jugador:

```
dist = 0  → 18 pts   (máximo)
dist = 10 → 15 pts
dist = 20 → 13 pts
dist = 30 → 10 pts
dist ≥ 40 →  8 pts   (mínimo, límite de rango)
dist > 40 →  falla, no conecta
```

**Fórmula:**
```python
factor = 1.0 - (distancia / 40)
daño   = int(8 + factor * (18 - 8))
```

---

## 4. Motor difuso Mamdani

La Bestia no tiene lógica `if/else`. Su decisión surge del algoritmo Mamdani aplicado sobre el estado actual del combate.

### 4.1 Variables de entrada (3)

#### `Distancia` — [0, 100] u

Qué tan separados están los combatientes.

| Conjunto | Forma | Rango activo |
|---|---|---|
| `Cerca` | Trapecio izquierdo | 0–45 (plano hasta 20, baja a 0 en 45) |
| `Media` | Triángulo | 25–75 (pico en 50) |
| `Lejos` | Trapecio derecho | 55–100 (sube desde 55, plano desde 80) |

#### `Vida_NPC` — [0, 100] %

PS actuales de la Bestia.

| Conjunto | Forma | Rango activo |
|---|---|---|
| `Baja` | Trapecio izquierdo | 0–40 (plano hasta 20, baja a 0 en 40) |
| `Media` | Triángulo | 25–75 (pico en 50) |
| `Alta` | Trapecio derecho | 60–100 (sube desde 60, plano desde 80) |

#### `Vida_Jugador` — [0, 100] %

PS actuales del jugador. Misma forma que `Vida_NPC`.

---

### 4.2 Variable de salida (1)

#### `Accion` — [0, 100]

Una sola variable de salida que codifica las 4 posibles acciones del NPC en una escala continua.

| Conjunto | Forma | Rango activo | Zona |
|---|---|---|---|
| `Alejarse` | Trapecio izquierdo | 0–25 | 0–20 |
| `Defender` | Triángulo | 15–45 (pico en 30) | 20–42 |
| `Acercarse` | Triángulo | 38–72 (pico en 55) | 42–66 |
| `Atacar` | Trapecio derecho | 60–100 (sube desde 60, plano desde 78) | 66–100 |

Los conjuntos se solapan deliberadamente para que el centroide resultante sea sensible a transiciones graduales entre estados.

---

### 4.3 Base de reglas (27 combinaciones)

Una regla por cada combinación posible de los 3 conjuntos de cada variable de entrada (3 × 3 × 3 = 27). Todas usan el operador **AND** (mínimo).

#### Zona CERCA

| vida_npc | vida_jugador | → acción | Razonamiento |
|---|---|---|---|
| Alta | Alta | Atacar | En rango y sano — ataca sin dudar |
| Alta | Media | Atacar | Ventaja de vida — presiona |
| Alta | Baja | Atacar | Jugador débil — remata |
| Media | Alta | Atacar | Aún tiene fuerza suficiente |
| Media | Media | Atacar | Combate parejo — agresivo |
| Media | Baja | Atacar | Jugador débil — aprovecha |
| Baja | Alta | **Defender** | NPC mal y jugador fuerte — única situación donde no ataca |
| Baja | Media | Atacar | Golpe desesperado |
| Baja | Baja | Atacar | Ambos mal — el que golpea primero gana |

#### Zona MEDIA

| vida_npc | vida_jugador | → acción | Razonamiento |
|---|---|---|---|
| Alta | Alta | Acercarse | Necesita entrar en rango para atacar |
| Alta | Media | Acercarse | Avanza con ventaja |
| Alta | Baja | **Atacar** | Jugador débil — golpe de oportunidad aunque esté lejos |
| Media | Alta | Acercarse | Aún puede ganar si entra en rango |
| Media | Media | Acercarse | Neutro — busca posición |
| Media | Baja | **Atacar** | Jugador débil — oportunidad |
| Baja | Alta | **Alejarse** | NPC mal y jugador fuerte — única huida a distancia media |
| Baja | Media | Defender | Equilibrado pero dañado — se cubre |
| Baja | Baja | Atacar | Ambos mal — apuesta todo |

#### Zona LEJOS

| vida_npc | vida_jugador | → acción | Razonamiento |
|---|---|---|---|
| Alta | Alta | Acercarse | Siempre se acerca si tiene vida — no puede atacar desde lejos |
| Alta | Media | Acercarse | Ídem |
| Alta | Baja | Acercarse | Ídem — persigue al jugador débil |
| Media | Alta | Acercarse | Ídem |
| Media | Media | Acercarse | Ídem |
| Media | Baja | Acercarse | Ídem — persigue |
| Baja | Alta | **Alejarse** | NPC crítico y jugador fuerte — huye |
| Baja | Media | **Alejarse** | NPC crítico — busca distancia |
| Baja | Baja | **Defender** | Ambos mal y lejos — espera cubierto |

---

### 4.4 Pipeline Mamdani paso a paso

**Ejemplo:** `distancia=50, vida_npc=70, vida_jugador=30`

**Paso 1 — Fuzzificación**
```
distancia=50  → Cerca: 0.0,  Media: 1.0,  Lejos: 0.0
vida_npc=70   → Baja:  0.0,  Media: 0.33, Alta:  0.5
vida_jugador=30→ Baja:  0.5,  Media: 0.2,  Alta:  0.0
```

**Paso 2 — Razonamiento (disparo de reglas)**
Cada regla calcula su `alpha = min(antecedentes)`:

```
Media ∩ Alta ∩ Baja  = min(1.0, 0.5, 0.5) = 0.5  → Atacar
Media ∩ Alta ∩ Media = min(1.0, 0.5, 0.2) = 0.2  → Atacar
Media ∩ Media ∩ Baja = min(1.0, 0.33, 0.5) = 0.33 → Atacar
...
```

**Paso 3 — Agregación**
Para cada conjunto de salida se toma el `max` de todos los alphas que apuntan a él:
```
Atacar    → max(0.5, 0.2, 0.33, ...) = 0.5
Acercarse → max(...)  = ...
...
```

**Paso 4 — Defusificación (centroide)**
```
         Σ  x · μ_agregado(x)
salida = ─────────────────────    (x ∈ [0, 100], resolución=500 puntos)
              Σ  μ_agregado(x)
```

El resultado es un único valor crisp, por ejemplo `centroide = 84.0`.

---

### 4.5 Interpretación del centroide → acción discreta

```python
if   centroide < 20:  acción = "Alejarse",  daño = 0
elif centroide < 42:  acción = "Defender",  daño = 0
elif centroide < 66:  acción = "Acercarse", daño = 0
else:                 acción = "Atacar",    daño = 8 + int((centroide−66)/34 × 8)
```

El daño del ataque del NPC no es fijo — escala de **8 a 16 pts** según qué tan "convencido" esté el motor (cuánto más alto el centroide en la zona Atacar, más daño).

**Tabla de comportamiento real del motor** (valores discretos representativos):

| Escenario | dist | vida_npc | vida_jug | centroide | acción | daño_base |
|---|---|---|---|---|---|---|
| Cerca / NPC Alta / Jug Alta | 10 | 90 | 90 | 84.0 | Atacar | 12 |
| Cerca / NPC Alta / Jug Baja | 10 | 90 | 10 | 84.0 | Atacar | 12 |
| Cerca / NPC Baja / Jug Alta | 10 | 10 | 90 | 30.0 | **Defender** | 0 |
| Cerca / NPC Baja / Jug Baja | 10 | 10 | 10 | 84.0 | Atacar | 12 |
| Media / NPC Alta / Jug Alta | 50 | 90 | 90 | 55.0 | Acercarse | 0 |
| Media / NPC Alta / Jug Baja | 50 | 90 | 10 | 84.0 | **Atacar** | 12 |
| Media / NPC Baja / Jug Alta | 50 | 10 | 90 | 9.2 | **Alejarse** | 0 |
| Media / NPC Baja / Jug Baja | 50 | 10 | 10 | 84.0 | Atacar | 12 |
| Lejos / NPC Alta / Jug Alta | 90 | 90 | 90 | 55.0 | Acercarse | 0 |
| Lejos / NPC Alta / Jug Baja | 90 | 90 | 10 | 55.0 | Acercarse | 0 |
| Lejos / NPC Baja / Jug Alta | 90 | 10 | 90 | 9.2 | **Alejarse** | 0 |
| Lejos / NPC Baja / Jug Baja | 90 | 10 | 10 | 30.0 | **Defender** | 0 |

---

## 5. Resolución de un turno completo

### 5.1 Daño del NPC

El NPC solo inflige daño cuando su acción es `Atacar` **y** la distancia en ese momento es `≤ 60 u`.

```
daño_real = daño_base                      # sin defensa
daño_real = max(0, daño_base − 8)          # con defensa del jugador activa
```

### 5.2 Overrides de borde

Cuando el NPC llega a un límite físico del tablero, su acción se redirige:

| Condición | Acción del motor | Override |
|---|---|---|
| `distancia ≤ 5` y NPC quería `Acercarse` | Acercarse | → **Atacar** (no puede acercarse más — muerde) |
| `distancia ≥ 95` y NPC quería `Alejarse` | Alejarse | → **Defender** (no puede huir más — se cubre) |

### 5.3 Movimiento del NPC

Después de decidir la acción, el NPC mueve la distancia:

```
Acercarse → distancia −= 10
Alejarse  → distancia += 10
Atacar    → sin movimiento
Defender  → sin movimiento
```

### 5.4 Condición de victoria

- `vida_npc ≤ 0` → ganador: `"Jugador"` (se evalúa después del ataque del jugador, antes del turno del NPC)
- `vida_jugador ≤ 0` → ganador: `"NPC"` (se evalúa al final del turno)

---

## 6. Interfaz de la API (`resolver_turno`)

La función principal es stateless — recibe el estado completo y devuelve el estado nuevo. Esto permite conectarla a cualquier frontend (web, pygame, consola) sin modificar la lógica.

```python
resultado = resolver_turno(estado, accion_jugador)
```

**Entrada:**
- `estado`: dict con los campos descritos en §2
- `accion_jugador`: `"1"` a `"4"` o nombre directo (`"atacar"`, etc.)

**Salida:**
```python
{
  "estado":   {...},          # estado actualizado
  "registro": ["Turno 3", "Tu ataque impacta...", "Bestia ataca..."],
  "jugador":  {"accion": "atacar", "danio": 13, "mensaje": "..."},
  "npc": {
    "accion":         "Atacar",
    "danio_base":     12,
    "valor_accion":   84.0,    # centroide del motor difuso
    "danio_aplicado": 4,       # después de reducción por defensa
    "ataque_conecto": True,
  }
}
```

El campo `valor_accion` expone el centroide crudo del motor, útil para visualización en tiempo real de la lógica difusa.
