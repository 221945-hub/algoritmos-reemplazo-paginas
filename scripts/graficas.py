#!/usr/bin/env python3
"""
graficas.py - PASO 6: gráficas comparativas a partir de los CSV de resultados/.

Requiere matplotlib:
    Windows:  python -m pip install matplotlib     ->  python scripts/graficas.py
    Ubuntu:   sudo apt install python3-matplotlib  ->  python3 scripts/graficas.py

Genera en graficas/ (PNG a 200 ppp para el informe + SVG vectorial):
    g1_fallos_por_algoritmo   fallos con 3 marcos, ordenados, con el Óptimo de referencia
    g2_costo_es               costo de E/S = lecturas (fallos) + escrituras a disco
    g3_curva_marcos           fallos vs. marcos (1..8), un panel por algoritmo
    g4_belady                 cadena del Tema 3: 3 vs. 4 marcos (anomalía de Belády)
Todos los datos salen del simulador en C (scripts/generar_resultados.sh).
"""
import csv
import os
import sys

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
except ImportError:
    sys.exit("Falta matplotlib. Instálalo con: python -m pip install matplotlib")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
OUT = os.path.join(RAIZ, "graficas")

# Paleta de referencia (modo claro). Solo se usan los slots 1-3 (validados
# para cualquier combinación de pares) y grises neutros para la referencia.
SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
GRILLA = "#e4e3df"
REFERENCIA = "#8a8984"      # Óptimo: referencia teórica, no una serie más
AZUL = "#2a78d6"            # slot 1
NARANJA = "#eb6834"         # slot 2

NOMBRES = {
    1: "FIFO", 2: "Óptimo (OPT)", 3: "LRU", 4: "Reloj", 5: "NRU", 6: "LFU",
    7: "MFU", 8: "Reloj Mejorado", 9: "Aging", 10: "Working Set",
    11: "WSClock", 12: "Aleatorio",
}

plt.rcParams.update({
    "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE,
    "savefig.facecolor": SUPERFICIE, "font.family": "DejaVu Sans",
    "font.size": 10, "text.color": TEXTO, "axes.labelcolor": TEXTO_2,
    "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "axes.edgecolor": GRILLA, "axes.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
})


def leer(nombre):
    ruta = os.path.join(RES, nombre)
    if not os.path.exists(ruta):
        sys.exit(f"No existe {ruta}. Ejecuta antes: bash scripts/generar_resultados.sh")
    with open(ruta, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    for fl in filas:
        for k in ("ID", "Marcos", "Fallos", "Aciertos", "Escrituras_Disco"):
            fl[k] = int(fl[k])
    return filas


def titulo(fig, texto, subtitulo):
    fig.text(0.02, 0.975, texto, fontsize=13, fontweight="bold", color=TEXTO, va="top")
    fig.text(0.02, 0.925, subtitulo, fontsize=9.5, color=TEXTO_2, va="top")


def guardar(fig, nombre):
    os.makedirs(OUT, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"{nombre}.{ext}"), dpi=200)
    plt.close(fig)
    print(f"  graficas/{nombre}.png / .svg")


def grilla_x(ax):
    ax.xaxis.grid(True, color=GRILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)


# ---------------------------------------------------------------- G1
def g1_fallos(resumen):
    datos = sorted(resumen, key=lambda r: (-r["Fallos"], -r["ID"]))   # mejor arriba
    opt = next(r["Fallos"] for r in resumen if r["ID"] == 2)
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    fig.subplots_adjust(left=0.19, right=0.95, top=0.84, bottom=0.10)
    y = range(len(datos))
    colores = [REFERENCIA if r["ID"] == 2 else AZUL for r in datos]
    ax.barh(list(y), [r["Fallos"] for r in datos], height=0.62, color=colores,
            edgecolor=SUPERFICIE, linewidth=2)
    for i, r in enumerate(datos):
        ax.text(r["Fallos"] + 0.3, i, f"{r['Fallos']}  ({r['Fallos'] / 30 * 100:.1f} %)",
                va="center", fontsize=9, color=TEXTO)
    ax.axvline(opt, color=REFERENCIA, linestyle=(0, (4, 3)), linewidth=1.2)
    ax.text(opt + 0.2, len(datos) - 0.35, f"mínimo teórico = {opt}", color=TEXTO_2,
            fontsize=8.5, va="bottom")
    ax.set_yticks(list(y), [NOMBRES[r["ID"]] for r in datos])
    ax.set_xlim(0, 30)
    ax.set_xlabel("Fallos de página (de 30 referencias)")
    grilla_x(ax)
    titulo(fig, "Fallos de página por algoritmo",
           "3 marcos · cadena oficial de 30 referencias · menos es mejor · "
           "en gris, el Óptimo (no realizable)")
    guardar(fig, "g1_fallos_por_algoritmo")


# ---------------------------------------------------------------- G2
def g2_costo(resumen):
    datos = sorted(resumen, key=lambda r: (-(r["Fallos"] + r["Escrituras_Disco"]), -r["ID"]))
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    fig.subplots_adjust(left=0.19, right=0.95, top=0.80, bottom=0.10)
    y = list(range(len(datos)))
    lect = [r["Fallos"] for r in datos]
    escr = [r["Escrituras_Disco"] for r in datos]
    ax.barh(y, lect, height=0.62, color=AZUL, edgecolor=SUPERFICIE, linewidth=2,
            label="Lecturas de disco (= fallos de página)")
    ax.barh(y, escr, left=lect, height=0.62, color=NARANJA, edgecolor=SUPERFICIE,
            linewidth=2, label="Escrituras de páginas sucias")
    for i, r in enumerate(datos):
        tot = r["Fallos"] + r["Escrituras_Disco"]
        ax.text(tot + 0.3, i, f"{tot}  ({r['Fallos']} + {r['Escrituras_Disco']})",
                va="center", fontsize=9, color=TEXTO)
    ax.set_yticks(y, [NOMBRES[r["ID"]] for r in datos])
    ax.set_xlim(0, 40)
    ax.set_xlabel("Operaciones de E/S a disco")
    grilla_x(ax)
    ax.legend(loc="lower center", bbox_to_anchor=(0.42, 1.0), ncol=2, frameon=False,
              fontsize=9, handlelength=1.2)
    titulo(fig, "Costo total de E/S por algoritmo",
           "3 marcos · cada fallo lee una página; expulsar una página modificada "
           "obliga a escribirla antes")
    guardar(fig, "g2_costo_es")


# ---------------------------------------------------------------- G3
def g3_curva(curva):
    marcos = sorted({r["Marcos"] for r in curva})
    serie = {aid: [next(r["Fallos"] for r in curva if r["ID"] == aid and r["Marcos"] == m)
                   for m in marcos] for aid in NOMBRES}
    fig, axs = plt.subplots(3, 4, figsize=(11, 7.6), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.86, bottom=0.08, wspace=0.12, hspace=0.32)
    for idx, aid in enumerate(NOMBRES):
        ax = axs[idx // 4][idx % 4]
        if aid != 2:
            ax.plot(marcos, serie[2], color=REFERENCIA, linestyle=(0, (4, 3)), linewidth=1.2)
        ax.plot(marcos, serie[aid], color=REFERENCIA if aid == 2 else AZUL, linewidth=2,
                marker="o", markersize=4, markeredgecolor=SUPERFICIE, markeredgewidth=1.5)
        v3 = serie[aid][marcos.index(3)]
        ax.plot([3], [v3], marker="o", markersize=8, color=REFERENCIA if aid == 2 else AZUL,
                markeredgecolor=SUPERFICIE, markeredgewidth=2, zorder=5)
        ax.annotate(f"{v3}", (3, v3), xytext=(6, 6), textcoords="offset points",
                    fontsize=9, fontweight="bold", color=TEXTO)
        ax.set_title(NOMBRES[aid], fontsize=10, color=TEXTO, loc="left", pad=4)
        ax.yaxis.grid(True, color=GRILLA, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(length=0)
        ax.set_xticks(marcos)
        ax.set_ylim(0, 32)
    for ax in axs[-1]:
        ax.set_xlabel("Marcos")
    for fila in axs:
        fila[0].set_ylabel("Fallos")
    leyenda = [Line2D([], [], color=AZUL, linewidth=2, marker="o", markersize=4,
                      label="Algoritmo"),
               Line2D([], [], color=REFERENCIA, linewidth=1.2, linestyle=(0, (4, 3)),
                      label="Óptimo (referencia)"),
               Line2D([], [], color=AZUL, linestyle="none", marker="o", markersize=8,
                      label="3 marcos (experimento)")]
    fig.legend(handles=leyenda, loc="upper right", bbox_to_anchor=(0.985, 0.995), ncol=3,
               frameon=False, fontsize=9)
    titulo(fig, "Fallos de página según la cantidad de marcos",
           "Cadena oficial · con 7 o más marcos caben las 7 páginas distintas "
           "y solo quedan los 7 fallos obligatorios")
    guardar(fig, "g3_curva_marcos")


# ---------------------------------------------------------------- G4
def g4_belady(belady):
    ids = list(NOMBRES)
    f3 = {r["ID"]: r["Fallos"] for r in belady if r["Marcos"] == 3}
    f4 = {r["ID"]: r["Fallos"] for r in belady if r["Marcos"] == 4}
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    fig.subplots_adjust(left=0.19, right=0.76, top=0.80, bottom=0.10)
    for i, aid in enumerate(reversed(ids)):
        a, b = f3[aid], f4[aid]
        ax.plot([a, b], [i, i], color=GRILLA, linewidth=3, solid_capstyle="round", zorder=1)
        ax.plot([a], [i], "o", color=AZUL, markersize=9, markeredgecolor=SUPERFICIE,
                markeredgewidth=2, zorder=3)
        ax.plot([b], [i], "o", color=NARANJA, markersize=9, markeredgecolor=SUPERFICIE,
                markeredgewidth=2, zorder=3)
        if b > a:
            txt, peso = f"▲ anomalía ({a} → {b})", "bold"
        else:
            txt, peso = f"{a} → {b}", "normal"
        ax.text(12.6, i, txt, va="center", fontsize=9, color=TEXTO, fontweight=peso,
                clip_on=False)
    ax.set_yticks(range(len(ids)), [NOMBRES[a] for a in reversed(ids)])
    ax.set_xlim(5, 12.3)
    ax.set_xticks(range(5, 13))
    ax.set_xlabel("Fallos de página")
    grilla_x(ax)
    leyenda = [Line2D([], [], linestyle="none", marker="o", color=AZUL, markersize=9,
                      label="3 marcos"),
               Line2D([], [], linestyle="none", marker="o", color=NARANJA, markersize=9,
                      label="4 marcos")]
    ax.legend(handles=leyenda, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2,
              frameon=False, fontsize=9)
    titulo(fig, "Anomalía de Belády: ¿más memoria, más fallos?",
           "Cadena del Tema 3: 1,2,3,4,1,2,5,1,2,3,4,5 · todas lecturas\n"
           "Si el punto naranja queda a la derecha del azul, agregar un marco empeoró el resultado")
    guardar(fig, "g4_belady")


def main():
    resumen = leer("resumen_3marcos.csv")
    curva = leer("curva_marcos.csv")
    belady = leer("belady_tema3.csv")
    print("Generando graficas:")
    g1_fallos(resumen)
    g2_costo(resumen)
    g3_curva(curva)
    g4_belady(belady)


if __name__ == "__main__":
    main()
