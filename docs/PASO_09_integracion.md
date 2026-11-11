# PASO 9: Integración final y entrega

> **Estado:** ✅ Proyecto integrado: compila desde cero sin advertencias, **67/67 pruebas** superadas, reparto definitivo de los 5 integrantes aplicado en el código, el informe y la documentación, y paquete de entrega generado.
> **Archivos:** `src/algoritmos.c` (responsables), `scripts/contenido_informe.py` (integrantes y cronograma), `scripts/empaquetar_entrega.py` (nuevo), `informe/*.docx` + `.pdf` (regenerados), `docs/evidencias/validacion_paso09.txt`

## Objetivo

Comprobar que todas las piezas (simulador de consola, validación, resultados, gráficas, simulador web e informe) funcionen juntas con los mismos datos, aplicar el reparto final del grupo y dejar el proyecto listo para entregar y exponer.

---

## 9.1 Reparto definitivo

El grupo quedó con **5 integrantes**, que van en orden alfabético por apellido. Este reparto reemplaza al inicial de 6 integrantes con 2 algoritmos cada uno.

| N.º | Integrante | Algoritmos | Comandos |
|---|---|---|---|
| 1 | Angel Ismael Alvarez Catunta (221945) | 5 NRU, 7 MFU | `-a 5`, `-a 7` |
| 2 | Haider Alex Carpio Hermoza | 4 Reloj, 11 WSClock | `-a 4`, `-a 11` |
| 3 | Jhamil Jhonatan Huahualuque Vargas | 2 Óptimo, 3 LRU, 12 Aleatorio | `-a 2`, `-a 3`, `-a 12` |
| 4 | Marcus Geuseppe Meza Zamalloa | 8 Reloj Mejorado, 9 Aging | `-a 8`, `-a 9` |
| 5 | Elvis Raúl Suca Hancco | 1 FIFO, 6 LFU, 10 Working Set | `-a 1`, `-a 6`, `-a 10` |

**Dónde se aplicó:**
- **Código C:** campo `responsable` de la tabla `ALGORITMOS[]` en `src/algoritmos.c` y la cabecera de cada `src/algoritmos/*.c`. La columna «Responsable» de la tabla comparativa se amplió a 18 caracteres para que quepan los nombres.
- **Simulador web:** se recompiló `web/motor.wasm` porque lee el responsable desde el mismo C.
- **Informe:** carátula con los 5 nombres, responsable de cada algoritmo en el Capítulo II y cronograma con 15 tareas (una de implementación por integrante, también en el Gantt `g5`).
- **Documentación:** tablas de los Pasos 1, 4 y 6.

Los **resultados no cambian**: el reparto solo afecta a etiquetas, no a la lógica de los algoritmos.

## 9.2 Validación final

| Comprobación | Comando | Resultado |
|---|---|---|
| Compilación desde cero | `make clean && make` | ✅ 0 advertencias (`-std=c11 -Wall -Wextra -pedantic`) |
| Motor web | `make web` (Emscripten) | ✅ `motor.js` + `motor.wasm` regenerados |
| Validación formal (C vs. Python vs. WebAssembly) | `make validar` | ✅ **67/67** pruebas |
| Resultados y gráficas | `make resultados` + `python scripts/graficas.py` | ✅ los mismos números del Paso 6 |
| Informe | `generar_informe.py` + `actualizar_indice.ps1` | ✅ regenerado con índice y PDF |

Evidencia completa: [`evidencias/validacion_paso09.txt`](evidencias/validacion_paso09.txt).

## 9.3 Cómo ejecutar (resumen para el grupo)

```bash
wsl -d Ubuntu                      # desde Windows
cd ".../Proyecto/src"
make                               # compila (si dice "Nothing to be done", ya está compilado)
../build/simulador                 # los 12 algoritmos + tabla comparativa
../build/simulador -r              # solo la tabla
../build/simulador -l              # lista de algoritmos y responsables
../build/simulador -a N            # solo el algoritmo N (1..12)
../build/simulador -a 1 -m 4 -c 1,2,3,4,1,2,5,1,2,3,4,5   # anomalía de Belády
make validar                       # 67 pruebas
make web-servir                    # simulador web en http://localhost:8000
```

`make` solo recompila lo que cambió. Para forzar una compilación completa: `make clean && make`.

## 9.4 Guía de la exposición

Cada integrante ejecuta su `-a N`, explica la traza paso a paso con el código abierto al lado y muestra un dato clave:

| Integrante | Algoritmo | Fallos / escrituras | Qué destacar |
|---|---|---|---|
| Elvis | FIFO (`-a 1`) | 25 / 9 | Cola por orden de llegada. Con la cadena del Tema 3 pasa de 9 a 10 fallos con 4 marcos (Belády). |
| Elvis | LFU (`-a 6`) | 19 / 4 | El mejor realizable, empatado con WSClock. Contador reiniciado a 1 al cargar y empate por FIFO. |
| Elvis | Working Set (`-a 10`) | 20 / 7 | Ventana τ = 4. Expulsa la primera página con edad mayor que τ. |
| Jhamil | Óptimo (`-a 2`) | 15 / 6 | Cota inferior: mira el futuro, así que no es realizable. Ningún algoritmo baja de 15. |
| Jhamil | LRU (`-a 3`) | 22 / 8 | Algoritmo de pila: nunca sufre la anomalía de Belády. |
| Jhamil | Aleatorio (`-a 12`) | 20 / 8 | LCG con semilla 42: el resultado es reproducible. |
| Haider | Reloj (`-a 4`) | 24 / 9 | Bit R y puntero circular (segunda oportunidad). |
| Haider | WSClock (`-a 11`) | 19 / 4 | Reloj + conjunto de trabajo. Programa la escritura de las páginas sucias en lugar de expulsarlas. |
| Angel | NRU (`-a 5`) | 21 / 7 | Clases 2R + M. El bit R se limpia cada 5 referencias. |
| Angel | MFU (`-a 7`) | 25 / 9 | Expulsa la página más usada: empata con FIFO como el peor. |
| Marcus | Reloj Mejorado (`-a 8`) | 21 / 6 | Pares (R, M). Prefiere las páginas limpias para escribir menos a disco. |
| Marcus | Aging (`-a 9`) | 22 / 8 | Contador de 8 bits desplazado. Aquí da la misma traza que LRU. |

**Cierre sugerido:** abrir el simulador web en la pestaña «Comparar los 12 algoritmos» y cargar el preset «Belády (Tema 3)» con 3 y con 4 marcos.

## 9.5 Paquete de entrega

```bash
python scripts/empaquetar_entrega.py
```

El script crea `entrega/Proyecto_SO_Reemplazo_de_Paginas.zip` **solo con los archivos versionados en git**: código, pruebas, scripts, resultados, gráficas, simulador web, documentación e informe (`.docx` + `.pdf`). El material de análisis y la guía de estudio personal quedan fuera automáticamente. La carpeta `entrega/` está en `.gitignore`.

## 9.6 Lista de verificación final

| | Ítem |
|---|---|
| ✅ | 12 algoritmos en C, un módulo por algoritmo, 0 advertencias |
| ✅ | Mismos parámetros para todos (3 marcos, 30 referencias, 12 escrituras) |
| ✅ | 67 pruebas automáticas: valores de control, implementación independiente en Python, propiedades y WebAssembly |
| ✅ | Trazas, CSV y gráficas regenerables con un comando |
| ✅ | Simulador web con el mismo código C |
| ✅ | Informe de 28 páginas con la estructura del enunciado y los 5 integrantes |
| ✅ | Material de análisis fuera de GitHub |
| ✅ | Verificación final automática del PDF: sin marcadores pendientes, citas APA, 5 integrantes, responsables y resultados iguales al CSV, índice completo y toda cita en la bibliografía |
| ✍️ | **A cargo del grupo (opcional):** códigos universitarios de los integrantes 2 a 5, un segundo antecedente nacional y la verificación de los DOI de la bibliografía |

## 9.6 bis Versión extensa del informe (2.0)

Además del informe breve (`informe/`, 28 páginas) se entrega la **versión extensa**: `Informe_Proyecto_SO_Reemplazo_de_Paginas2.0.docx` + `.pdf` (raíz del repositorio, **69 páginas**). Incluye tabla de ventajas y desventajas, traza completa con variables auxiliares, código y citas de cada algoritmo, 7 figuras, validación, simulador web y anexo con el código común.

```bash
python scripts/generar_informe_extenso.py                     # crea el .docx 2.0
powershell -ExecutionPolicy Bypass -File scriptsctualizar_indice.ps1 -Docx Informe_Proyecto_SO_Reemplazo_de_Paginas2.0.docx
```

Se regeneró con el generador original del Paso 8 (`scripts/generar_informe_extenso.py` + `contenido_informe_extenso.py`), aplicando todo lo cambiado desde entonces:

| Cambio | Detalle |
|---|---|
| Integrantes | 5 nombres en la carátula, en la nota del cronograma y como responsables de cada algoritmo; la tabla comparativa muestra el nombre |
| Cronograma y Gantt | 15 tareas con el reparto definitivo |
| Pendientes visibles | Se quitó la nota amarilla del antecedente nacional 2 |
| Formato | «Relación con el proyecto:» seguida de minúscula; decimales con punto en todo el texto; «Tabla 27» y «Tabla 28» en lugar de «Tabla siguiente»; índice en el estilo de Word (Times New Roman) |
| Bibliografía | Se quitó Stallings (2018), que no se citaba en el texto (APA 7 exige que toda referencia esté citada) |
| Afirmaciones corregidas con los datos | WSClock **sí** expulsa la página 0 (paso 22): ahora se explica que escribe poco porque programa escrituras; con 4 marcos, **NRU y LFU** (13) quedan a un fallo del Óptimo; la página 0 de LFU nunca es expulsada desde el paso 2; la leyenda de las trazas describe la columna *Resultado* (Fallo/Acierto) |
| Maquetación | Se eliminó una página en blanco tras el índice (los 9 archivos del Anexo A ya no van al índice) y una página con una sola referencia (la Bibliografía sigue a las Recomendaciones) |

**Verificación del PDF (69 págs.):** sin marcadores pendientes, sin páginas vacías, citas APA, 5 integrantes, 12 responsables correctos, resúmenes iguales al CSV del simulador e índice completo. Además se contrastaron contra las trazas todas las afirmaciones puntuales del texto (pasos 6, 18, 21 y 23, MFU = FIFO paso a paso, curva de 1 a 8 marcos, 600 cadenas aleatorias, 91 anomalías del Aleatorio, ejemplos de Belády de LFU y Working Set).

## 9.7 Problemas encontrados y soluciones

| Problema | Solución |
|---|---|
| Revisión final del texto del informe: citas como «(Silberschatz et al. (2018))» | Se convierten al formato APA 7 entre paréntesis: «(Silberschatz et al., 2018)», «(Tanenbaum & Bos, 2015)» |
| Mayúscula después de «Relación con el proyecto:» | Se pasa a minúscula, como corresponde en español |
| Nota amarilla «[COMPLETAR – Antecedente nacional 2]» visible en el informe | Se quitó del informe. Para agregar otro antecedente: `ANT_NACIONALES` y `BIBLIOGRAFIA` en `contenido_informe.py` |
| La copia `Informe_…Paginas.docx` de la raíz (versión de 73 páginas) se subió por error en el commit de revisión | Se reemplazó por la versión 2.0 regenerada y verificada |
| Word no guardaba a tiempo el PDF de la versión 2.0 antes de cerrarse | Se exportó otra vez el PDF desde el documento ya actualizado |
| Los nombres no cabían en la columna «Responsable» (12 caracteres) | Columna ampliada a 18 y separadores a 96 caracteres |
| `generar_informe.py` falló con *Permission denied* | El `.docx` estaba abierto en Word. Hay que cerrarlo antes de regenerar el informe |
| `actualizar_indice.ps1` quedó colgado mientras el documento seguía abierto | Se cerró solo la instancia oculta de Word (`/Automation`) y se repitió con el archivo cerrado |

---

**Proyecto completo.** Bitácora al 100 % en el [README](../README.md).
