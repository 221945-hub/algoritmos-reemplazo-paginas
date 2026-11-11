#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_informe.py - PASO 8: genera el informe en Word a partir de:
  - caratula.docx (raíz del proyecto, solo local) como portada;
  - scripts/contenido_informe.py (redacción);
  - resultados/*.csv, graficas/*.png y docs/img/*.png (datos del simulador en C);
  - src/ (código fuente que se incluye en el informe).

Uso (Windows o Linux, requiere python-docx):
    python scripts/generar_informe.py
Versión EXTENSA (2.0) del informe. La breve la genera generar_informe.py.
Salida: Informe_Proyecto_SO_Reemplazo_de_Paginas2.0.docx (raíz del proyecto)
El índice se rellena al abrir el documento en Word (o con scripts/actualizar_indice.ps1).
"""
import copy
import csv
import os
import re
import sys
import tempfile
import zipfile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Twips

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contenido_informe_extenso as C  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "src")
CARATULA = os.path.join(RAIZ, "caratula.docx")
SALIDA = os.path.join(RAIZ, "Informe_Proyecto_SO_Reemplazo_de_Paginas2.0.docx")

FUENTE = "Times New Roman"
MONO = "Consolas"
ANCHO_TEXTO = 9360          # twips: carta 8.5" − 2 × 1" de margen
NEGRO = RGBColor(0, 0, 0)
GRIS_CAB = "D9D9D9"

contador = {"tabla": 0, "figura": 0}


# =====================================================================
# Utilidades XML
# =====================================================================
def insertar_antes(padre, elemento, sucesores):
    """Inserta 'elemento' antes del primer hijo cuyo tag esté en 'sucesores' (orden del esquema)."""
    for i, hijo in enumerate(padre):
        if hijo.tag in [qn(s) for s in sucesores]:
            padre.insert(i, elemento)
            return elemento
    padre.append(elemento)
    return elemento


def fijar_fuente(rpr_dueno, nombre):
    rpr = rpr_dueno.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), nombre)


def sombrear_parrafo_estilo(estilo, color):
    ppr = estilo.element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    insertar_antes(ppr, shd, ["w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap",
                              "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN",
                              "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
                              "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
                              "w:textDirection", "w:textAlignment", "w:textboxTightWrap",
                              "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange"])


def nivel_esquema(estilo, nivel):
    ppr = estilo.element.get_or_add_pPr()
    for viejo in ppr.findall(qn("w:outlineLvl")):
        ppr.remove(viejo)
    el = OxmlElement("w:outlineLvl")
    el.set(qn("w:val"), str(nivel))
    insertar_antes(ppr, el, ["w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange"])


def sombrear_celda(celda, color):
    tcpr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    insertar_antes(tcpr, shd, ["w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText",
                               "w:vAlign", "w:hideMark"])


def campo(parrafo, instruccion, texto_provisional=""):
    """Inserta un campo de Word (PAGE, TOC...)."""
    def fld(tipo):
        r = OxmlElement("w:r")
        f = OxmlElement("w:fldChar")
        f.set(qn("w:fldCharType"), tipo)
        r.append(f)
        return r
    p = parrafo._p
    p.append(fld("begin"))
    r = OxmlElement("w:r")
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instruccion} "
    r.append(it)
    p.append(r)
    p.append(fld("separate"))
    run = parrafo.add_run(texto_provisional)
    p.append(fld("end"))
    return run


# =====================================================================
# Documento base: carátula con márgenes corregidos
# =====================================================================
def abrir_base():
    if not os.path.exists(CARATULA):
        print("Aviso: no existe caratula.docx; se usa una portada de texto.")
        return Document(), False
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False).name
    with zipfile.ZipFile(CARATULA) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            datos = zin.read(item.filename)
            if item.filename == "word/document.xml":
                texto = datos.decode("utf-8")
                # Google Docs exporta márgenes con decimales (1440.0000000000002)
                texto = re.sub(r'(w:(?:top|bottom|left|right|header|footer)=")(\d+)\.\d+"', r'\1\2"', texto)
                # y sin el atributo obligatorio w:gutter
                texto = re.sub(r'<w:pgMar (?![^>]*w:gutter)', '<w:pgMar w:gutter="0" ', texto)
                datos = texto.encode("utf-8")
            zout.writestr(item, datos)
    return Document(tmp), True


def texto_parrafo(p):
    return "".join(t.text or "" for t in p._p.iter(qn("w:t")))


def completar_caratula(doc):
    pars = doc.paragraphs
    buscar = lambda txt: next(p for p in pars if texto_parrafo(p).strip().startswith(txt))
    p_titulo, p_curso, p_alumno = buscar("titulo"), buscar("CURSO"), buscar("ALUMNO")
    p_miembro = buscar("Angel Ismael")

    # Título
    r = p_titulo.runs[0]
    r.text = "INFORME DEL PROYECTO DE SISTEMAS OPERATIVOS"
    r.add_break()
    r.add_text("Algoritmos de reemplazo de páginas")

    # Curso y docente
    def completar_linea(p, valor):
        run = p.add_run(valor)
        run.font.name = FUENTE
        fijar_fuente(run._r, FUENTE)
        run.font.size = Pt(12)
        run.font.bold = False
    completar_linea(p_curso, "Sistemas Operativos")
    nuevo = copy.deepcopy(p_curso._p)
    p_curso._p.addnext(nuevo)
    ts = list(nuevo.iter(qn("w:t")))
    ts[0].text = "DOCENTE"
    ts[-1].text = "Ing. Emilio Palomino Olivera"

    # Integrantes, con tabulación fija para alinear los códigos
    for t in p_alumno._p.iter(qn("w:t")):
        t.text = "INTEGRANTES:"
    plantilla = copy.deepcopy(p_miembro._p)
    anterior = p_miembro._p
    for i, (nombre, codigo) in enumerate(C.INTEGRANTES):
        el = p_miembro._p if i == 0 else copy.deepcopy(plantilla)
        if i > 0:
            anterior.addnext(el)
        r = el.find(qn("w:r"))
        for hijo in list(r):
            if hijo.tag in (qn("w:t"), qn("w:tab")):
                r.remove(hijo)
        for tag, val in (("w:t", nombre), ("w:tab", None), ("w:t", codigo)):
            h = OxmlElement(tag)
            if val is not None:
                h.text = val
                h.set(qn("xml:space"), "preserve")
            r.append(h)
        ppr = el.find(qn("w:pPr"))
        tabs = OxmlElement("w:tabs")
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), "left")
        tab.set(qn("w:pos"), "7200")
        tabs.append(tab)
        insertar_antes(ppr, tabs, ["w:spacing", "w:ind", "w:jc", "w:rPr"])
        sp = ppr.find(qn("w:spacing"))
        if sp is not None:
            sp.set(qn("w:line"), "240")
        anterior = el

    # Para que la carátula quepa en 1 página con todos los integrantes se quitan solo dos líneas
    # vacías que no sostienen nada: la que separa FACULTAD de ESCUELA y la previa a CUSCO.
    # Las líneas vacías bajo los logos NO se eliminan: los logos están anclados a esos
    # párrafos y quitarlas los superpone al título.
    pars = doc.paragraphs
    vacio = lambda p: not texto_parrafo(p).strip() and not p._p.xpath(".//w:drawing|.//w:pict")
    i_esc = next(i for i, p in enumerate(pars) if texto_parrafo(p).startswith("ESCUELA"))
    i_cus = next(i for i, p in enumerate(pars) if texto_parrafo(p).startswith("CUSCO"))
    quitar = [pars[i_esc - 1]] if vacio(pars[i_esc - 1]) else []
    quitar += [pars[i_cus - 1]] if vacio(pars[i_cus - 1]) else []
    for p in quitar:
        p._p.getparent().remove(p._p)


def caratula_texto(doc):
    for txt, tam, neg in [
        ("UNIVERSIDAD NACIONAL DE SAN ANTONIO ABAD DEL CUSCO", 14, True),
        ("FACULTAD DE INGENIERÍA ELÉCTRICA, ELECTRÓNICA, INFORMÁTICA Y MECÁNICA", 12, True),
        ("ESCUELA PROFESIONAL DE INGENIERÍA INFORMÁTICA Y DE SISTEMAS", 12, True),
        ("", 12, False), ("INFORME DEL PROYECTO DE SISTEMAS OPERATIVOS", 15, True),
        ("Algoritmos de reemplazo de páginas", 15, True), ("", 12, False),
        ("CURSO: Sistemas Operativos", 12, False), ("DOCENTE: Ing. Emilio Palomino Olivera", 12, False),
        ("INTEGRANTES:", 12, True)] + [(f"{n}    {c}", 12, False) for n, c in C.INTEGRANTES] + [
        ("", 12, False), ("CUSCO - PERÚ", 12, False), ("Semestre 2026 - II", 12, False)]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(txt)
        r.font.size, r.font.bold, r.font.name = Pt(tam), neg, FUENTE


# =====================================================================
# Estilos
# =====================================================================
def configurar_estilos(doc):
    est = doc.styles
    for nivel, tam, alin, antes, despues in [(1, 14, WD_ALIGN_PARAGRAPH.CENTER, 0, 18),
                                             (2, 13, WD_ALIGN_PARAGRAPH.LEFT, 18, 8),
                                             (3, 12, WD_ALIGN_PARAGRAPH.LEFT, 14, 6)]:
        s = est[f"Heading {nivel}"]
        s.font.name, s.font.size, s.font.bold, s.font.italic = FUENTE, Pt(tam), True, False
        s.font.color.rgb = NEGRO
        fijar_fuente(s.element, FUENTE)
        pf = s.paragraph_format
        pf.alignment, pf.space_before, pf.space_after = alin, Pt(antes), Pt(despues)
        pf.keep_with_next, pf.line_spacing = True, 1.15
        pf.page_break_before = (nivel == 1)
        nivel_esquema(s, nivel - 1)

    def nuevo(nombre, tam, fuente=FUENTE, interlineado=1.5, despues=6, alin=None):
        s = est.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = est["Normal"]
        s.font.name, s.font.size = fuente, Pt(tam)
        fijar_fuente(s.element, fuente)
        pf = s.paragraph_format
        pf.line_spacing, pf.space_after, pf.space_before = interlineado, Pt(despues), Pt(0)
        if alin is not None:
            pf.alignment = alin
        return s

    nuevo("Cuerpo", 12, alin=WD_ALIGN_PARAGRAPH.JUSTIFY)
    v = nuevo("Viñeta", 12, alin=WD_ALIGN_PARAGRAPH.JUSTIFY, despues=3)
    v.paragraph_format.left_indent, v.paragraph_format.first_line_indent = Inches(0.5), Inches(-0.25)
    c = nuevo("Código", 7.5, MONO, 1.0, 0)
    c.paragraph_format.left_indent = Inches(0.08)
    sombrear_parrafo_estilo(c, "F2F2F2")
    nuevo("Celda", 9, interlineado=1.0, despues=0)
    nuevo("Etiqueta", 12, interlineado=1.15, despues=0).font.bold = True
    t = nuevo("TituloTabla", 12, interlineado=1.15, despues=6)
    t.font.italic = True
    t.paragraph_format.keep_with_next = True
    est["Etiqueta"].paragraph_format.keep_with_next = True
    est["Etiqueta"].paragraph_format.space_before = Pt(10)
    nuevo("Nota", 10, interlineado=1.15, despues=10)
    b = nuevo("Bibliografía", 12, alin=WD_ALIGN_PARAGRAPH.LEFT, despues=8)
    b.paragraph_format.left_indent, b.paragraph_format.first_line_indent = Inches(0.5), Inches(-0.5)
    nuevo("TítuloSinNumero", 14, interlineado=1.15, despues=18, alin=WD_ALIGN_PARAGRAPH.CENTER).font.bold = True
    # Estilos que Word usa al generar el índice (nombres internos "toc 1".."toc 3")
    for nivel, sangria in ((1, 0), (2, 0.25), (3, 0.5)):
        s = est.add_style(f"toc {nivel}", WD_STYLE_TYPE.PARAGRAPH)
        s.element.styleId = f"TOC{nivel}"      # Word busca los estilos del índice por este id
        s.element.attrib.pop(qn("w:customStyle"), None)   # estilo integrado, no personalizado
        s.base_style = est["Normal"]
        s.font.name, s.font.size = FUENTE, Pt(11)
        fijar_fuente(s.element, FUENTE)
        s.paragraph_format.left_indent = Inches(sangria)
        s.paragraph_format.space_after = Pt(0)
        s.paragraph_format.space_before = Pt(0)
        s.paragraph_format.line_spacing = 1.0
        s.font.bold = (nivel == 1)


# =====================================================================
# Bloques de contenido
# =====================================================================
MARCADO = re.compile(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*|`[^`]+`)")


def texto_con_formato(p, texto, tam=None):
    for trozo in MARCADO.split(texto):
        if not trozo:
            continue
        if trozo.startswith("**"):
            r = p.add_run(trozo[2:-2]); r.bold = True
        elif trozo.startswith("`"):
            r = p.add_run(trozo[1:-1]); r.font.name = MONO; fijar_fuente(r._r, MONO)
            r.font.size = Pt((tam or 12) - 1.5)
        elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
            r = p.add_run(trozo[1:-1]); r.italic = True
        else:
            r = p.add_run(trozo)
        if tam and not trozo.startswith("`"):
            r.font.size = Pt(tam)
    return p


def par(doc, texto, estilo="Cuerpo", alin=None):
    p = doc.add_paragraph(style=estilo)
    if alin is not None:
        p.alignment = alin
    return texto_con_formato(p, texto)


VINETA_NUMID = None     # numId de una lista con viñetas en numbering.xml (de la carátula)


def detectar_vinetas(doc):
    """Busca en la numeración del documento una lista de viñetas reutilizable."""
    global VINETA_NUMID
    try:
        numbering = doc.part.numbering_part.element
    except Exception:  # documento sin numeración
        return
    for num in numbering.findall(qn("w:num")):
        abs_id = num.find(qn("w:abstractNumId")).get(qn("w:val"))
        for an in numbering.findall(qn("w:abstractNum")):
            if an.get(qn("w:abstractNumId")) == abs_id:
                lvl0 = an.find(qn("w:lvl"))
                fmt = lvl0.find(qn("w:numFmt")) if lvl0 is not None else None
                if fmt is not None and fmt.get(qn("w:val")) == "bullet":
                    VINETA_NUMID = num.get(qn("w:numId"))
                    return


def vinetas(doc, items):
    for it in items:
        p = doc.add_paragraph(style="Viñeta")
        if VINETA_NUMID:
            ppr = p._p.get_or_add_pPr()
            numpr = OxmlElement("w:numPr")
            ilvl = OxmlElement("w:ilvl"); ilvl.set(qn("w:val"), "0")
            numid = OxmlElement("w:numId"); numid.set(qn("w:val"), VINETA_NUMID)
            numpr.append(ilvl); numpr.append(numid)
            ppr.insert(1 if ppr.find(qn("w:pStyle")) is not None else 0, numpr)
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.first_line_indent = Inches(-0.25)
        else:
            p.add_run("•\t")
        texto_con_formato(p, it)


def titulo(doc, texto, nivel):
    return doc.add_paragraph(texto, style=f"Heading {nivel}")


def rotulo_tabla(doc, titulo_tabla):
    contador["tabla"] += 1
    doc.add_paragraph(f"Tabla {contador['tabla']}", style="Etiqueta")
    doc.add_paragraph(titulo_tabla, style="TituloTabla")
    return contador["tabla"]


def nota(doc, texto="Elaboración propia con el simulador del proyecto."):
    p = doc.add_paragraph(style="Nota")
    r = p.add_run("Nota. ")
    r.italic = True
    texto_con_formato(p, texto, tam=10)


def figura(doc, ruta, titulo_fig, ancho=6.3, texto_nota=None):
    contador["figura"] += 1
    doc.add_paragraph(f"Figura {contador['figura']}", style="Etiqueta")
    doc.add_paragraph(titulo_fig, style="TituloTabla")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(ruta, width=Inches(ancho))
    nota(doc, texto_nota or "Elaboración propia con los datos del simulador en C.")
    return contador["figura"]


def tabla(doc, encabezados, filas, anchos, tam=9, alinear=None, fmt_celda=None, repetir=True):
    t = doc.add_table(rows=1 + len(filas), cols=len(encabezados))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    tblpr = t._tbl.tblPr
    tblw = tblpr.find(qn("w:tblW"))
    tblw.set(qn("w:type"), "dxa")
    tblw.set(qn("w:w"), str(sum(anchos)))
    bordes = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{lado}")
        b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "4"); b.set(qn("w:space"), "0"); b.set(qn("w:color"), "808080")
        bordes.append(b)
    insertar_antes(tblpr, bordes, ["w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook",
                                   "w:tblCaption", "w:tblDescription"])
    # Márgenes de celda explícitos (el estilo de tabla de la carátula trae 100 twips arriba/abajo)
    margen = OxmlElement("w:tblCellMar")
    for lado, valor in (("top", "15"), ("left", "60"), ("bottom", "15"), ("right", "60")):
        m = OxmlElement(f"w:{lado}"); m.set(qn("w:w"), valor); m.set(qn("w:type"), "dxa"); margen.append(m)
    insertar_antes(tblpr, margen, ["w:tblLook", "w:tblCaption", "w:tblDescription"])
    for i, w in enumerate(anchos):
        t.columns[i].width = Twips(w)
    for ri, fila in enumerate([encabezados] + filas):
        tr = t.rows[ri]
        trpr = tr._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit"); trpr.append(cs)
        if ri == 0 and repetir:
            th = OxmlElement("w:tblHeader"); trpr.append(th)
        for ci, valor in enumerate(fila):
            celda = tr.cells[ci]
            celda.width = Twips(anchos[ci])
            p = celda.paragraphs[0]
            p.style = doc.styles["Celda"]
            if alinear and alinear[ci]:
                p.alignment = alinear[ci]
            if ri == 0:
                r = p.add_run(str(valor)); r.bold = True; r.font.size = Pt(tam)
                sombrear_celda(celda, GRIS_CAB)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                texto_con_formato(p, str(valor), tam=tam)
                if fmt_celda:
                    fmt_celda(ri - 1, ci, celda, p)
            # Mantener la tabla completa en una página (cada fila "unida" a la siguiente)
            if ri < len(filas):
                for cp in celda.paragraphs:
                    cp.paragraph_format.keep_with_next = True
    doc.add_paragraph(style="Nota").paragraph_format.space_after = Pt(0)
    return t


def bloque_codigo(doc, texto):
    for linea in texto.rstrip("\n").split("\n"):
        p = doc.add_paragraph(style="Código")
        p.add_run(linea.replace("\t", "    ") if linea else " ")


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


# =====================================================================
# Secciones del informe
# =====================================================================
def introduccion(doc):
    titulo(doc, "INTRODUCCIÓN", 1)
    for sub, clave in (("Descripción y evolución del tema", "evolucion"),
                       ("Problema", "problema"), ("Propuesta de solución", "propuesta")):
        titulo(doc, sub, 2)
        for t in C.INTRODUCCION[clave]:
            par(doc, t)


def indice(doc):
    p = doc.add_paragraph("ÍNDICE", style="TítuloSinNumero")
    p.paragraph_format.page_break_before = True
    p = doc.add_paragraph(style="Cuerpo")
    campo(p, 'TOC \\o "1-3" \\h \\z \\u',
          "Haga clic derecho aquí y elija «Actualizar campo» para generar el índice.")


def capitulo1(doc):
    titulo(doc, "CAPÍTULO I: PLANTEAMIENTO DEL PROBLEMA Y METODOLOGÍA", 1)
    titulo(doc, "1.1 Planteamiento del problema", 2)
    titulo(doc, "1.1.1 Descripción del problema", 3)
    for t in C.CAP1["descripcion"]:
        par(doc, t)
    titulo(doc, "1.1.2 Identificación del problema", 3)
    par(doc, "Los factores críticos que originan el problema son:")
    vinetas(doc, C.CAP1["identificacion"])
    titulo(doc, "1.2 Justificación", 2)
    for t in C.CAP1["justificacion"]:
        par(doc, t)
    titulo(doc, "1.3 Limitaciones", 2)
    vinetas(doc, C.CAP1["limitaciones"])
    titulo(doc, "1.4 Delimitaciones", 2)
    vinetas(doc, C.CAP1["delimitaciones"])
    titulo(doc, "1.5 Metodología", 2)
    for t in C.CAP1["metodologia"]:
        par(doc, t)
    titulo(doc, "1.5.1 Cronograma", 3)
    par(doc, "La Tabla 1 detalla las fases, tareas, duración (en días hábiles), recursos asignados y "
             "predecesoras, en el formato de una hoja de tareas de MS Project. La Figura 1 muestra el "
             "diagrama de Gantt resultante.")
    rotulo_tabla(doc, "Cronograma del proyecto por fases, tareas, recursos y predecesoras")
    c = WD_ALIGN_PARAGRAPH.CENTER
    tabla(doc, ["ID", "Fase", "Tarea", "Días", "Recursos", "Pred.", "Semana"],
          [[a, b, t, str(d), r, p, s] for a, b, t, d, r, p, s in C.CRONOGRAMA],
          [450, 1500, 3300, 550, 1610, 900, 1050], tam=9,
          alinear=[c, None, None, c, None, c, c])
    nota(doc, "; ".join(f"Integrante {i}: {n}" for i, (n, _) in enumerate(C.INTEGRANTES, 1)) + ".")
    figura(doc, os.path.join(RAIZ, "graficas", "g5_cronograma_gantt.png"),
           "Diagrama de Gantt del proyecto", texto_nota="Elaboración propia a partir de la Tabla 1.")


def minuscula_inicial(texto):
    """En español va minúscula después de dos puntos (salvo siglas o nombres propios como WSClock)."""
    if len(texto) > 1 and texto[0].isupper() and texto[1].islower():
        return texto[0].lower() + texto[1:]
    return texto


def capitulo2(doc, trazas, resumen):
    titulo(doc, "CAPÍTULO II: MARCO TEÓRICO Y MODELADO DE LOS ALGORITMOS", 1)
    titulo(doc, "2.1 Antecedentes internacionales", 2)
    for i, (ref, cuerpo, rel) in enumerate(C.ANT_INTERNACIONALES, 1):
        par(doc, f"**Antecedente internacional {i}.** " + ref)
        par(doc, cuerpo)
        par(doc, "**Relación con el proyecto:** " + minuscula_inicial(rel))

    titulo(doc, "2.2 Antecedentes nacionales", 2)
    for i, (ref, cuerpo, rel) in enumerate(C.ANT_NACIONALES, 1):
        par(doc, f"**Antecedente nacional {i}.** " + ref)
        par(doc, cuerpo)
        par(doc, "**Relación con el proyecto:** " + minuscula_inicial(rel))
    # Para agregar otro antecedente nacional (verificado): C.ANT_NACIONALES y C.BIBLIOGRAFIA.

    titulo(doc, "2.3 Temas relacionados al proyecto con modelado de cada algoritmo", 2)
    titulo(doc, "2.3.1 Fundamentos de la memoria virtual y condiciones del experimento", 3)
    for sub, textos in C.FUNDAMENTOS:
        par(doc, f"**{sub}.** " + textos[0])
        for t in textos[1:]:
            par(doc, t)
    rotulo_tabla(doc, "Cadena oficial de 30 referencias y tipo de operación")
    refs = [r for r in trazas if r["ID"] == "1"]
    anchos = [1100] + [275] * 30
    filas = [["Página"] + [r["Pagina"] for r in refs], ["Operación"] + [r["Operacion"] for r in refs]]
    tabla(doc, ["Paso"] + [str(i) for i in range(1, 31)], filas, [960] + [280] * 30, tam=7,
          alinear=[None] + [WD_ALIGN_PARAGRAPH.CENTER] * 30)
    nota(doc, "R = lectura, W = escritura. 7 páginas distintas; 12 escrituras (40 %). Páginas de datos (0 y 2) "
              "se escriben con frecuencia; páginas de código (1, 5 y 7) solo se leen.")

    por_alg = {}
    for r in trazas:
        por_alg.setdefault(int(r["ID"]), []).append(r)
    res = {int(r["ID"]): r for r in resumen}

    for n, (aid, archivo, nombre, integrante, teoria, ventajas, desventajas, complejidad,
            belady, analisis, citas) in enumerate(C.ALGORITMOS, 2):
        nom_int, _ = C.INTEGRANTES[integrante - 1]
        titulo(doc, f"2.3.{n} Algoritmo {aid}: {nombre}", 3)
        par(doc, f"*Responsable: Integrante {integrante} – {nom_int}*")

        doc.add_paragraph("a) Fundamento teórico y principio de operación", style="Etiqueta")
        for t in teoria:
            par(doc, t)
        rotulo_tabla(doc, f"Ventajas, desventajas, complejidad y anomalía de Belády de {nombre.split(' (')[0]}")
        n_filas = max(len(ventajas), len(desventajas))
        filas = [["• " + ventajas[i] if i < len(ventajas) else "",
                  "• " + desventajas[i] if i < len(desventajas) else ""] for i in range(n_filas)]
        filas.append([f"**Complejidad:** {complejidad}", f"**Anomalía de Belády:** {belady}"])
        tabla(doc, ["Ventajas", "Desventajas"], filas, [4680, 4680], tam=10)

        doc.add_paragraph("b) Modelado y traza completa paso a paso", style="Etiqueta")
        r = res[aid]
        par(doc, f"La Tabla {contador['tabla'] + 1} muestra la ejecución de {nombre.split(' (')[0]} sobre la "
                 "cadena oficial con 3 marcos, tal como la imprime el simulador en C.")
        rotulo_tabla(doc, f"Traza de {nombre.split(' (')[0]} con 3 marcos y 30 referencias")
        filas, previo = [], ["-", "-", "-"]
        cargados = []
        for fila in por_alg[aid]:
            marcos = [fila["M1"], fila["M2"], fila["M3"]]
            cargado = next((k for k in range(3) if marcos[k] != previo[k]), -1) if fila["Resultado"] == "F" else -1
            cargados.append(cargado)
            filas.append([fila["Paso"], fila["Pagina"], fila["Operacion"]] + marcos +
                         ["Fallo" if fila["Resultado"] == "F" else "Acierto", fila["Victima"], fila["Auxiliar"]])
            previo = marcos

        def formato(fi, ci, celda, p, cargados=cargados):
            if 3 <= ci <= 5 and cargados[fi] == ci - 3:
                for run in p.runs:
                    run.bold = True
                sombrear_celda(celda, "FBE0D4")
            if ci == 6 and p.runs and p.runs[0].text == "Fallo":
                p.runs[0].bold = True
            if ci == 8:
                for run in p.runs:
                    run.font.name = MONO
                    fijar_fuente(run._r, MONO)
                    run.font.size = Pt(7)
        cen = WD_ALIGN_PARAGRAPH.CENTER
        tabla(doc, ["Paso", "Ref", "Op", "M1", "M2", "M3", "Resultado", "Víctima", "Variables auxiliares"],
              filas, [470, 450, 400, 430, 430, 430, 880, 760, 5110], tam=8,
              alinear=[cen] * 8 + [None], fmt_celda=formato)
        nota(doc, "En negrita y sombreada, la página cargada en ese paso. Fuente: "
                  f"`resultados/trazas/{aid:02d}_{archivo}.txt`.")
        par(doc, f"**Resumen estadístico:** {r['Fallos']} fallos de página, {r['Aciertos']} aciertos, "
                 f"tasa de fallos {float(r['Tasa_Fallos_Pct']):.2f} % (tasa de aciertos "
                 f"{float(r['Tasa_Aciertos_Pct']):.2f} %) y {r['Escrituras_Disco']} escrituras a disco.")
        for t in analisis:
            par(doc, t)

        doc.add_paragraph("c) Código fuente en lenguaje C para Linux", style="Etiqueta")
        par(doc, f"Módulo `src/algoritmos/{archivo}.c`. Se compila junto con los módulos comunes del Anexo A "
                 "mediante `make` (gcc -std=c11 -Wall -Wextra -pedantic -O2) y se ejecuta con "
                 f"`./simulador -a {aid}`, que imprime la traza anterior y el conteo de fallos.")
        bloque_codigo(doc, leer(os.path.join(SRC, "algoritmos", f"{archivo}.c")))

        doc.add_paragraph("d) Citas bibliográficas", style="Etiqueta")
        par(doc, f"Fundamentado en {citas}")


def evaluacion(doc, resumen):
    titulo(doc, "2.4 Evaluación comparativa de resultados", 2)
    par(doc, f"La Tabla {contador['tabla'] + 1} consolida los resultados de los 12 algoritmos bajo las mismas condiciones "
             "(3 marcos, cadena oficial de 30 referencias).")
    rotulo_tabla(doc, "Resultados de los 12 algoritmos con 3 marcos")
    nombres = {a[0]: a[2].split(" (")[0] for a in C.ALGORITMOS}
    filas = [[r["ID"], nombres[int(r["ID"])], r["Responsable"], r["Fallos"],
              r["Aciertos"], f"{float(r['Tasa_Fallos_Pct']):.2f} %", r["Escrituras_Disco"]] for r in resumen]
    c = WD_ALIGN_PARAGRAPH.CENTER
    tabla(doc, ["#", "Algoritmo", "Responsable", "Fallos", "Aciertos", "% Fallos", "Escrituras"],
          filas, [450, 2400, 1700, 1100, 1100, 1310, 1300], tam=10, alinear=[c, None, None, c, c, c, c])
    nota(doc)
    g = os.path.join(RAIZ, "graficas")
    figura(doc, os.path.join(g, "g1_fallos_por_algoritmo.png"), "Fallos de página por algoritmo (3 marcos)")
    par(doc, "El Óptimo marca el mínimo teórico (15 fallos). Los mejores algoritmos realizables son LFU y "
             "WSClock (19) y los peores, FIFO y MFU (25): entre el mejor y el peor algoritmo real hay 6 fallos, "
             "es decir, el 20 % de las referencias.")
    figura(doc, os.path.join(g, "g2_costo_es.png"), "Costo total de E/S: lecturas (fallos) más escrituras de páginas sucias")
    par(doc, "Al sumar las escrituras, LFU y WSClock siguen primeros (23 operaciones) y son los que menos "
             "escriben (4): LFU conserva la página 0, la más modificada, y WSClock programa la escritura de las "
             "páginas sucias antes de expulsarlas. Reloj Mejorado (27) supera a NRU "
             "(28) con los mismos fallos, lo que confirma su objetivo de diseño: preferir víctimas limpias.")
    figura(doc, os.path.join(g, "g3_curva_marcos.png"), "Fallos de página según la cantidad de marcos (1 a 8)")
    par(doc, "Con 1 marco todos obtienen 30 fallos y con 7 o más, 7 fallos (los obligatorios). Con 3 marcos "
             "las diferencias son máximas (de 15 a 25), lo que justifica la condición del experimento. FIFO y "
             "MFU no mejoran de 2 a 3 marcos, y con 4 marcos NRU y LFU (13) quedan a un fallo del Óptimo (12): el orden "
             "de los algoritmos depende de la memoria disponible.")
    figura(doc, os.path.join(g, "g4_belady.png"), "Anomalía de Belády con la cadena del material del curso")
    par(doc, "FIFO, Reloj, MFU, Reloj Mejorado y WSClock empeoran de 9 a 10 fallos al pasar de 3 a 4 marcos. "
             "Todos eligen la víctima, en algún momento, por orden de llegada o con un puntero circular. LRU y el "
             "Óptimo, por ser algoritmos de pila, nunca presentaron la anomalía, ni en esta cadena ni en 600 "
             "cadenas aleatorias.")

    titulo(doc, "2.5 Validación del simulador", 2)
    par(doc, "La exactitud de los resultados se verificó con el script `tests/validar.py` (`make validar`), "
             "que compara el simulador con una implementación de referencia escrita por separado en Python a "
             f"partir de las reglas del experimento. Se superaron **67 de 67 pruebas** (Tabla {contador['tabla'] + 1}).")
    rotulo_tabla(doc, "Grupos de pruebas de validación")
    grupos = [
        ("V1", "Compilación con gcc sin errores ni advertencias", "2"),
        ("V2", "Valores de control (FIFO 25, OPT 15, LRU 22, Reloj 24) y Belády del Tema 3", "6"),
        ("V3", "Traza idéntica a la referencia con 1 a 8 marcos (12 algoritmos)", "8"),
        ("V4", "Invariantes en cada traza (p. ej., fallos ≥ Óptimo, un fallo cambia un solo marco)", "8"),
        ("V5", "Casos de borde (1 marco, sin repeticiones, máximos, etc.)", "13"),
        ("V6", "400 cadenas aleatorias con lecturas y escrituras", "1"),
        ("V7", "Propiedad de pila (LRU, OPT) y anomalía de Belády", "4"),
        ("V8", "Entradas inválidas en la línea de comandos", "18"),
        ("V9", "Reproducibilidad y exportación CSV", "3"),
        ("V10", "Motor WebAssembly del simulador web idéntico a la referencia (397 casos)", "4"),
    ]
    tabla(doc, ["Grupo", "Qué se comprueba", "Pruebas"], [list(g_) for g_ in grupos] + [["", "**Total**", "**67/67**"]],
          [800, 7300, 1260], tam=10, alinear=[c, None, c])
    nota(doc, "Salida completa en `docs/evidencias/validacion_paso09.txt` del repositorio.")

    titulo(doc, "2.6 Simulador web interactivo", 2)
    par(doc, "Además del programa de consola, el mismo código C se compiló a **WebAssembly** con Emscripten "
             "para ofrecer un simulador interactivo en el navegador. La página no reimplementa los algoritmos: "
             "llama a las funciones de `src/web/api_web.c`, que ejecutan los 12 módulos en C sin cambios. La "
             "prueba V10 comprobó que sus trazas son idénticas a las del programa de consola.")
    vinetas(doc, [
        "**Paso a paso:** animación con reproducir/pausa y velocidad, matriz de marcos con la página cargada, "
        "el acierto y la víctima, explicación en lenguaje natural y variables internas del algoritmo.",
        "**Comparación:** gráfico y tabla de los 12 algoritmos con la misma entrada, y prueba de la anomalía de "
        "Belády con un marco adicional.",
        "**Entradas libres:** cadena de hasta 64 referencias, patrón de lecturas/escrituras y de 1 a 8 marcos.",
        "**Uso:** `make web` compila el motor y `make web-servir` lo abre en http://localhost:8000.",
    ])
    figura(doc, os.path.join(RAIZ, "docs", "img", "web_paso_a_paso.png"),
           "Simulador web: algoritmo del Reloj en el paso 18", ancho=6.3,
           texto_nota="Captura del simulador web del proyecto (motor C compilado a WebAssembly).")
    figura(doc, os.path.join(RAIZ, "docs", "img", "web_comparar.png"),
           "Simulador web: comparación de los 12 algoritmos y prueba de Belády", ancho=5.6,
           texto_nota="Captura del simulador web del proyecto.")


def cierre(doc):
    titulo(doc, "CONCLUSIONES", 1)
    vinetas(doc, C.CONCLUSIONES)
    titulo(doc, "RECOMENDACIONES", 2).paragraph_format.page_break_before = False
    vinetas(doc, C.RECOMENDACIONES)
    titulo(doc, "BIBLIOGRAFÍA", 2).paragraph_format.page_break_before = False
    for ref in C.BIBLIOGRAFIA:
        texto_con_formato(doc.add_paragraph(style="Bibliografía"), ref)


def anexos(doc):
    titulo(doc, "ANEXOS", 1)
    titulo(doc, "Anexo A. Código fuente común del simulador", 2)
    par(doc, "Los módulos de cada algoritmo (Capítulo II) se compilan junto con los siguientes archivos. El "
             "proyecto completo compila con `make` en Linux sin advertencias.")
    for nombre in ("parametros.h", "parametros.c", "comun.h", "comun.c", "algoritmos.h", "algoritmos.c",
                   "main.c", "Makefile", os.path.join("web", "api_web.c")):
        # Etiqueta (no título): así los 9 archivos no alargan el índice
        texto_con_formato(doc.add_paragraph(style="Etiqueta"), f"`src/{nombre.replace(os.sep, '/')}`")
        bloque_codigo(doc, leer(os.path.join(SRC, nombre)))

    titulo(doc, "Anexo B. Compilación y ejecución en Linux", 2)
    bloque_codigo(doc, "\n".join([
        "$ cd src",
        "$ make                       # compila con gcc -std=c11 -Wall -Wextra -pedantic -O2",
        "$ ../build/simulador         # traza de los 12 algoritmos + tabla comparativa",
        "$ ../build/simulador -a 2    # solo el Optimo",
        "$ ../build/simulador -r -m 4 -c 1,2,3,4,1,2,5,1,2,3,4,5   # Belady con 4 marcos",
        "$ ../build/simulador -o resumen.csv -t trazas.csv          # exportar CSV",
        "$ make validar               # 67 pruebas automaticas",
        "$ make web && make web-servir   # simulador web en http://localhost:8000"]))
    par(doc, "Extracto de la tabla comparativa que imprime el simulador en la terminal de Linux:")
    salida = leer(os.path.join(RAIZ, "resultados", "salida_consola.txt"))
    pos = salida.index("TABLA COMPARATIVA")
    inicio = salida.rfind("\n", 0, salida.rfind("\n", 0, pos)) + 1   # línea de '=' anterior al título
    bloque_codigo(doc, salida[inicio:])


# =====================================================================
def main():
    for ruta in ("resultados/resumen_3marcos.csv", "resultados/trazas_3marcos.csv",
                 "graficas/g1_fallos_por_algoritmo.png", "graficas/g5_cronograma_gantt.png",
                 "docs/img/web_paso_a_paso.png"):
        if not os.path.exists(os.path.join(RAIZ, ruta)):
            sys.exit(f"Falta {ruta}: ejecuta antes make resultados, scripts/graficas.py y el Paso 7.")
    with open(os.path.join(RAIZ, "resultados", "trazas_3marcos.csv"), encoding="utf-8") as f:
        trazas = list(csv.DictReader(f))
    with open(os.path.join(RAIZ, "resultados", "resumen_3marcos.csv"), encoding="utf-8") as f:
        resumen = list(csv.DictReader(f))

    doc, con_caratula = abrir_base()
    configurar_estilos(doc)
    detectar_vinetas(doc)
    if con_caratula:
        completar_caratula(doc)
    else:
        caratula_texto(doc)

    # Sección nueva: el contenido lleva número de página; la carátula no
    doc.add_section(WD_SECTION.NEW_PAGE)
    pie = doc.sections[1].footer
    pie.is_linked_to_previous = False
    pp = pie.paragraphs[0]
    pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    numero = campo(pp, "PAGE", "1")
    for r in pp.runs + [numero]:
        r.font.name, r.font.size = FUENTE, Pt(11)
        fijar_fuente(r._r, FUENTE)

    introduccion(doc)
    indice(doc)
    capitulo1(doc)
    capitulo2(doc, trazas, resumen)
    evaluacion(doc, resumen)
    cierre(doc)
    anexos(doc)

    doc.core_properties.title = "Algoritmos de reemplazo de páginas"
    doc.core_properties.subject = "Informe del proyecto de Sistemas Operativos - UNSAAC 2026-II"
    doc.core_properties.author = "Grupo del proyecto de Sistemas Operativos"
    doc.core_properties.language = "es-PE"
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    doc.save(SALIDA)
    print(f"Generado: {os.path.relpath(SALIDA, RAIZ)}  ({contador['tabla']} tablas, {contador['figura']} figuras)")


if __name__ == "__main__":
    main()
