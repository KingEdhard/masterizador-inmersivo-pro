Write-Host "🎬 Configurando Masterizador Inmersivo Pro..." -ForegroundColor Cyan

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python no encontrado. Instálalo desde https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "✔ Python encontrado: $(python --version)" -ForegroundColor Green

if (-not (Test-Path "venv")) {
    Write-Host "🔧 Creando entorno virtual..."
    python -m venv venv
}
Write-Host "✔ Entorno virtual listo" -ForegroundColor Green

Write-Host "📦 Instalando dependencias..."
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "✔ Dependencias instaladas" -ForegroundColor Green

if (-not (Test-Path "bin\ffmpeg.exe")) {
    Write-Host "⬇️ Descargando FFmpeg..."
    $zipUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    $zipFile = "$env:TEMP\ffmpeg.zip"
    $extractPath = "$env:TEMP\ffmpeg_temp"

    Invoke-WebRequest -Uri $zipUrl -OutFile $zipFile
    Expand-Archive -Path $zipFile -DestinationPath $extractPath -Force

    $ffmpegExe = Get-ChildItem -Path $extractPath -Recurse -Name "ffmpeg.exe" | Select-Object -First 1
    $ffprobeExe = Get-ChildItem -Path $extractPath -Recurse -Name "ffprobe.exe" | Select-Object -First 1

    if ($ffmpegExe -and $ffprobeExe) {
        Copy-Item -Path "$extractPath\$ffmpegExe" -Destination "bin\ffmpeg.exe"
        Copy-Item -Path "$extractPath\$ffprobeExe" -Destination "bin\ffprobe.exe"
        Write-Host "✔ FFmpeg descargado y copiado a bin/" -ForegroundColor Green
    } else {
        Write-Host "❌ No se encontraron los binarios en el ZIP. Descarga manual de https://ffmpeg.org" -ForegroundColor Red
    }

    Remove-Item -Path $zipFile -Force
    Remove-Item -Path $extractPath -Recurse -Force
} else {
    Write-Host "✔ FFmpeg ya existe en bin/" -ForegroundColor Green
}

Write-Host "✅ Configuración completada. Ejecuta: python src/main.py" -ForegroundColor Cyan
