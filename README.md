# Sistema difuso aplicado a juego estratégico

Proyecto del curso de Desarrollo de sistemas inteligentes.

## Modos disponibles

### Consola

```bash
python3 juego_difuso.py
```

### Interfaz web 16-bit

La interfaz web usa el mismo motor difuso de `mamdani.py` y las reglas definidas en `juego_difuso.py`.

```bash
python3 servidor_web.py
```

Luego abre:

```text
http://127.0.0.1:8000
```

## Estructura

- `mamdani.py`: algoritmo Mamdani implementado en el proyecto.
- `juego_difuso.py`: reglas del NPC y resolución del combate por turnos.
- `servidor_web.py`: servidor HTTP sin dependencias externas.
- `web/`: interfaz 16-bit en HTML, CSS y JavaScript.
