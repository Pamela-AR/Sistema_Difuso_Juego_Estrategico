import json
import time
import os
import matplotlib.pyplot as plt
import numpy as np

# Importamos las variables lingüísticas de nuestro juego
from juego_difuso import distancia, vida_npc, vida_jugador, accion, sistema

plt.ion()
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
fig.canvas.manager.set_window_title('Visualizador Difuso - Pensamiento del NPC')

def graficar_variable(ax, var_ling, titulo, color_map):
    x = np.linspace(var_ling.universe[0], var_ling.universe[1], 200)
    for nombre, fn in var_ling.sets.items():
        y = [fn(xi) for xi in x]
        ax.plot(x, y, label=nombre, color=color_map.get(nombre, 'k'), linewidth=2)
    ax.set_title(titulo)
    ax.legend(loc='upper right', fontsize='small')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlim(var_ling.universe[0], var_ling.universe[1])
    ax.set_ylim(-0.05, 1.05)

colores_dist = {"Cerca": "red", "Media": "orange", "Lejos": "green"}
colores_vida = {"Baja": "red", "Media": "orange", "Alta": "green"}
colores_acc  = {"Alejarse": "blue", "Defender": "orange", "Acercarse": "purple", "Atacar": "red"}

# Graficamos los conjuntos fijos de fondo
graficar_variable(axs[0, 0], distancia, 'Distancia al Jugador', colores_dist)
graficar_variable(axs[0, 1], vida_npc, 'Vida del NPC', colores_vida)
graficar_variable(axs[1, 0], vida_jugador, 'Vida del Jugador', colores_vida)
graficar_variable(axs[1, 1], accion, 'Salida: Acción Decidida', colores_acc)

plt.tight_layout()

# Referencias para actualizar las líneas dinámicas
lineas = {
    'distancia': axs[0, 0].axvline(0, color='black', linestyle='--', linewidth=2, visible=False),
    'vida_npc': axs[0, 1].axvline(0, color='black', linestyle='--', linewidth=2, visible=False),
    'vida_jugador': axs[1, 0].axvline(0, color='black', linestyle='--', linewidth=2, visible=False),
    'accion': axs[1, 1].axvline(0, color='black', linestyle='-', linewidth=3, visible=False)
}

texto_accion = axs[1, 1].text(0.5, 0.5, '', transform=axs[1, 1].transAxes, 
                              ha='center', va='center', fontsize=14, 
                              bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

archivo_estado = "estado_difuso.json"
ultimo_modificado = 0

print("Visualizador iniciado. Esperando datos del juego...")

while True:
    try:
        if os.path.exists(archivo_estado):
            mtime = os.path.getmtime(archivo_estado)
            if mtime > ultimo_modificado:
                ultimo_modificado = mtime
                with open(archivo_estado, "r") as f:
                    estado = json.load(f)
                
                # Actualizar líneas
                lineas['distancia'].set_xdata([estado['distancia']])
                lineas['distancia'].set_visible(True)
                
                lineas['vida_npc'].set_xdata([estado['vida_npc']])
                lineas['vida_npc'].set_visible(True)
                
                lineas['vida_jugador'].set_xdata([estado['vida_jugador']])
                lineas['vida_jugador'].set_visible(True)
                
                lineas['accion'].set_xdata([estado['accion_valor']])
                lineas['accion'].set_visible(True)
                
                texto_accion.set_text(f"Acción: {estado['accion_nombre']}\nValor: {estado['accion_valor']:.1f}")
                texto_accion.set_position((0.5, 0.8)) # Mover arriba para que no estorbe
                
                fig.canvas.draw()
                fig.canvas.flush_events()
                
    except Exception as e:
        pass # Ignorar errores temporales de lectura
    
    plt.pause(0.5)

