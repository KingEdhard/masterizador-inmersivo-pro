import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.components.menu import seleccionar_modo
from src.components.archivos import seleccionar_archivos
from src.components.analisis import analizar_archivo
from src.components.pista import elegir_pista
from src.components.canales import elegir_canales_salida
from src.components.formato import elegir_formato_y_nombre
from src.components.subtitulos import definir_politica_subtitulos
from src.components.filtros import construir_filtro
from src.components.construccion_cmd import construir_comando
from src.components.ejecucion import ejecutar_proceso
from src.components.post_proceso import post_proceso

def main():
    while True:
        modo = seleccionar_modo()
        if modo == '3':
            print("\n¡Hasta pronto!")
            break

        rutas = seleccionar_archivos(modo)
        if rutas is None:
            print("No se seleccionó ningún archivo. Volviendo al menú...")
            input("Presiona Enter para continuar...")
            continue

        archivo_ref = rutas['archivo_ref']
        carpeta_salida = rutas['carpeta_salida']
        lista_txt = rutas['lista_txt']

        info = analizar_archivo(archivo_ref)
        pistas = info['pistas']
        if not pistas:
            input("Presiona Enter para volver al Menú Principal...")
            continue

        duracion = info['duracion']
        resolucion = info['resolucion']

        print(f"\n📋 INFORMACIÓN TÉCNICA (Resolución: {resolucion})")

        idx_sel = elegir_pista(pistas)
        if idx_sel is None:
            continue

        # Nueva pregunta: 5.1 o 7.1
        canales_out = elegir_canales_salida()

        # Pasamos canales_out a formato para que construya el nombre correcto
        fmt = elegir_formato_y_nombre(archivo_ref, carpeta_salida, resolucion, pistas, canales_out)
        if fmt is None:
            continue

        formato_salida = fmt['formato_salida']
        titulo_master = fmt['titulo_master']
        ruta_salida = fmt['ruta_salida']

        subs_action = definir_politica_subtitulos(archivo_ref, formato_salida)
        # El filtro también recibe los canales de salida
        filtro = construir_filtro(idx_sel, pistas, canales_out)

        config_cmd = {
            'archivo_ref': archivo_ref,
            'lista_txt': lista_txt,
            'opcion': modo,
            'idx_sel': idx_sel,
            'pistas': pistas,
            'formato_salida': formato_salida,
            'subs_action': subs_action,
            'filtro': filtro,
            'titulo_master': titulo_master,
            'ruta_salida': ruta_salida
        }
        cmd = construir_comando(config_cmd)

        exito, ruta_final = ejecutar_proceso(cmd, duracion, archivo_ref)

        if modo == '1' and lista_txt and os.path.exists(lista_txt):
            os.remove(lista_txt)

        post_proceso(exito, archivo_ref, ruta_final, idx_sel)

        input("\nPresiona Enter para volver al Menú Principal...")

if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        input("\nERROR: Se produjo una excepción. Presiona Enter para cerrar...")
