#!/usr/bin/env python3
"""
Script de prueba para verificar que el procesamiento difuso genera datos correctamente.
"""

import json
from juego_difuso import resolver_turno, crear_estado_inicial

# Crear estado inicial
estado = crear_estado_inicial()
print("Estado inicial creado:", estado)
print()

# Ejecutar un turno
print("Ejecutando turno 1...")
resultado = resolver_turno(estado, "atacar")

print("\n=== RESULTADO DEL TURNO ===")
print(f"Nuevo estado: {resultado['estado']}")
print(f"Registro: {resultado['registro']}")
print(f"Acción jugador: {resultado['jugador']}")
print(f"Acción NPC: {resultado['npc']}")

if resultado.get("procesamiento_difuso"):
    print("\n=== DATOS DEL PROCESAMIENTO DIFUSO ===")
    datos = resultado["procesamiento_difuso"]
    
    print("\n--- FUZZIFICACIÓN ---")
    for var_name, var_data in datos["fuzzificacion"].items():
        print(f"\n{var_name}: {var_data['valor']} {var_data['unidad']}")
        for conj_name, grado in var_data["conjuntos"].items():
            print(f"  {conj_name}: {grado:.3f}")
    
    print("\n--- REGLAS ACTIVADAS ---")
    for rule in datos["reglas_activadas"]:
        print(f"\nRegla {rule['indice']} (Fuerza: {rule['firing_strength']:.3f})")
        print(f"Antecedentes ({rule['operador']}):")
        for ant in rule["antecedentes"]:
            print(f"  {ant['variable']} es {ant['conjunto']} (μ={ant['valor_membresia']})")
        print("Consecuentes:")
        for out_var, conj in rule["consecuentes"].items():
            print(f"  {out_var} es {conj}")
    
    print("\n--- AGREGACIÓN ---")
    for var_name, var_data in datos["agregacion"].items():
        print(f"\n{var_name}:")
        for conj_name, alpha in var_data["conjuntos"].items():
            print(f"  {conj_name}: {alpha:.3f}")
    
    print("\n--- VALOR DE SALIDA ---")
    for var_name, valor in datos["valor_salida"].items():
        print(f"{var_name}: {valor:.3f}")
else:
    print("\n[ADVERTENCIA] No se retornaron datos de procesamiento difuso")

print("\n✓ Test completado exitosamente")
