import os
import subprocess
import json
from src.utils import FFPROBE_PATH, DEBUG

CODECS_AUDIO_MP4 = {'aac', 'mp3', 'ac3', 'eac3', 'alac'}

def detectar_subs_incompatibles(archivo):
    if not os.path.exists(archivo):
        return []
    cmd = [FFPROBE_PATH, '-v', 'error', '-select_streams', 's', '-show_entries', 'stream=index,codec_name', '-of', 'json', archivo.replace('\\', '/')]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        datos = json.loads(res.stdout) if res.stdout else {}
    except Exception:
        if DEBUG:
            print("[DEBUG] fallo al ejecutar ffprobe para subtítulos:", getattr(res, 'stderr', 'no output'))
        return []
    incompatibles = []
    for s in datos.get('streams', []):
        idx = s.get('index')
        codec = (s.get('codec_name') or '').lower()
        if codec in ('hdmv_pgs_subtitle', 'pgs', 'dvd_subtitle', 'dvdsub', 'hdmv_pgs'):
            incompatibles.append((idx, codec))
    return incompatibles

def detectar_audio_incompatible_mp4(pistas):
    problematicas = []
    for idx, desc, canales, layout in pistas:
        partes = desc.split('(')
        if len(partes) > 1:
            codec_str = partes[-1].split()[0].lower()
            if codec_str not in CODECS_AUDIO_MP4:
                problematicas.append(desc)
    return problematicas

def definir_politica_subtitulos(archivo_ref, formato_salida):
    """
    Para MP4: si hay subs incompatibles (PGS), se omiten automáticamente.
    Para MKV: copiar los subtítulos originales sin preguntar (copy).
    """
    if formato_salida == 'mp4':
        subs_incompat = detectar_subs_incompatibles(archivo_ref)
        if subs_incompat:
            print("\n⚠ Se detectaron subtítulos incompatibles con MP4 (mov_text):")
            for idx, codec in subs_incompat:
                print(f"   - stream {idx}: {codec}")
            print("Se omitirán los subtítulos problemáticos en la salida.")
            return 'drop_subs'
        else:
            return 'copy_mp4'
    else:  # MKV: conservar subtítulos originales sin preguntar
        return 'copy'  # usaremos 'copy' en lugar de 'convert_to_srt'
