def elegir_pista(pistas):
    if not pistas:
        return None
    print("\n🎧 PISTAS DE AUDIO DETECTADAS (estilo VLC):")
    for _, desc, _, _ in pistas:
        print(f"   {desc}")
    print("-" * 60)
    indices_validos = [str(idx) for idx, _, _, _ in pistas]
    while True:
        entrada = input("\n🔊 Número de pista a masterizar (escribe exactamente el número entre corchetes): ").strip()
        if entrada in indices_validos:
            return int(entrada)
        print(f"✖ ID inválido. Los IDs disponibles son: {', '.join(indices_validos)}")