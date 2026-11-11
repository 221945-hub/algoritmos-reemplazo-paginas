# PASO 8: Informe en Word

> **Estado:** ✅ Generado: 73 páginas, 28 tablas y 7 figuras. Validado contra el esquema de Word y con el índice actualizado.
> **Archivos generados:** `informe/Informe_Proyecto_SO_Reemplazo_de_Paginas.docx` (+ `.pdf`), `scripts/contenido_informe.py`, `scripts/generar_informe.py`, `scripts/actualizar_indice.ps1`, `graficas/g5_cronograma_gantt.png`
> **Archivos modificados:** `scripts/graficas.py` (diagrama de Gantt)

## Objetivo

Redactar el informe con la estructura que pide el enunciado (prompt de Gemini), usando **exclusivamente datos producidos por el simulador validado**: trazas, métricas, gráficas y código fuente real.

---

## 8.1 Cómo se genera

```
caratula.docx (solo local) ─┐
contenido_informe.py ───────┤
resultados/*.csv ───────────┼──► generar_informe.py ──► informe/*.docx ──► actualizar_indice.ps1 ──► índice + PDF
graficas/*.png, docs/img ───┤        (python-docx)                           (Microsoft Word)
src/**/*.c ─────────────────┘
```

```bash
python scripts/generar_informe.py                                      # crea el .docx
powershell -ExecutionPolicy Bypass -File scripts\actualizar_indice.ps1  # rellena el índice y exporta el PDF
```

- **Separación de contenido y formato:** la redacción está en `contenido_informe.py`. Para cambiar un párrafo no hace falta tocar el código que da formato.
- **Datos siempre actualizados:** las 12 tablas de traza se arman desde `resultados/trazas_3marcos.csv` y el código fuente se lee de `src/`. Si cambia un algoritmo, se ejecuta `make resultados` y se regenera el informe.
- **Carátula:** se usa `caratula.docx` como base, con sus logos y diseño. Si no existe (por ejemplo, en un clon del repositorio, porque está excluida de git), el script genera una carátula de texto.

## 8.2 Estructura del informe (según el enunciado)

| Sección | Contenido | Págs. |
|---|---|---|
| **Carátula** | Universidad, facultad, escuela, título, curso, docente, 6 integrantes (5 por completar), Cusco y semestre | 1 |
| **Introducción** | Evolución del tema (Atlas → paginación por demanda → Belády, Denning, Corbató, WSClock → NVMe), problema (fallos de página, EAT, hiperpaginación) y propuesta | 1–2 |
| **Índice** | Tabla de contenido automática de Word (3 niveles) | 3–4 |
| **Capítulo I** | 1.1 Planteamiento (1.1.1 descripción, 1.1.2 identificación en viñetas), 1.2 Justificación (teórica, técnica y práctica), 1.3 Limitaciones, 1.4 Delimitaciones, 1.5 Metodología, 1.5.1 Cronograma (tabla tipo MS Project con 16 tareas, recursos y predecesoras, más diagrama de Gantt) | 5–10 |
| **Capítulo II** | 2.1 Antecedentes internacionales (4), 2.2 Antecedentes nacionales, 2.3 Temas con modelado de cada algoritmo (fundamentos más **12 algoritmos**, cada uno con: a) teoría, ventajas, desventajas, complejidad y Belády; b) **traza completa de 30 pasos** con variables auxiliares y resumen estadístico; c) **código C real** del módulo; d) citas), 2.4 Evaluación comparativa (tabla y 4 gráficas), 2.5 Validación (67/67), 2.6 Simulador web (capturas) | 11–54 |
| **Conclusiones y recomendaciones** | 7 conclusiones respaldadas por datos y 4 recomendaciones | 55–56 |
| **Bibliografía** | 13 referencias en APA 7 con sangría francesa | 57–58 |
| **Anexos** | A: código común completo (`parametros`, `comun`, `algoritmos`, `main.c`, `Makefile`, `api_web.c`); B: compilación y ejecución en Linux | 59–73 |

## 8.3 Formato aplicado

- Times New Roman 12, interlineado 1,5, texto justificado y márgenes de 1" (carta), igual que la carátula.
- Títulos con estilos de Word (Título 1, 2 y 3) para que el índice se genere solo. Cada capítulo empieza en una página nueva.
- **Tablas y figuras en formato APA 7:** «Tabla N» en negrita, título en cursiva arriba y «*Nota.*» con la fuente debajo.
- Las trazas de 30 pasos caben **cada una en una sola página**, con la página cargada en negrita y sombreada.
- Código en Consolas 7,5 pt sobre fondo gris claro.
- Numeración de páginas desde la Introducción; la carátula no lleva número.
- Viñetas reales de Word (lista con numeración), no caracteres «•» escritos a mano.

## 8.4 Verificación

| Comprobación | Resultado |
|---|---|
| Validación del `.docx` contra el esquema OOXML (validador de la skill docx) | ✅ *All validations PASSED* |
| Apertura en Microsoft Word 16, actualización del índice y exportación a PDF | ✅ 73 páginas, sin errores |
| Revisión visual de las 73 páginas (hojas de contacto) | ✅ Tras corregir los problemas de 8.5 |
| Números del informe = `resultados/*.csv` = validación del Paso 5 | ✅ (las tablas se generan desde los CSV) |

## 8.5 Problemas encontrados y soluciones

| Problema | Causa | Solución |
|---|---|---|
| python-docx no abría `caratula.docx` | Google Docs exporta márgenes con decimales (`1440.0000000000002`) | Se corrigen al copiar la plantilla |
| Error de esquema `pgMar … gutter is required` | La carátula de Google Docs no trae ese atributo | Se agrega `w:gutter="0"` |
| El título quedaba debajo de los logos | Los logos están anclados a las líneas vacías que se habían quitado | Se conservan esas líneas; solo se quitan dos que no sostienen nada |
| La carátula pasaba a 2 páginas con 6 integrantes | Más líneas que la carátula original | Interlineado sencillo en la lista y dos líneas vacías menos |
| Filas de tabla muy altas (trazas partidas en 2 páginas) | El estilo de tabla de la carátula trae 100 twips de margen arriba y abajo | Márgenes de celda explícitos (15 twips) y tablas «unidas» a una página |
| El índice salía en Arial | El estilo base del documento es Arial 11 | Estilos `toc 1–3` en Times New Roman |

## 8.6 Pendientes para los integrantes (antes de entregar)

1. **Nombres y códigos** de los integrantes 2 a 6: editar `INTEGRANTES` en `scripts/contenido_informe.py` y regenerar, o corregirlos directamente en el Word.
2. **Antecedente nacional 2** (resaltado en amarillo en la sección 2.2): agregar una tesis o artículo peruano **verificado** y su referencia en la Bibliografía. Solo se encontró uno verificable: Ruiz y Raffo (2003), *Industrial Data*, UNMSM.
3. **Revisar la bibliografía:** las referencias internacionales se redactaron sin consultarlas en línea; la única verificada en internet es Ruiz y Raffo (2003). Conviene confirmar los DOI.
4. Si se edita el Word a mano, clic derecho en el índice → **Actualizar campo** → **Actualizar toda la tabla**.

---

**Siguiente paso:** PASO 9. Integración final: validación completa, revisión del repositorio y del README, y entrega.
