from src.utils import input_validado

def elegir_canales_salida():
    """Pregunta si se quiere 5.1 o 7.1. Retorna el número de canales (6 u 8)."""
    opcion = input_validado(
        "🔉 ¿Cuántos canales de salida deseas? (1=5.1, 2=7.1) [7.1]: ",
        opciones_validas=['1', '2', '5.1', '7.1', ''],
        defecto='7.1',
        map_alias={'1': '5.1', '2': '7.1'}
    )
    return 8 if opcion == '7.1' else 6
