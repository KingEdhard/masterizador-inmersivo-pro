import os
from src.utils import input_validado
from src.components.subtitulos import detectar_audio_incompatible_mp4

def elegir_formato_y_nombre(archivo_ref, carpeta_salida, resolucion, pistas, canales_out):
    """
    canales_out: 6 para 5.1, 8 para 7.1.
    """
    # Elegir formato
    raw = input_validado(
        "👉 ¿Formato de salida? (1=mp4, 2=mkv) [mp4]: ",
        opciones_validas=['1', '2', 'mp4', 'mkv', ''],
        defecto='mp4',
        map_alias={'1': 'mp4', '2': 'mkv'}
    )
    formato_salida = raw if raw in ('mp4', 'mkv') else 'mp4'

    # Advertencia audio incompatible MP4
    if formato_salida == 'mp4':
        problematicas = detectar_audio_incompatible_mp4(pistas)
        if problematicas:
            print("\n⚠ Las siguientes pistas de audio originales NO son compatibles con MP4:")
            for p in problematicas:
                print(f"   - {p}")
            print("   Si continúas en MP4, estas pistas NO se podrán copiar y el proceso FALLARÁ.")
            cambiar = input("👉 ¿Deseas cambiar automáticamente a MKV para conservarlas? (s/n) [s]: ").strip().lower()
            if cambiar in ('', 's'):
                formato_salida = 'mkv'
                print("   ➡ Se usará MKV como formato de salida.\n")
            else:
                print("   ➡ Continuando en MP4 (puede fallar al empaquetar).\n")

    # Nombre base
    nombre_base_default = os.path.splitext(os.path.basename(archivo_ref))[0]
    nombre_base = input(
        f"✍️ Nombre base del archivo de salida (sin extensión) [{nombre_base_default}]: "
    ).strip()
    if not nombre_base:
        nombre_base = nombre_base_default

    # Definir etiqueta de canales
    canales_str = "5.1" if canales_out == 6 else "7.1"

    # Construir nombre completo con la etiqueta de canales
    nombre_completo = f"{nombre_base} {resolucion} E-AC3 {canales_str} Masterizado.{formato_salida}"
    ruta_salida = os.path.join(carpeta_salida, nombre_completo).replace('\\', '/')

    print(f"\n📁 El archivo de salida será:")
    print(f"   {ruta_salida}")
    input("[Presione Enter para continuar...]")

    return {
        'formato_salida': formato_salida,
        'nombre_base': nombre_base,
        'titulo_master': f"{nombre_base} E-AC3 {canales_str} Masterizado (Voces +2dB)",
        'ruta_salida': ruta_salida
    }
