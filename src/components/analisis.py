import subprocess
import json
import os
from src.utils import FFPROBE_PATH, DEBUG

def _run_ffprobe(args, archivo):
    archivo_norm = archivo.replace('\\', '/')
    cmd = [FFPROBE_PATH, '-v', 'error'] + args + ['-of', 'json', archivo_norm]
    if DEBUG:
        print(f"[DEBUG] Ejecutando: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if res.returncode != 0:
            if DEBUG:
                print(f"[DEBUG] ffprobe error (código {res.returncode}):")
                print(res.stderr[:500])
            return {}
        if not res.stdout.strip():
            if DEBUG:
                print("[DEBUG] ffprobe stdout vacío")
            return {}
        return json.loads(res.stdout)
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Excepción ejecutando ffprobe: {e}")
        return {}

def obtener_info_completa(archivo):
    # Resolución
    datos_res = _run_ffprobe(['-select_streams', 'v:0', '-show_entries', 'stream=width,height'], archivo)
    streams_video = datos_res.get('streams', [])
    if streams_video:
        w = streams_video[0].get('width', 0)
        h = streams_video[0].get('height', 0)
        if w and h:
            resolucion = f"{w}p x {h}p"   # ← ESTILO ORIGINAL RESTAURADO
        else:
            resolucion = "Resolucion Desconocida"
    else:
        resolucion = "Resolucion Desconocida"

    # Duración
    datos_dur = _run_ffprobe(['-show_entries', 'format=duration'], archivo)
    duracion = float(datos_dur.get('format', {}).get('duration', 0))

    # Pistas de audio
    datos_audio = _run_ffprobe([
        '-select_streams', 'a',
        '-show_entries', 'stream=index,codec_name,channels,channel_layout:stream_tags=language,title,comment,handler_name'
    ], archivo)

    if DEBUG:
        print("\n[DEBUG] Metadatos crudos de audio:")
        print(json.dumps(datos_audio, indent=2))

    pistas = []
    for stream in datos_audio.get('streams', []):
        idx = stream.get('index')
        codec = stream.get('codec_name', '???').upper()
        canales = stream.get('channels', 0)
        layout = stream.get('channel_layout', '')
        if layout and '.' in layout:
            canales_str = layout.split('(')[0]
        else:
            canales_str = f"{canales}ch"
        tags = stream.get('tags', {})
        idioma = tags.get('language', 'und')
        titulo = tags.get('title') or tags.get('comment') or tags.get('handler_name') or ''
        if titulo:
            descripcion = f"[{idx}] {titulo} ({codec} {canales_str})"
        else:
            descripcion = f"[{idx}] Idioma: {idioma} ({codec} {canales_str})"
        pistas.append((idx, descripcion, canales, layout if layout else f"{canales}ch"))

    return duracion, pistas, resolucion

def analizar_archivo(archivo_ref):
    duracion, pistas, resolucion = obtener_info_completa(archivo_ref)
    if not pistas:
        print("\n✖ No se detectaron pistas de audio en el archivo. Proceso cancelado.\n")
    return {
        'duracion': duracion,
        'pistas': pistas,
        'resolucion': resolucion
    }
