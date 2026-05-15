import re
import subprocess
from tqdm import tqdm
import os
from src.utils import DEBUG
from src.components.subtitulos import detectar_subs_incompatibles

def ejecutar_ffmpeg(comando, duracion_total):
    if DEBUG:
        print("\n[DEBUG] Comando FFmpeg:")
        print(" ".join(comando))
        print("-" * 60)
    proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='replace')
    pbar = tqdm(total=100, desc="Masterizando", unit="%", ncols=80)
    tiempo_previo = 0.0
    patron_tiempo = re.compile(r"time=(\d+):(\d+):(\d+(?:\.\d+)?)")
    stderr_completo = ""
    try:
        for linea in proceso.stdout:
            stderr_completo += linea
            m = patron_tiempo.search(linea)
            if m:
                h, m_, s = map(float, m.groups())
                t_actual = h * 3600 + m_ * 60 + s
                if duracion_total and duracion_total > 0:
                    progreso = (t_actual / duracion_total) * 100.0
                    incr = max(0.0, progreso - tiempo_previo)
                    if incr > 0:
                        pbar.update(incr)
                        tiempo_previo = progreso
    except Exception:
        pass
    finally:
        proceso.wait()
        if proceso.returncode == 0:
            pbar.n = 100
        pbar.close()

    exito = proceso.returncode == 0
    if not exito:
        print("\n✖ ERROR: FFmpeg finalizó con código", proceso.returncode)
        print("--- Últimas líneas del error ---")
        print(stderr_completo[-2000:])
    return exito, stderr_completo

def manejar_error_empaquetado_y_fallback(cmd_original, ruta_salida, archivo_ref, duracion_total):
    exito, stderr = ejecutar_ffmpeg(cmd_original, duracion_total)
    if exito:
        return True, cmd_original, ruta_salida, stderr

    err_low = (stderr or "").lower()

    # Buscar errores específicos de empaquetado: mov_text, subtítulos, attachments, códec no válido en contenedor
    fallback_trigger = False
    if any(k in err_low for k in ('could not write header', 'error writing trailer', 'invalid codec')):
        fallback_trigger = True
    elif 'mov_text' in err_low:
        fallback_trigger = True
    elif 'subtitle' in err_low and ('could not find tag' in err_low or 'codec not supported' in err_low or 'mov_text' in err_low):
        fallback_trigger = True
    elif 'attachment' in err_low and 'could not write' in err_low:
        fallback_trigger = True

    # Adicional: si hay timestamps unset, no es fallo de subs, pero podemos forzar regeneración con genpts (ya lo hicimos)
    # Si no es fallback elegible, salir
    if not fallback_trigger:
        return False, cmd_original, ruta_salida, stderr

    subs_incompat = detectar_subs_incompatibles(archivo_ref)
    if not subs_incompat:
        subs_incompat = [('unknown', 'detected_via_stderr')]

    print("\n✖ ERROR de empaquetado (subtítulos/attachments). Reintentando fallback MP4...")
    for idx, codec in subs_incompat:
        print(f"   - stream {idx}: {codec}")

    ruta_mp4 = os.path.splitext(ruta_salida)[0] + '.mp4'
    cmd_fb = []
    i = 0
    while i < len(cmd_original):
        tok = cmd_original[i]
        if tok == '-map' and i+1 < len(cmd_original) and str(cmd_original[i+1]).startswith('0:s'):
            i += 2
            continue
        if tok == '-c:s' and i+1 < len(cmd_original) and cmd_original[i+1] in ('mov_text', 'srt', 'copy'):
            i += 2
            continue
        cmd_fb.append(tok)
        i += 1

    if cmd_fb and cmd_fb[-1] == ruta_salida:
        cmd_fb[-1] = ruta_mp4
    else:
        for j in range(len(cmd_fb)-1, -1, -1):
            if isinstance(cmd_fb[j], str) and cmd_fb[j].endswith(('.mkv', '.mp4')):
                cmd_fb[j] = ruta_mp4
                break

    print("\n▶ Reintentando con estrategia fallback: MP4 sin subtítulos problemáticos...\n")
    exito_fb, stderr_fb = ejecutar_ffmpeg(cmd_fb, duracion_total)
    if exito_fb:
        # Limpiar archivo original fallido (si existe)
        if os.path.exists(ruta_salida):
            try:
                os.remove(ruta_salida)
                if DEBUG:
                    print(f"[DEBUG] Archivo original fallido eliminado: {ruta_salida}")
            except Exception:
                pass
        print("\n✔ Fallback completado: archivo creado en MP4.")
        return True, cmd_fb, ruta_mp4, stderr_fb
    else:
        print("\n✖ El fallback a MP4 también falló.")
        return False, cmd_fb, ruta_mp4, stderr_fb

def ejecutar_proceso(cmd, duracion, archivo_ref):
    exito, _, ruta_final, _ = manejar_error_empaquetado_y_fallback(cmd, cmd[-1], archivo_ref, duracion)
    return exito, ruta_final
