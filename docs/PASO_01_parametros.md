# PASO 1: Fijar los parámetros del experimento

> **Proyecto:** Algoritmos de reemplazo de páginas. Sistemas Operativos, UNSAAC, semestre 2026-II
> **Docente:** Ing. Emilio Palomino Olivera
> **Estado:** ✅ Completado
> **Archivos generados:** `docs/PASO_01_parametros.md`, `src/parametros.h`, `src/parametros.c`

## Objetivo

Definir **una sola vez** las condiciones del experimento. Así los 12 algoritmos se evalúan con los mismos datos y los resultados se pueden comparar. Ningún integrante debe cambiar estos valores en su módulo. Todos los incluyen desde `src/parametros.h`.

---

## 1.1 Entorno de memoria

| Parámetro | Valor | Justificación |
|---|---|---|
| Marcos físicos | **3** | Lo exige el enunciado. Hay mucha contención (7 páginas distintas para 3 marcos), así que las diferencias entre algoritmos se notan. |
| Longitud de la cadena | **30 referencias** | Lo exige el enunciado. |
| Páginas distintas | **7** → {0, 1, 2, 3, 4, 5, 7} | Cota inferior: **mínimo 7 fallos** (fallos obligatorios o "en frío"). |
| Estado inicial | Los 3 marcos vacíos (`-1`) | Las 3 primeras cargas **cuentan como fallo**, igual que en Silberschatz. |
| Unidad de tiempo | 1 referencia = 1 tic de reloj virtual | La usan Aging (desplazamiento) y WSClock (edad). |

## 1.2 Cadena oficial de referencias

```
Paso: 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
Ref : 7  0  1  2  0  3  0  4  2  3  0  3  2  1  2  0  1  7  0  1  3  5  2  0  1  4  2  3  0  1
```

**Frecuencia por página:**

| Página | 0 | 1 | 2 | 3 | 4 | 5 | 7 | Total |
|---|---|---|---|---|---|---|---|---|
| Veces | 8 | 6 | 6 | 5 | 2 | 1 | 2 | 30 |

**Por qué esta cadena:**
- Los pasos 1 a 20 son la cadena clásica de Silberschatz (Tema 3, sección 9.5). Eso permite contrastar con la bibliografía.
- Hay **localidad temporal**: las páginas 0, 1 y 2 suman 20 de las 30 referencias.
- Hay **cambios de localidad**: las páginas 4, 5 y 7 aparecen poco. Castigan a los algoritmos que expulsan páginas "calientes" (MFU, FIFO).
- La página 0 es la más referenciada, así que sirve para distinguir LFU de MFU.

## 1.3 Patrón de lectura/escritura (bit M)

NRU, Reloj Mejorado y WSClock necesitan saber si una página quedó **modificada (sucia)**. En lugar de inventar escrituras con `i % 2`, se fija un patrón explícito:

```
Paso: 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30
Ref : 7  0  1  2  0  3  0  4  2  3  0  3  2  1  2  0  1  7  0  1  3  5  2  0  1  4  2  3  0  1
Tipo: R  W  R  R  W  R  R  W  W  R  W  R  R  R  W  R  R  R  W  R  W  R  W  W  R  R  R  W  W  R
```

- **12 escrituras (40 %)** y **18 lecturas (60 %)**.
- Las páginas **0 y 2** se modifican con frecuencia: son las páginas de **datos o pila**.
- Las páginas **3 y 4** se modifican pocas veces. Las páginas **1, 5 y 7** nunca se escriben: son las páginas de **código**, de solo lectura.
- Regla del bit M: cuando una página se carga, `M = ESCRITURA[i]`. Cuando hay un acierto, `M = M | ESCRITURA[i]`. M se pone en 0 solo cuando la página se escribe a disco.

## 1.4 Reglas comunes a todos los algoritmos

1. **Se cuenta como fallo** toda referencia a una página que no está en los 3 marcos. Las cargas en marco vacío también cuentan.
2. Si hay un marco vacío, **se usa el marco vacío de menor índice** y no se ejecuta la política de reemplazo.
3. La tabla de traza muestra los marcos por **posición física** (M1, M2, M3), no por orden de cola.
4. Si hay empate entre candidatos a víctima y el algoritmo no define otra regla, **gana el marco de menor índice**.
5. Métricas obligatorias: total de fallos, total de aciertos y tasa de fallos (fallos / 30 × 100 %).

## 1.5 Parámetros específicos por algoritmo

> 🔄 **Revisión (2026-11-09):** el conjunto de algoritmos se alinea con el boceto `Proyecto_Algoritmos_Reemplazo_Paginas_Unificado`. **NRU** y **Working Set** reemplazan a *FIFO Segmentado* y *Page Buffering*. Las demás reglas del enunciado (3 marcos, cadena de 30 referencias, trazas con variables auxiliares, código C funcional) se mantienen.

| # | Algoritmo | Parámetros y decisiones fijadas |
|---|---|---|
| 1 | **FIFO** | Cola de llegada. Se expulsa la página que lleva más tiempo cargada. Un acierto no altera la cola. |
| 2 | **Óptimo (OPT)** | Se expulsa la página cuyo próximo uso está más lejos. Si varias no se vuelven a usar, se expulsa la de menor índice de marco. |
| 3 | **LRU** | Marca de tiempo del último uso por marco. Se expulsa la de marca menor. |
| 4 | **Reloj (Segunda Oportunidad)** | Bit R por marco y puntero circular que empieza en M1. Al cargar o en un acierto: R = 1. Si R = 1, se pone R = 0 y el puntero avanza. Si R = 0, la página es la víctima. Después del reemplazo el puntero avanza una posición. |
| 5 | **NRU (Not Recently Used)** | Bits R y M. **Interrupción de reloj cada `PERIODO_RELOJ` = 5 tics**: al **inicio** de los pasos 6, 11, 16, 21 y 26 se ponen en 0 todos los bits R (M no se toca). Clase = 2·R + M: 0 = (0,0), 1 = (0,1), 2 = (1,0), 3 = (1,1). Se expulsa una página de la **clase más baja**. Empate: la más antigua por llegada (FIFO). Al cargar: R = 1 y M = `ESCRITURA[i]`. En un acierto: R = 1 y `M |= W`. Se diferencia del Reloj Mejorado en que **revisa toda la tabla** y no usa puntero. |
| 6 | **LFU** | Contador de usos por página. **Se reinicia a 1 al cargar** (no hay historial fuera de memoria). Empate: se expulsa la más antigua por llegada (FIFO). |
| 7 | **MFU** | Mismo contador que LFU. Se expulsa la de **mayor** contador. Empate: FIFO. |
| 8 | **Reloj Mejorado (Enhanced Second Chance)** | Clases (R,M): (0,0) < (0,1) < (1,0) < (1,1). Se sigue el algoritmo de segunda oportunidad mejorado de Silberschatz. **Pasada 1:** se busca (0,0) con el puntero, sin modificar bits. **Pasada 2:** se busca (0,1) y se pone R = 0 en cada marco recorrido. Se repite hasta encontrar víctima. M se toma de `ESCRITURA[]`. |
| 9 | **Envejecimiento (Aging)** | Registro de **8 bits** por marco. En un acierto o carga: R = 1 (la página nueva entra con registro 0). **Al final de cada tic:** `reg = (reg >> 1) | (R << 7)`, luego R = 0. Víctima: el registro menor. Empate: menor índice. |
| 10 | **Working Set (Conjunto de Trabajo)** | Versión de Tanenbaum (sección 3.4.8), con **τ = `WS_TAU` = 4 tics** y los bits R limpiados cada `PERIODO_RELOJ` = 5 tics, igual que NRU. Cada marco guarda R y el **tiempo virtual del último uso (TUU)**, que solo se actualiza al cargar o durante el barrido. Un acierto **solo pone R = 1**. En un fallo con memoria llena se recorre la tabla de M1 a M3: (a) si R = 1, TUU = t actual (está en el conjunto de trabajo); (b) si R = 0 y edad = t − TUU **> τ**, la **primera** encontrada es la víctima (está **fuera** del conjunto de trabajo); el barrido sigue solo para actualizar el TUU de las demás; (c) si R = 0 y edad ≤ τ, se recuerda el de mayor edad. Si nadie cumple (b), se expulsa el de mayor edad con R = 0. Si todos tienen R = 1, se expulsa el de menor índice. |
| 11 | **WSClock** | **τ = `WSCLOCK_TAU` = 4 tics**. Cada marco guarda R, M y el tiempo del último uso. En un acierto: R = 1, se actualiza el tiempo y `M |= W`. El puntero recorre los marcos: si R = 1, se pone R = 0, se actualiza el tiempo y avanza. Si R = 0 y edad > τ con M = 0, la página es la víctima. Si R = 0 y edad > τ con M = 1, se **programa la escritura** (M = 0, cuenta 1 escritura) y avanza. Si da una vuelta completa sin víctima, se elige el primer marco con R = 0 y M = 0. Si no existe, se elige el marco bajo el puntero. |
| 12 | **Aleatorio** | Generador **LCG propio** `x = (1103515245·x + 12345) mod 2³¹`, semilla **42**, víctima = `x mod 3`. Se usa un generador propio para que el resultado sea reproducible en cualquier compilador. |

## 1.6 Reparto del trabajo (2 algoritmos por integrante, igual que el boceto)

| Integrante | Código | Algoritmos | Archivos (`src/algoritmos/`) |
|---|---|---|---|
| 1. Angel Ismael Alvarez Catunta | 221945 | FIFO, Óptimo | `fifo.c`, `optimo.c` |
| 2. *[Por completar]* | — | LRU, Reloj | `lru.c`, `reloj.c` |
| 3. *[Por completar]* | — | NRU, LFU | `nru.c`, `lfu.c` |
| 4. *[Por completar]* | — | MFU, Reloj Mejorado | `mfu.c`, `reloj_mejorado.c` |
| 5. *[Por completar]* | — | Aging, Working Set | `aging.c`, `working_set.c` |
| 6. *[Por completar]* | — | WSClock, Aleatorio | `wsclock.c`, `aleatorio.c` |

En cada pareja hay un algoritmo sencillo y uno complejo, para que la carga quede equilibrada.

## 1.7 Valores de control para validar el código (Paso 5)

Calculados de forma independiente con la cadena oficial:

| Algoritmo | Fallos (3 marcos) | Fallos (4 marcos) |
|---|---|---|
| FIFO | 25 | 19 |
| Óptimo | **15** (mínimo posible) | 12 |
| LRU | 22 | 17 |
| Segunda Oportunidad | 24 | 17 |

**Prueba de la anomalía de Belády** (Tema 3, diapositiva 73). Con la cadena `1,2,3,4,1,2,5,1,2,3,4,5`, FIFO da **9 fallos con 3 marcos** y **10 con 4 marcos**.

**Regla de cordura:** ningún algoritmo puede tener **menos de 15 fallos** (el óptimo) ni **menos de 7** (los fallos obligatorios).

## 1.8 Fuentes

- Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating system concepts* (10th ed.). Wiley. Capítulo de memoria virtual, sección *Page Replacement*.
- Tanenbaum, A. S., & Bos, H. (2015). *Modern operating systems* (4th ed.). Pearson. Sección 3.4 (Aging, WSClock, NRU).
- Carr, R. W., & Hennessy, J. L. (1981). WSCLOCK: A simple and effective algorithm for virtual memory management. *Proceedings of the 8th ACM SOSP*, 87–95.
- Material del curso: *Tema 3: Memoria* (diapositivas, secciones 9.5 a 9.7).

---

**Siguiente paso:** PASO 2. Preparar el entorno Linux (WSL + gcc + make).
