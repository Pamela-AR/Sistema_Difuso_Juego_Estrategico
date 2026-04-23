# Visualización del Procesamiento Difuso - Documentación

## Descripción General

Se ha implementado un sistema completo de visualización del procesamiento difuso (fuzzy logic) en la interfaz web del juego. Ahora es posible ver en tiempo real:

1. **Fuzzificación (Entrada)**: Valores de entrada y sus grados de membresía en cada conjunto lingüístico
2. **Reglas Activadas**: Todas las reglas que se activaron con su "fuerza de disparo" (firing strength)
3. **Agregación (Salida)**: Cómo se combinaron las salidas de las reglas activadas
4. **Centroide (Defuzzificación)**: Valor crisp final de la salida del sistema

## Cambios en los Archivos

### Backend - `juego_difuso.py`

#### Nueva función: `_extraer_datos_procesamiento()`
Extrae datos detallados del procesamiento difuso:

```python
def _extraer_datos_procesamiento(entradas, salidas):
    """
    Retorna un diccionario con:
    - fuzzificacion: variables de entrada con sus grados de membresía
    - reglas_activadas: reglas con firing_strength > 0.001
    - agregacion: valores de cada conjunto de salida
    - valor_salida: centroide defuzzificado
    """
```

#### Modificación: `turno_npc()`
Ahora retorna 4 valores en lugar de 3:
```python
# Antes:
return accion_npc, danio, valor_centroide

# Ahora:
return accion_npc, danio, valor_centroide, datos_proc
```

#### Modificación: `resolver_turno()`
La respuesta JSON ahora incluye datos del procesamiento difuso:

```json
{
  "estado": {...},
  "registro": [...],
  "jugador": {...},
  "npc": {...},
  "procesamiento_difuso": {
    "fuzzificacion": {...},
    "reglas_activadas": [...],
    "agregacion": {...},
    "valor_salida": {...}
  }
}
```

### Backend - `servidor_web.py`

#### Nuevo endpoint: `GET /api/procesamiento`
Permite acceder a los datos guardados en `estado_difuso.json`:

```python
if parsed.path == "/api/procesamiento":
    try:
        with open("estado_difuso.json", "r") as f:
            datos = json.load(f)
            self._send_json(datos)
    except (FileNotFoundError, json.JSONDecodeError):
        self._send_json({"error": "No hay datos..."}, status=HTTPStatus.NOT_FOUND)
```

### Frontend - `index.html`

#### Nuevo Panel: `.fuzzy-panel`
Agregada nueva sección con:
- Header con título "🧠 Lógica Difusa" y botón toggle
- Contenido scrollable que muestra:
  - Sección de fuzzificación
  - Sección de reglas activadas  
  - Sección de agregación
  - Sección de centroide

### Frontend - `styles.css`

#### Cambios principales:
1. **Grid layout**: Cambiado de 2 a 3 columnas para acomodar el nuevo panel
2. **Estilos de `.fuzzy-panel`**: Tema oscuro con colores de terminal (cian #4ec9b0)
3. **Estilos de secciones**: 
   - `.fuzzy-section`: Contenedores de datos con borde izquierdo
   - `.fuzzy-rule`: Reglas activadas con visualización de fuerza
   - `.fuzzy-entry`: Pares etiqueta-valor
   - `.fuzzy-value`: Valores resaltados en cian

#### Media queries:
- En pantallas ≤ 1200px: Grid se convierte a 1 columna apilada verticalmente
- En pantallas ≤ 860px: Ajuste adicional de bordes y espacios

### Frontend - `app.js`

#### Nueva función: `renderFuzzyProcessing(data)`
Genera HTML dinámico que muestra:

```javascript
// Secciones generadas:
// 1. Fuzzificación: Variables de entrada y sus grados
// 2. Reglas Activadas: Con detalles de antecedentes y firing strength
// 3. Agregación: Valores de salida con barras visuales
// 4. Centroide: Valor defuzzificado final
```

#### Mejoras en `playTurn()`:
Ahora captura y renderiza los datos del procesamiento difuso:

```javascript
const payload = await response.json();
gameState = payload.estado;
renderLog(payload.registro);
renderFuzzyProcessing(payload.procesamiento_difuso);  // ← Nueva línea
```

#### Toggle del panel:
```javascript
elements.toggleFuzzy.addEventListener("click", () => {
  const isHidden = elements.fuzzyContent.style.display === "none";
  elements.fuzzyContent.style.display = isHidden ? "block" : "none";
  elements.toggleFuzzy.textContent = isHidden ? "−" : "+";
});
```

## Formato de Datos JSON

### Estructura completa:

```json
{
  "fuzzificacion": {
    "Distancia": {
      "valor": 40,
      "unidad": "u",
      "conjuntos": {
        "Cerca": 0.2,
        "Media": 0.6,
        "Lejos": 0.0
      }
    }
  },
  
  "reglas_activadas": [
    {
      "indice": 0,
      "antecedentes": [
        {
          "variable": "Distancia",
          "conjunto": "Cerca",
          "negado": false,
          "valor_membresia": 0.2
        }
      ],
      "operador": "AND",
      "firing_strength": 0.2,
      "consecuentes": {
        "Accion": "Atacar"
      }
    }
  ],
  
  "agregacion": {
    "Accion": {
      "conjuntos": {
        "Alejarse": 0.0,
        "Defender": 0.0,
        "Acercarse": 0.6,
        "Atacar": 0.2
      }
    }
  },
  
  "valor_salida": {
    "Accion": 55.0
  }
}
```

## Flujo de Datos

```
┌─────────────────────────────────┐
│ Usuario hace clic (Atacar, etc.)│
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ POST /api/turno                 │
│ {estado, accion}                │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ resolver_turno()                │
│ - Normaliza estado              │
│ - Aplica acción jugador         │
│ - turno_npc() →                 │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ turno_npc()                     │
│ - Fuzzifica entradas            │
│ - Aplica reglas (razonamiento)  │
│ - Agrega salidas                │
│ - Defuzzifica                   │
│ - Extrae datos_proc ←───────┐   │
└────────────┬────────────────┘   │
             │                    │
             ▼                    │
┌─────────────────────────────────┐│
│ _extraer_datos_procesamiento()  ││
│ Retorna JSON detallado          ││
└────────────┬────────────────────┘│
             │                     │
             ▼                     │
┌─────────────────────────────────────┐
│ resolver_turno() retorna:           │
│ {                                   │
│   estado,                           │
│   registro,                         │
│   jugador,                          │
│   npc,                              │
│   procesamiento_difuso ←────────────┘
│ }
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Cliente recibe JSON             │
│ playTurn() → renderFuzzyProcessing()
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Panel Fuzzy actualiza con:      │
│ - Fuzzificación                 │
│ - Reglas activadas              │
│ - Agregación                    │
│ - Centroide                     │
└─────────────────────────────────┘
```

## Filtrado de Datos

Para evitar saturar el panel, solo se muestran:
- **Reglas activadas**: Solo aquellas con `firing_strength > 0.001`
- Este umbral se puede ajustar en `_extraer_datos_procesamiento()` si es necesario

## Pruebas

Se incluye archivo `test_fuzzy.py` para verificar que la extracción de datos funciona:

```bash
python test_fuzzy.py
```

Muestra un turno completo con todos los datos del procesamiento difuso.

## Mejoras Futuras (Opcionales)

1. **Gráficos de funciones de membresía**: Usar Canvas o SVG para dibujar las funciones
2. **Gráficos de agregación**: Visualizar cómo se combinaron las reglas
3. **Historial de turnos**: Guardar y comparar procesamiento entre turnos
4. **Exportación a CSV**: Descarga de datos para análisis externo
5. **Modo depuración**: Pausar después de cada fase del procesamiento

## Estilo Visual

El panel de lógica difusa utiliza:
- **Color principal**: Cian (#4ec9b0) para resaltar valores
- **Fondo**: Gradiente oscuro (#1a1a2e → #16213e) similar a terminal
- **Fuente**: Monoespacial (Courier New) para mejor legibilidad de números
- **Emojis**: Para identificar rápidamente cada sección (📊, ⚡, 🎯, ✓)

## Notas Técnicas

- Los datos se guardan también en `estado_difuso.json` para herramientas externas
- El panel es completamente responsive y se adapta a pantallas pequeñas
- El toggle permite ocultar el panel para ver más del campo de batalla
- Los datos se actualizan después de cada turno del NPC
