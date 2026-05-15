cat > README.md << 'EOF'
# 🎬 Masterizador Inmersivo Pro v7.0 (Arquitectura de Componentes)

## 📌 Descripción general

Procesa archivos de video (MKV/MP4) aplicando un filtro que realza las voces (+2 dB entre 400 Hz y 4000 Hz), normaliza el volumen y realiza un **upmix inteligente a 5.1 o 7.1** según la elección del usuario.  
El audio mejorado se codifica en **E‑AC3 (Dolby Digital Plus) a 1024 kbps** y se añade como una nueva pista predeterminada, **conservando sin modificar todas las pistas originales**, subtítulos, capítulos y archivos adjuntos.

---

## 🔄 Flujo de trabajo

1. **Menú principal**  
   - Opción 1: Unir múltiples partes de una película antes de masterizar.  
   - Opción 2: Masterizar un único archivo.  
   - Opción 3: Salir.

2. **Selección de archivos**  
   - Diálogo gráfico filtrado solo para archivos de video (.mkv, .mp4, .avi, etc.).  
   - En modo unión se crea automáticamente un archivo `lista_temp.txt` para concatenación con FFmpeg.

3. **Análisis técnico con ffprobe**  
   - Resolución real del video (ej. `1920p x 1080p`).  
   - Duración total del contenedor.  
   - Lista de pistas de audio con formato “estilo VLC”: `[índice] título (CÓDEC canales)`.  
   - Se valida que el archivo sea realmente multimedia y que contenga al menos una pista de audio.

4. **Selección de pista de audio a masterizar**  
   - El usuario escribe el número exacto de la pista deseada.

5. **Elección de canales de salida** 🆕  
   - `1`: 5.1 surround  
   - `2`: 7.1 surround (por defecto)

6. **Configuración de formato y nombre de salida**  
   - Se pregunta **una sola vez** el contenedor destino (`mp4`/`mkv`).  
   - Si se elige MP4 y el archivo original contiene códecs de audio no compatibles con MP4 (DTS, TrueHD, FLAC, etc.), se advierte y se sugiere cambiar automáticamente a MKV.  
   - Se propone un nombre base (por defecto el nombre del archivo original) y se muestra la **ruta final completa** antes de continuar (solo presionar Enter).

7. **Política de subtítulos**  
   - **MKV**: se copian todos los subtítulos originales sin modificar.  
   - **MP4**: si hay subtítulos PGS o DVD (incompatibles con `mov_text`), se omiten automáticamente para evitar errores de empaquetado.

8. **Construcción del filtro de audio**  
   - Normalización dinámica: `dynaudnorm=f=150:g=31:p=0.95`  
   - Realce de voces: `firequalizer` con +2 dB entre 400 Hz y 4000 Hz  
   - Upmix multicanal mediante `pan` (ver sección dedicada).

9. **Ejecución de FFmpeg**  
   - Barra de progreso basada en el tiempo.  
   - Si se produce un error de empaquetado (subtítulos/attachments), se activa automáticamente un **fallback a MP4 sin subtítulos problemáticos**.

10. **Post‑proceso**  
    - Mensaje de éxito con la ubicación del archivo.  
    - Opcionalmente, se muestra una **gráfica comparativa** de formas de onda (original vs. masterizado) usando `matplotlib`.

---

## 🔊 Mejoras en el audio

### 1. Normalización dinámica (Dynaudnorm)
- **Parámetros:** `f=150` (tamaño de ventana de análisis), `g=31` (ganancia máxima), `p=0.95` (percentil de referencia).  
- **Efecto:** nivela el volumen sin distorsionar los picos transitorios, evitando que pasajes bajos se pierdan y que los altos saturen.

### 2. Realce de voces (Firequalizer)
- **Filtro:** `gain = if(gte(f,400), if(lte(f,4000), 2, 0), 0)`  
- **Efecto:** aplica **exactamente +2 dB** en la banda de frecuencias vocales (400‑4000 Hz). Fuera de esa banda la ganancia es 0 dB (sin alterar).  
- **Nota:** Las comas dentro del filtro se escapan con `\` para la sintaxis de FFmpeg.

### 3. Upmix a 5.1 o 7.1 (pan dinámico)
La matriz de `pan` se adapta al número de canales de la pista original y a la salida deseada:

| Fuente original | Salida 5.1 | Salida 7.1 |
|-----------------|------------|------------|
| **Mono / Estéreo** | FL/FR directos, FC=0.5FL+0.5FR, LFE=0.5FL+0.5FR, traseros = FL/FR | FL/FR directos, FC/LFE creados, traseros y laterales copiados desde FL/FR |
| **5.1** | Copia directa de los 6 canales | Copia directa de los canales 5.1; laterales se generan a partir de los traseros |
| **7.1** | Mezcla de 7.1 → 5.1 (omitiendo laterales) | Copia directa de los 8 canales |

Esto asegura una **compatibilidad óptima** sin perder información direccional.

---

## 📦 Conservación de datos originales

- **Vídeo:** copiado sin recodificar (`-c:v copy`).  
- **Todas las pistas de audio originales:** se copian con su códec original y se les quita la bandera `default`.  
- **Subtítulos:**  
  - MKV → copiados tal cual.  
  - MP4 → convertidos a `mov_text` (si son compatibles) o descartados si son gráficos.  
- **Capítulos y metadatos globales:** copiados íntegramente.  
- **Archivos adjuntos (fuentes, carátulas):** copiados sin modificaciones.

La nueva pista masterizada se coloca como **primera pista de audio** y se marca como **predeterminada (default)**, con el título descriptivo:  
`NombreBase E-AC3 5.1 Masterizado (Voces +2dB)` (o 7.1 según la elección).

---

## 🛡️ Manejo de errores

| Situación | Comportamiento |
|-----------|----------------|
| Archivo no multimedia (extensión .torrent, .zip, etc.) | `ffprobe` no detecta pistas → se cancela y vuelve al menú |
| Códecs de audio originales no compatibles con MP4 | Advertencia y sugerencia de cambio automático a MKV |
| Error de timestamps en MKV | Se fuerza regeneración con `-fflags +genpts` |
| Error de empaquetado por subtítulos/attachments | Fallback automático a MP4 sin subtítulos, eliminando el archivo MKV fallido |
| Otros errores de FFmpeg | Se muestra el `stderr` y se retorna al menú |
| Cancelación del usuario | En cualquier momento (nombre, confirmación, etc.) el programa retorna limpiamente al menú |

---

## 📈 Precisión del upmix

- **Distribución de canales:** respeta exactamente la asignación de canales de la fuente (cuando es multicanal). En estéreo/mono, la creación del canal central y LFE se hace mediante **mezcla ponderada** (coeficiente 0.5), que es el estándar de la industria para evitar saturación.  
- **No se introducen desfases ni artificios:** el `pan` de FFmpeg es un simple enrutamiento sin filtros adicionales, por lo que la **fidelidad es 1:1** respecto a la fuente en los canales directos.  
- La **codificación E‑AC3 a 1024 kbps** ofrece una calidad perceptualmente idéntica al original para la mayoría de los casos (transparencia auditiva incluso en sistemas de alta gama).

---

## 🔧 Requisitos técnicos

- **FFmpeg/FFprobe** (ejecutables en la carpeta `bin/`).  
- **Python 3.6+** con librerías: `numpy`, `tqdm`, `matplotlib` (opcional para gráfica).  
- **Sistema operativo:** Windows (compatible con Linux/macOS si se ajustan rutas).

---

## ▶️ Cómo ejecutar

```bash
source venv/Scripts/activate   # activar entorno virtual
python src/main.py             # lanzar el programa