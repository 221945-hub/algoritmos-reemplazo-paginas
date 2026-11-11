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
Salida: informe/Informe_Proyecto_SO_Reemplazo_de_Paginas.docx
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
import contenido_informe as C  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "src")
CARATULA = os.path.join(RAIZ, "caratula.docx")
SALIDA = os.path.join(RAIZ, "informe", "Informe_Proyecto_SO_Reemplazo_de_Paginas.docx")

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
# Secciones del informe (versión breve, centrada en el código)
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
    rotulo_tabla(doc, "Cronograma del proyecto (formato de hoja de tareas de MS Project)")
    c = WD_ALIGN_PARAGRAPH.CENTER
    tabla(doc, ["ID", "Fase", "Tarea", "Días", "Recursos", "Pred.", "Sem."],
          [[a, b, t, str(d), r, p, s] for a, b, t, d, r, p, s in C.CRONOGRAMA],
          [400, 1550, 3500, 500, 1610, 900, 900], tam=8,
          alinear=[c, None, None, c, None, c, c])
    nota(doc, "; ".join(f"Integrante {i}: {n}" for i, (n, _) in enumerate(C.INTEGRANTES, 1))
              + ". Duración total: 21 días hábiles.")


def cita_parentetica(cita):
    """'Tanenbaum y Bos (2015)' -> 'Tanenbaum & Bos, 2015' (APA 7, cita entre paréntesis)."""
    m = re.fullmatch(r"(.+?) \((\d{4})\)", cita.strip())
    if not m:
        return cita
    return f"{m.group(1).replace(' y ', ' & ')}, {m.group(2)}"


def matriz_traza(doc, filas_csv):
    """Traza compacta 3×30: filas Ref, Op, M1–M3 y Res; una columna por paso."""
    n = len(filas_csv)
    previo, cargado = ["-", "-", "-"], []
    for f in filas_csv:
        marcos = [f["M1"], f["M2"], f["M3"]]
        cargado.append(next((k for k in range(3) if marcos[k] != previo[k]), -1)
                       if f["Resultado"] == "F" else -1)
        previo = marcos
    filas = [["Ref"] + [f["Pagina"] for f in filas_csv],
             ["Op"] + [f["Operacion"] for f in filas_csv]]
    for k in range(3):
        filas.append([f"M{k + 1}"] + [f[f"M{k + 1}"] for f in filas_csv])
    filas.append(["Res"] + [f["Resultado"] for f in filas_csv])
    filas.append(["Sale"] + [("" if f["Victima"] == "-" else f["Victima"]) for f in filas_csv])

    def formato(fi, ci, celda, p):
        if ci == 0:
            for r in p.runs:
                r.bold = True
            return
        paso = ci - 1
        if 2 <= fi <= 4 and cargado[paso] == fi - 2:
            sombrear_celda(celda, "FBE0D4")
            for r in p.runs:
                r.bold = True
        if fi == 5 and p.runs and p.runs[0].text == "F":
            p.runs[0].bold = True
    tabla(doc, ["Paso"] + [str(i) for i in range(1, n + 1)], filas, [720] + [288] * n, tam=7,
          alinear=[None] + [WD_ALIGN_PARAGRAPH.CENTER] * n, fmt_celda=formato)


def capitulo2(doc, trazas, resumen):
    titulo(doc, "CAPÍTULO II: MARCO TEÓRICO Y MODELADO DE LOS ALGORITMOS", 1)
    titulo(doc, "2.1 Antecedentes internacionales", 2)
    for ref, cuerpo, rel in C.ANT_INTERNACIONALES:
        par(doc, f"{ref} {cuerpo} **Relación con el proyecto:** {rel[0].lower() + rel[1:]}")
    titulo(doc, "2.2 Antecedentes nacionales", 2)
    for ref, cuerpo, rel in C.ANT_NACIONALES:
        par(doc, f"{ref} {cuerpo} **Relación con el proyecto:** {rel[0].lower() + rel[1:]}")
    # Para agregar otro antecedente nacional (verificado), añadirlo a C.ANT_NACIONALES
    # y su referencia a C.BIBLIOGRAFIA.

    titulo(doc, "2.3 Temas relacionados al proyecto con modelado de cada algoritmo", 2)
    titulo(doc, "2.3.1 Condiciones del experimento", 3)
    par(doc, C.CONDICIONES)
    rotulo_tabla(doc, "Cadena oficial de 30 referencias (R = lectura, W = escritura)")
    refs = [r for r in trazas if r["ID"] == "1"]
    tabla(doc, ["Paso"] + [str(i) for i in range(1, 31)],
          [["Página"] + [r["Pagina"] for r in refs], ["Op"] + [r["Operacion"] for r in refs]],
          [720] + [288] * 30, tam=7, alinear=[None] + [WD_ALIGN_PARAGRAPH.CENTER] * 30)

    por_alg = {}
    for r in trazas:
        por_alg.setdefault(int(r["ID"]), []).append(r)
    res = {int(r["ID"]): r for r in resumen}

    for n, (aid, archivo, nombre, integrante, principio, ventaja, desventaja,
            belady, observacion, cita) in enumerate(C.ALGORITMOS, 2):
        nom_int, _ = C.INTEGRANTES[integrante - 1]
        corto = nombre.split(" (")[0]
        titulo(doc, f"2.3.{n} Algoritmo {aid}: {nombre}", 3)
        par(doc, f"*Responsable: Integrante {integrante} – {nom_int}.*")
        par(doc, f"**Principio de operación.** {principio} **Ventaja:** {ventaja} **Desventaja:** "
                 f"{desventaja} **Anomalía de Belády:** {belady} ({cita_parentetica(cita)}).")
        r = res[aid]
        rotulo_tabla(doc, f"Traza de {corto} con 3 marcos y 30 referencias")
        matriz_traza(doc, por_alg[aid])
        par(doc, f"**Resultado:** {r['Fallos']} fallos, {r['Aciertos']} aciertos, tasa de fallos "
                 f"{float(r['Tasa_Fallos_Pct']):.2f} % y {r['Escrituras_Disco']} escrituras a disco. "
                 f"{observacion}")
        p = doc.add_paragraph(style="Etiqueta")
        texto_con_formato(p, f"Código fuente en C: `src/algoritmos/{archivo}.c` (ejecución: "
                             f"`./simulador -a {aid}`)")
        bloque_codigo(doc, leer(os.path.join(SRC, "algoritmos", f"{archivo}.c")))


def evaluacion(doc, resumen):
    titulo(doc, "2.4 Comparación de resultados", 2)
    rotulo_tabla(doc, "Resultados de los 12 algoritmos con 3 marcos y 30 referencias")
    nombres = {a[0]: a[2].split(" (")[0] for a in C.ALGORITMOS}
    filas = [[r["ID"], nombres[int(r["ID"])], r["Fallos"], r["Aciertos"],
              f"{float(r['Tasa_Fallos_Pct']):.2f} %", r["Escrituras_Disco"]] for r in resumen]
    c = WD_ALIGN_PARAGRAPH.CENTER
    tabla(doc, ["#", "Algoritmo", "Fallos", "Aciertos", "% Fallos", "Escrituras"],
          filas, [500, 3460, 1300, 1300, 1500, 1300], tam=10, alinear=[c, None, c, c, c, c])
    nota(doc)
    g = os.path.join(RAIZ, "graficas")
    figura(doc, os.path.join(g, "g1_fallos_por_algoritmo.png"), "Fallos de página por algoritmo (3 marcos)",
           ancho=4.6)
    par(doc, "El Óptimo marca el mínimo (15). LFU y WSClock son los mejores algoritmos realizables (19) y "
             "FIFO y MFU los peores (25).")
    figura(doc, os.path.join(g, "g4_belady.png"), "Anomalía de Belády con la cadena 1,2,3,4,1,2,5,1,2,3,4,5",
           ancho=4.6)
    par(doc, "Cinco algoritmos empeoran al pasar de 3 a 4 marcos; LRU y el Óptimo, algoritmos de pila, no.")


def cierre(doc):
    titulo(doc, "CONCLUSIONES", 1)
    vinetas(doc, C.CONCLUSIONES)
    titulo(doc, "RECOMENDACIONES", 2)
    vinetas(doc, C.RECOMENDACIONES)
    titulo(doc, "BIBLIOGRAFÍA", 2)
    for ref in C.BIBLIOGRAFIA:
        texto_con_formato(doc.add_paragraph(style="Bibliografía"), ref)


def anexos(doc):
    titulo(doc, "ANEXO: COMPILACIÓN Y EJECUCIÓN EN LINUX", 2)
    par(doc, "Los 12 módulos se compilan junto con los archivos comunes del proyecto (`parametros`, `comun`, "
             "`algoritmos`, `main.c` y `Makefile`), disponibles en el repositorio:")
    bloque_codigo(doc, "\n".join([
        "$ cd src",
        "$ make                    # gcc -std=c11 -Wall -Wextra -pedantic -O2 (0 advertencias)",
        "$ ../build/simulador      # traza de los 12 algoritmos + tabla comparativa",
        "$ ../build/simulador -a 2 # solo un algoritmo (1..12)",
        "$ make validar            # 67 pruebas automaticas"]))


# =====================================================================
def main():
    for ruta in ("resultados/resumen_3marcos.csv", "resultados/trazas_3marcos.csv",
                 "graficas/g1_fallos_por_algoritmo.png", "graficas/g4_belady.png"):
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
