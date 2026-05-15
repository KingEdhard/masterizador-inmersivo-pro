# 🎬 Masterizador Inmersivo Pro v7.0 (Arquitectura de Componentes)

## 📌 Descripción general
Procesa archivos de video (MKV/MP4) aplicando un filtro que realza las voces (+2 dB entre 400 Hz y 4000 Hz), normaliza el volumen y realiza un **upmix inteligente a 5.1 o 7.1** según la elección del usuario.  
El audio mejorado se codifica en **E‑AC3 (Dolby Digital Plus) a 1024 kbps** y se añade como una nueva pista predeterminada, **conservando sin modificar todas las pistas originales**, subtítulos, capítulos y archivos adjuntos.

## ⚙️ Instalación automática (recomendada)

Después de clonar o descargar el proyecto, ejecuta **un solo comando** según tu sistema:

- **Windows (PowerShell):** `.\setup.ps1`
- **Windows (Git Bash), Linux o macOS:** `chmod +x setup.sh && ./setup.sh`

Estos scripts crearán el entorno virtual, instalarán las dependencias y descargarán automáticamente `ffmpeg.exe` y `ffprobe.exe` en la carpeta `bin/`.

> 🔽 **Para obtener el proyecto** haz clic en el botón verde **Code** en GitHub y selecciona **Download ZIP** o copia la URL para clonarlo con `git clone`.

## 🔧 Instalación manual
1. Crea un entorno virtual: `python -m venv venv`
2. Actívalo:
   - Windows: `venv\Scripts\Activate.ps1` (PowerShell) o `source venv/Scripts/activate` (Git Bash)
   - Linux/macOS: `source venv/bin/activate`
3. Instala las dependencias: `pip install -r requirements.txt`
4. Descarga `ffmpeg.exe` y `ffprobe.exe` de [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (versión **release essentials**) y colócalos en la carpeta `bin/`.

## 🔄 Flujo de trabajo
1. **Menú principal** – Unir partes o masterizar un único archivo.
2. **Selección de archivos** – Diálogo filtrado para video.
3. **Análisis técnico con ffprobe** – Resolución, duración, pistas de audio.
4. **Selección de pista a masterizar**.
5. **Elección de canales de salida** (5.1 / 7.1).
6. **Configuración de formato y nombre** – Una sola pregunta, advertencia si MP4 no compatible con audio original.
7. **Política de subtítulos** – Copia automática en MKV, omisión de incompatibles en MP4.
8. **Construcción del filtro** – Normalización, realce de voces, upmix.
9. **Ejecución con FFmpeg** – Barra de progreso, fallback automático ante errores de empaquetado.
10. **Post‑proceso** – Mensaje de éxito y gráfica comparativa opcional.

## 🔊 Mejoras en el audio
- **Normalización dinámica** (`dynaudnorm=f=150:g=31:p=0.95`)
- **Realce de voces** (+2 dB entre 400‑4000 Hz con `firequalizer`)
- **Upmix a 5.1 o 7.1** mediante `pan` adaptativo según la fuente.

## 📦 Conservación de datos originales
- Vídeo copiado sin recodificar.
- Pistas de audio originales conservadas con su códec original.
- Subtítulos copiados (MKV) o convertidos/omitidos (MP4).
- Capítulos, metadatos y adjuntos conservados íntegramente.

## 🛡️ Manejo de errores
- Archivo no multimedia → cancelación automática.
- Códecs de audio no compatibles con MP4 → advertencia y cambio a MKV.
- Error de timestamps en MKV → forzado con `-fflags +genpts`.
- Fallo de empaquetado → fallback automático a MP4.
- Otros errores → mensaje claro y vuelta al menú.

## 📈 Precisión del upmix
- Mezcla ponderada (coeficiente 0.5) para crear canales central y LFE desde estéreo.
- Sin artefactos ni desfases: el `pan` de FFmpeg es enrutamiento puro.
- Codificación E‑AC3 a 1024 kbps con transparencia auditiva.

## 🔧 Requisitos
- **FFmpeg** y **FFprobe** (se descargan automáticamente con el script de instalación).
- **Python 3.6+** con `numpy`, `tqdm` y (opcional) `matplotlib`.
- **Windows** (Linux/macOS adaptable).

## ▶️ Cómo ejecutar
source venv/Scripts/activate   # activar entorno virtual
python src/main.py             # lanzar el programa

---

*Repositorio creado por [KingEdhard](https://github.com/KingEdhard)*