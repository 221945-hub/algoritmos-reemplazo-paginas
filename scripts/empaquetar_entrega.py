# -*- coding: utf-8 -*-
"""
empaquetar_entrega.py - Arma el paquete de entrega (PASO 9).

Crea entrega/Proyecto_SO_Reemplazo_de_Paginas.zip solo con los archivos versionados
en git (git ls-files). Así nunca se cuela el material de análisis que está en
.gitignore (PDF del tema, carátula, prompt, ZIP del boceto) ni la guía de estudio
personal. Uso, desde la raíz del repositorio:

    python scripts/empaquetar_entrega.py
"""
import os
import subprocess
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "entrega")
NOMBRE = "Proyecto_SO_Reemplazo_de_Paginas"
OBLIGATORIOS = [
    "README.md",
    "informe/Informe_Proyecto_SO_Reemplazo_de_Paginas.docx",
    "informe/Informe_Proyecto_SO_Reemplazo_de_Paginas.pdf",
    "src/Makefile",
    "web/index.html",
    "web/motor.wasm",
]


def archivos_versionados():
    salida = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, capture_output=True, check=True)
    return sorted(f for f in salida.stdout.decode("utf-8").split("\0") if f)


def main():
    archivos = archivos_versionados()
    faltan = [f for f in OBLIGATORIOS if f not in archivos]
    if faltan:
        print("ERROR: faltan archivos obligatorios en git:", ", ".join(faltan))
        return 1
    os.makedirs(DESTINO, exist_ok=True)
    zip_ruta = os.path.join(DESTINO, NOMBRE + ".zip")
    with zipfile.ZipFile(zip_ruta, "w", zipfile.ZIP_DEFLATED) as z:
        for f in archivos:
            z.write(os.path.join(RAIZ, f), f"{NOMBRE}/{f}")
    kb = os.path.getsize(zip_ruta) / 1024
    print(f"Paquete creado: entrega/{NOMBRE}.zip ({len(archivos)} archivos, {kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
