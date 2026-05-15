#!/bin/bash
set -e

echo "🎬 Configurando Masterizador Inmersivo Pro..."

if ! command -v python &> /dev/null; then
    echo "❌ Python no encontrado. Instálalo desde https://python.org"
    exit 1
fi
echo "✔ Python encontrado: $(python --version)"

if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python -m venv venv
fi
echo "✔ Entorno virtual listo"

echo "📦 Instalando dependencias..."
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
pip install -r requirements.txt
echo "✔ Dependencias instaladas"

if [ ! -f "bin/ffmpeg.exe" ]; then
    echo "⬇️ Descargando FFmpeg..."
    ZIP_URL="https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    TEMP_DIR=$(mktemp -d)
    TEMP_ZIP="$TEMP_DIR/ffmpeg.zip"
    if command -v curl &> /dev/null; then
        curl -L -o "$TEMP_ZIP" "$ZIP_URL"
    else
        wget -O "$TEMP_ZIP" "$ZIP_URL"
    fi
    unzip -q "$TEMP_ZIP" -d "$TEMP_DIR"
    FFMPEG=$(find "$TEMP_DIR" -name ffmpeg.exe -type f | head -1)
    FFPROBE=$(find "$TEMP_DIR" -name ffprobe.exe -type f | head -1)
    if [ -n "$FFMPEG" ] && [ -n "$FFPROBE" ]; then
        cp "$FFMPEG" bin/ffmpeg.exe
        cp "$FFPROBE" bin/ffprobe.exe
        echo "✔ FFmpeg descargado y copiado a bin/"
    else
        echo "❌ No se encontraron los binarios. Descarga manual desde https://ffmpeg.org"
    fi
    rm -rf "$TEMP_DIR"
else
    echo "✔ FFmpeg ya existe en bin/"
fi

echo "✅ Configuración completada. Ejecuta: python src/main.py"
