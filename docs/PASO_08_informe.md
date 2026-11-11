# PASO 8: Informe en Word (versión breve, centrada en el código)

> **Estado:** ✅ Generado: **28 páginas** (1 de carátula + 27 de contenido), 15 tablas y 2 figuras. Validado contra el esquema de Word y con el índice actualizado.
> **Archivos:** `informe/Informe_Proyecto_SO_Reemplazo_de_Paginas.docx` (+ `.pdf`), `scripts/contenido_informe.py`, `scripts/generar_informe.py`, `scripts/actualizar_indice.ps1`, `graficas/g5_cronograma_gantt.png` (disponible, aunque no se usa en la versión breve)

## Objetivo

Presentar el proyecto con la estructura que pide el enunciado, pero de forma **puntual y centrada en los códigos C** de los 12 algoritmos, usando solo datos del simulador validado.

> 🔄 **Revisión (2026-11-10):** la primera versión tenía 73 páginas. A pedido del usuario se redujo a ~25. Introducción y Capítulo I en uno o dos párrafos por sección, trazas como **matriz compacta 3×30** e informe con **solo los 12 módulos** como código, sin el anexo de código común.

---

## 8.1 Cómo se genera

```
caratula.docx (solo local) ─┐
contenido_informe.py ───────┤
resultados/*.csv ───────────┼──► generar_informe.py ──► informe/*.docx ──► actualizar_indice.ps1 ──► índice + PDF
graficas/*.png ─────────────┤        (python-docx)                           (Microsoft Word)
src/algoritmos/*.c ─────────┘
```

```bash
python scripts/generar_informe.py                                      # crea el .docx
powershell -ExecutionPolicy Bypass -File scripts\actualizar_indice.ps1  # rellena el índice y exporta el PDF
```

- La redacción está en `contenido_informe.py` y el formato en `generar_informe.py`.
- Las trazas se arman desde `resultados/trazas_3marcos.csv` y el código se lee de `src/algoritmos/`. Si cambia un algoritmo: `make resultados` y regenerar.
- Si no existe `caratula.docx` (está excluida de git), el script genera una carátula de texto.

## 8.2 Estructura

| Sección | Contenido | Págs. |
|---|---|---|
| **Carátula** | Universidad, facultad, escuela, título, curso, docente, 5 integrantes (reparto definitivo del Paso 9), Cusco y semestre | — |
| **Introducción** | Evolución del tema, problema y propuesta (un párrafo cada uno) | 1 |
| **Índice** | Automático, 3 niveles, en una página | 2 |
| **Capítulo I** | 1.1 Planteamiento (1.1.1 descripción y 1.1.2 identificación), 1.2 Justificación, 1.3 Limitaciones, 1.4 Delimitaciones, 1.5 Metodología y 1.5.1 Cronograma (tabla tipo MS Project) | 3–4 |
| **Capítulo II** | 2.1 Antecedentes internacionales (2), 2.2 Antecedentes nacionales (1 verificado), 2.3 Condiciones y **12 algoritmos** (responsable, principio de operación, ventaja, desventaja y Belády; **traza 3×30**; resultado; **código C del módulo**), 2.4 Comparación (tabla + 2 gráficas) | 5–25 |
| **Conclusiones, recomendaciones y bibliografía** | 4 conclusiones, 2 recomendaciones y 9 referencias APA 7 | 26–27 |
| **Anexo** | Compilación y ejecución en Linux | 27 |

## 8.3 Formato

- Times New Roman 12, interlineado 1,5, texto justificado, márgenes de 1" (carta), igual que la carátula.
- Tablas y figuras en formato APA 7 («Tabla N», título en cursiva y «*Nota.*» con la fuente).
- **Traza compacta:** filas Ref, Op, M1–M3, Res y Sale; una columna por paso. La página cargada va sombreada y en negrita.
- Código en Consolas 7,5 pt sobre fondo gris claro; numeración de páginas desde la Introducción.

## 8.4 Verificación

| Comprobación | Resultado |
|---|---|
| Validación del `.docx` contra el esquema OOXML | ✅ *All validations PASSED* |
| Word 16: actualización del índice y exportación a PDF | ✅ 28 páginas |
| Revisión visual de todas las páginas | ✅ |
| Números del informe = CSV del simulador = validación del Paso 5 | ✅ |

## 8.5 Problemas encontrados y soluciones

| Problema | Solución |
|---|---|
| python-docx no abría `caratula.docx` (márgenes con decimales de Google Docs) | Se corrigen al copiar la plantilla |
| Error de esquema: falta `w:gutter` en los márgenes | Se agrega `w:gutter="0"` |
| El título quedaba debajo de los logos | Se conservan las líneas vacías donde están anclados los logos |
| Carátula en 2 páginas con todos los integrantes | Lista con interlineado sencillo y dos líneas vacías menos |
| Filas de tabla muy altas | Márgenes de celda explícitos (la plantilla traía 100 twips) |
| Índice en Arial y en 2 páginas | Estilos `TOC1–3` con su id interno y sin la marca de "personalizado", para que Word los use |
| Referencias con `*` visibles en los antecedentes | Se quitó el anidamiento de negrita y cursiva |

## 8.6 Pendientes para los integrantes

1. ~~Nombres de los integrantes~~ ✅ completados en el Paso 9 (faltan los códigos de los integrantes 2 a 5).
2. **Antecedente nacional 2** (opcional): la nota amarilla se quitó en el Paso 9. Si el grupo encuentra una fuente peruana verificada, se agrega en `ANT_NACIONALES`.
3. **Revisar la bibliografía:** solo Ruiz y Raffo (2003) se verificó en línea; conviene confirmar los DOI de las demás.
4. Si se edita el Word a mano: clic derecho en el índice → **Actualizar campo**.

---

**Siguiente paso:** PASO 9. Integración final y entrega.
