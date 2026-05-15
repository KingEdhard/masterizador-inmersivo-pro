import numpy as np
import subprocess
import os
import tempfile
from src.utils import FFMPEG_PATH, DEBUG, input_validado

def extraer_audio(archivo, map_audio, duracion_muestra=10, canales_forzados=2):
    if not archivo or not os.path.exists(archivo):
        return None
    cmd = [FFMPEG_PATH, '-hide_banner', '-loglevel', 'error', '-i', archivo, '-map', map_audio, '-t', str(duracion_muestra), '-f', 's16le', '-acodec', 'pcm_s16le', '-ar', '48000', '-ac', str(canales_forzados), '-']
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        return None
    if proc.returncode != 0:
        if DEBUG:
            stderr = proc.stderr.decode(errors='replace') if isinstance(proc.stderr, (bytes, bytearray)) else str(proc.stderr)
            print(f"[DEBUG] ffmpeg error extracting {map_audio}: {stderr[:500]}")
        return None
    raw = proc.stdout
    if not raw:
        return None
    if isinstance(raw, str):
        raw = raw.encode('utf-8', errors='replace')
    bytes_por_frame = 2 * canales_forzados
    n_frames = len(raw) // bytes_por_frame
    if n_frames == 0:
        return None
    usable = raw[:n_frames * bytes_por_frame]
    try:
        arr = np.frombuffer(usable, dtype=np.int16)
    except Exception:
        return None
    try:
        arr = arr.reshape(n_frames, canales_forzados)
    except Exception:
        try:
            arr = arr.reshape(-1, 1)
        except Exception:
            return None
    return arr.astype(np.float32) / 32768.0

def generar_grafica_comparativa(orig, master, pista_idx, duracion_muestra=10):
    try:
        import matplotlib
        matplotlib.use('TkAgg')
    except Exception:
        import matplotlib
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    print("\n🎧 Generando gráfica comparativa...")
    audio_orig = extraer_audio(orig, f'0:{pista_idx}', duracion_muestra, 2)
    audio_mast = extraer_audio(master, '0:a:0', duracion_muestra, 2)

    if audio_orig is None or audio_mast is None:
        print("✖ No se pudo extraer audio para la gráfica.")
        return
    audio_orig = np.atleast_2d(audio_orig).T if audio_orig.ndim == 1 else audio_orig
    audio_mast = np.atleast_2d(audio_mast).T if audio_mast.ndim == 1 else audio_mast
    n_frames = min(audio_orig.shape[0], audio_mast.shape[0])
    if n_frames == 0:
        print("✖ Fragmentos vacíos.")
        return
    audio_orig = audio_orig[:n_frames]
    audio_mast = audio_mast[:n_frames]
    mono_orig = np.mean(audio_orig, axis=1)
    mono_mast = np.mean(audio_mast, axis=1)
    sr = 48000.0
    t = np.arange(n_frames) / sr

    try:
        plt.figure(figsize=(10, 4))
        plt.plot(t, mono_orig, label='Original', alpha=0.7, linewidth=0.8)
        plt.plot(t, mono_mast, label='Masterizado', alpha=0.8, linewidth=0.8)
        plt.xlabel('Tiempo (s)')
        plt.ylabel('Amplitud (normalizada)')
        plt.title(f'Comparativa de formas de onda (fragmento de {duracion_muestra}s)')
        plt.legend(loc='upper right')
        plt.tight_layout()
        plt.show()
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Error mostrando gráfica: {e}")
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            tmp_path = tmp.name
            tmp.close()
            plt.savefig(tmp_path)
            plt.close()
            print(f"Gráfica guardada en: {tmp_path}")
        except Exception as e2:
            if DEBUG:
                print(f"[DEBUG] Error guardando gráfica: {e2}")
            print("✖ No se pudo mostrar ni guardar la gráfica.")

def post_proceso(exito, archivo_ref, ruta_final, idx_sel):
    if exito:
        print("\n" + "=" * 60)
        print(f"✔ PROCESO COMPLETADO: {os.path.basename(ruta_final)}")
        print("=" * 60)
        print("📁 Se han conservado todas las pistas originales.")
        print(f"🎧 Nueva pista predeterminada añadida (E-AC3 7.1 Masterizado).")
        ver_graf = input_validado("\n📈 ¿Ver gráfica comparativa de ondas? (s/n) [n]: ", ['s', 'n'], defecto='n')
        if ver_graf == 's':
            generar_grafica_comparativa(archivo_ref, ruta_final, idx_sel)
    else:
        print("\n✖ El proceso NO se completó correctamente.")