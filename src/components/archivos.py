import tkinter as tk
from tkinter import filedialog
import os

EXTENSIONES_VIDEO = [
    ".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".ts", ".m2ts", ".mts",
    ".m4v", ".mpg", ".mpeg", ".vob", ".evo", ".ogv", ".ogm", ".divx", ".xvid"
]

def seleccionar_archivos(modo):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    filetypes = [
        ("Archivos de video", "*.mkv *.mp4 *.avi *.mov *.wmv *.flv *.webm *.ts *.m2ts *.mts *.m4v *.mpg *.mpeg *.vob"),
        ("Todos los archivos", "*.*")
    ]

    try:
        if modo == '1':
            archivos = list(filedialog.askopenfilenames(
                title="Selecciona las partes en ORDEN (Parte 1, Parte 2...)",
                filetypes=filetypes
            ))
            if not archivos:
                return None
            carpeta = os.path.dirname(archivos[0])
            lista_txt = os.path.join(carpeta, "lista_temp.txt")
            with open(lista_txt, "w", encoding="utf-8") as f:
                for a in archivos:
                    f.write(f"file '{a.replace('\\', '/')}'\n")
            return {
                'archivo_ref': archivos[0],
                'archivos': archivos,
                'lista_txt': lista_txt,
                'carpeta_salida': carpeta
            }
        else:
            archivo_ref = filedialog.askopenfilename(
                title="Selecciona la película a masterizar",
                filetypes=filetypes
            )
            if not archivo_ref:
                return None
            return {
                'archivo_ref': archivo_ref,
                'archivos': [archivo_ref],
                'lista_txt': None,
                'carpeta_salida': os.path.dirname(archivo_ref)
            }
    finally:
        try:
            root.destroy()
        except:
            pass