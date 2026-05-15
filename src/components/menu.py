import os
import sys

def seleccionar_modo():
    # Limpiar pantalla de forma más agresiva
    if os.name == 'nt':
        os.system('cls')
    else:
        print("\033c", end="")  # ANSI clear para bash
    print("=" * 60)
    print("        🎬 MASTERIZADOR INMERSIVO PRO v7.0 (Componentes)")
    print("=" * 60)
    print("\nMENÚ PRINCIPAL:")
    print("  1. Unir partes (.mkv/.mp4) y Masterizar")
    print("  2. Masterizar un solo archivo de película")
    print("  3. Salir")
    print("-" * 60)
    while True:
        opcion = input("\n👉 Elige una opción (1, 2 o 3): ").strip()
        if opcion in ('1', '2', '3'):
            return opcion
        print("Opción no válida. Intenta de nuevo.")
