import os
from src.utils import FFMPEG_PATH

def construir_comando(config):
    cmd = [FFMPEG_PATH, '-y']

    # Forzar regeneración de timestamps para evitar "unknown timestamp" en MKV
    if config['opcion'] == '1':
        cmd.extend(['-fflags', '+genpts', '-f', 'concat', '-safe', '0', '-i', config['lista_txt']])
    else:
        cmd.extend(['-fflags', '+genpts', '-i', config['archivo_ref']])

    cmd.extend(['-map', '0:v', '-c:v', 'copy'])

    if config['subs_action'] == 'copy_mp4':
        cmd.extend(['-map', '0:s?', '-c:s', 'mov_text'])
    elif config['subs_action'] == 'copy':
        cmd.extend(['-map', '0:s?', '-c:s', 'copy'])

    cmd.extend(['-map', '0:t?', '-c:t', 'copy'])

    idx_sel = config['idx_sel']
    filtro = config['filtro']
    cmd.extend(['-filter_complex', f'[0:{idx_sel}]{filtro}[a_master]'])
    cmd.extend(['-map', '[a_master]'])
    cmd.extend([
        '-c:a:0', 'eac3',
        '-b:a:0', '1024k',
        f'-metadata:s:a:0', f'title={config["titulo_master"]}',
        '-disposition:a:0', 'default'
    ])

    indices_originales = [idx for idx, _, _, _ in config['pistas']]
    for i, idx_orig in enumerate(indices_originales, start=1):
        cmd.extend(['-map', f'0:{idx_orig}', f'-c:a:{i}', 'copy', f'-disposition:a:{i}', '0'])

    cmd.extend(['-map_metadata', '0', '-map_chapters', '0', config['ruta_salida']])
    return cmd
