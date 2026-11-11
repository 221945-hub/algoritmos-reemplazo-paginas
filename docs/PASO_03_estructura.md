# PASO 3: Estructura modular del código en C

> **Estado:** ✅ Completado
> **Archivos generados:** `src/comun.h`, `src/comun.c`, `src/algoritmos.h`, `src/algoritmos.c`, `src/main.c`, `src/algoritmos/*.c` (12 módulos), `src/Makefile` (actualizado)

## Objetivo

Construir el **esqueleto común** del simulador:
- una sola forma de **recibir los datos** (`Config`);
- una sola forma de **guardar la traza** (`Resultado` / `Paso`);
- una sola forma de **imprimir** las trazas y la tabla comparativa;
- **un archivo por algoritmo**, para que cada integrante trabaje en el suyo sin tocar los demás.

En este paso se implementó **FIFO completo** como **plantilla de referencia**. Los otros 11 módulos quedan creados y compilan, pero se marcan como `PENDIENTE` hasta el Paso 4.

> 🔄 En este paso también se aplicó la **revisión del Paso 1**: el conjunto de algoritmos es ahora el del boceto (NRU y Working Set en lugar de FIFO Segmentado y Page Buffering). Ver `docs/PASO_01_parametros.md`, sección 1.5.

---

## 3.1 Arquitectura

```
                        ┌──────────────────────────────┐
                        │           main.c             │
                        │  opciones (-a -r -m -c -o)   │
                        │  recorre la tabla ALGORITMOS │
                        └──────────────┬───────────────┘
                                       │ ALGORITMOS[k].simular(&cfg, &res)
                        ┌──────────────▼───────────────┐
                        │   algoritmos.c / .h          │
                        │   tabla {id, nombre,         │
                        │   responsable, función}      │
                        └──────────────┬───────────────┘
         ┌──────────┬──────────┬───────┴──┬──────────┬──────────┐
     fifo.c    optimo.c    lru.c   ...  aging.c   wsclock.c  aleatorio.c   (src/algoritmos/)
         └──────────┴──────────┴────┬─────┴──────────┴──────────┘
                                    │ usan
                        ┌───────────▼──────────────────┐
                        │   comun.c / .h               │
                        │   Config, Resultado, Paso    │
                        │   buscar_pagina, registrar_  │
                        │   paso, imprimir_traza ...   │
                        └───────────┬──────────────────┘
                        ┌───────────▼──────────────────┐
                        │ parametros.c / .h (Paso 1)   │
                        │ REFS[30], ESCRITURA[30], τ … │
                        └──────────────────────────────┘
```

## 3.2 Estructura de archivos

```
src/
├── parametros.h / .c     Paso 1: cadena, escrituras y constantes
├── comun.h / .c          Tipos y utilidades compartidas
├── algoritmos.h          Firma común + prototipos de los 12
├── algoritmos.c          Tabla de registro (id, nombre, responsable, función)
├── main.c                Programa principal y opciones de línea de comandos
├── test_parametros.c     Paso 2: prueba del entorno
├── Makefile
└── algoritmos/
    ├── fifo.c            ✅ implementado (plantilla)
    ├── optimo.c          ⏳ Integrante 1
    ├── lru.c  reloj.c    ⏳ Integrante 2
    ├── nru.c  lfu.c      ⏳ Integrante 3
    ├── mfu.c  reloj_mejorado.c   ⏳ Integrante 4
    ├── aging.c  working_set.c    ⏳ Integrante 5
    └── wsclock.c  aleatorio.c    ⏳ Integrante 6
```

> 🔄 **Reparto definitivo (Paso 9, 2026-11-11):** el grupo quedó con 5 integrantes y los responsables se actualizaron. Ver `docs/PASO_09_integracion.md` §9.1.

## 3.3 Tipos de datos (`comun.h`)

### `Config`: lo que **recibe** cada algoritmo
| Campo | Significado |
|---|---|
| `refs` | Cadena de referencias. Por defecto, `REFS` del Paso 1. |
| `escritura` | Patrón R/W. Por defecto, `ESCRITURA`. `NULL` = todas lecturas. |
| `n` | Número de referencias (30). |
| `marcos` | Número de marcos (3). Se puede cambiar con `-m` para las pruebas de Belády. |

### `Paso`: lo que se **guarda en cada referencia**
| Campo | Significado |
|---|---|
| `pagina`, `es_escritura` | Qué se pidió y cómo. |
| `marcos[]` | Contenido de M1..Mn **después** del paso. |
| `marco_cargado` | En qué marco entró la página. **−1 = acierto.** |
| `victima` | Página expulsada (−1 si se usó un marco libre o fue acierto). |
| `aux` | Texto con las **variables auxiliares**: cola, puntero, bits R/M, contadores, etc. Lo pide el enunciado. |

### `Resultado`: el **resultado completo** de un algoritmo
Contiene el nombre, si está implementado, los fallos, los aciertos, las escrituras a disco (para algoritmos con bit M) y los 30 `Paso`.

## 3.4 Interfaz común de un algoritmo

**Todos** los algoritmos tienen exactamente esta firma:
```c
void simular_xxx(const Config *cfg, Resultado *r);
```
Gracias a eso, `algoritmos.c` los guarda en una **tabla de punteros a función** y `main.c` los ejecuta con un simple bucle:
```c
for (int k = 0; k < NUM_ALGORITMOS; k++)
    ALGORITMOS[k].simular(&cfg, &resultados[k]);
```

### Patrón que debe seguir cada módulo (ver `fifo.c`)
```c
void simular_xxx(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    /* ... variables auxiliares propias del algoritmo ... */

    resultado_iniciar(r, "Nombre", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int idx = buscar_pagina(marcos, cfg->marcos, pagina);

        if (idx >= 0) {                       /* ACIERTO */
            /* actualizar auxiliares (bit R, contador...) */
            registrar_paso(r, cfg, i, marcos, -1, -1, "aux=%d", ...);
            continue;
        }
        /* FALLO */
        int marco = buscar_libre(marcos, cfg->marcos), victima = -1;
        if (marco < 0) {
            marco = /* POLÍTICA DE REEMPLAZO */;
            victima = marcos[marco];
        }
        marcos[marco] = pagina;
        registrar_paso(r, cfg, i, marcos, marco, victima, "aux=%d", ...);
    }
}
```
`registrar_paso()` **cuenta automáticamente** fallos y aciertos. El algoritmo solo decide **qué marco** usar.

## 3.5 Opciones del programa (`main.c`)

| Comando | Qué hace |
|---|---|
| `./simulador` | Muestra la traza de los 12 algoritmos y la tabla comparativa |
| `./simulador -a 1 -a 3` | Solo los algoritmos 1 y 3 |
| `./simulador -r` | Solo la tabla comparativa |
| `./simulador -m 4` | Usa 4 marcos |
| `./simulador -c 1,2,3,4,1,2,5,1,2,3,4,5` | Usa una cadena propia (todas lecturas) |
| `./simulador -o resultados.csv` | Exporta los resultados a CSV, para las gráficas |
| `./simulador -l` | Lista los algoritmos y sus responsables |
| `./simulador -h` | Ayuda |

Los errores (algoritmo inexistente, marcos fuera de rango, cadena mal escrita) se informan por `stderr` y el programa termina con **código 2**.

## 3.6 Makefile actualizado

- Cada `.c` se compila **por separado** a un `.o` en `build/`. Si un integrante cambia solo `lru.c`, solo se recompila ese archivo.
- `$(wildcard algoritmos/*.c)` incluye automáticamente cualquier módulo de la carpeta.

| Comando | Acción |
|---|---|
| `make` | Compila `simulador` y `test_parametros` |
| `make run` | Compila y ejecuta el simulador completo |
| `make test` | Prueba de parámetros (Paso 2) |
| `make clean` | Borra `build/` |

## 3.7 Pruebas realizadas (WSL, gcc 15.2)

| Prueba | Resultado |
|---|---|
| `make clean && make` | ✅ 16 archivos compilados, **0 advertencias** |
| FIFO con la cadena oficial y 3 marcos | ✅ **25 fallos / 5 aciertos**, igual al valor de control del Paso 1 |
| Belády: FIFO, `-c 1,2,3,4,1,2,5,1,2,3,4,5` | ✅ **9 fallos con `-m 3`** y **10 fallos con `-m 4`** |
| `-a 13`, `-m 0`, `-c 1,x` | ✅ Mensaje de error y código de salida 2 |
| `-o archivo.csv` | ✅ CSV generado (solo los algoritmos implementados) |
| `make test` | ✅ ENTORNO LISTO (0 fallas) |

### Salida real de FIFO (`./simulador -a 1`)
```
====================================================================================================
 ALGORITMO 1: FIFO   |   Responsable: Integrante 1
 Marcos: 3   |   Referencias: 30
====================================================================================================
 Paso | Ref | Op |  M1   M2   M3 | Res | Sale | Variables auxiliares
----------------------------------------------------------------------------------------------------
    1 |   7 |  R |   7*   -    - |  F  |    - | cola=[7]
    2 |   0 |  W |   7    0*   - |  F  |    - | cola=[7,0]
    3 |   1 |  R |   7    0    1*|  F  |    - | cola=[7,0,1]
    4 |   2 |  R |   2*   0    1 |  F  |    7 | cola=[0,1,2]
    5 |   0 |  W |   2    0    1 |  H  |    - | cola=[0,1,2]
    6 |   3 |  R |   2    3*   1 |  F  |    0 | cola=[1,2,3]
    7 |   0 |  R |   2    3    0*|  F  |    1 | cola=[2,3,0]
    8 |   4 |  W |   4*   3    0 |  F  |    2 | cola=[3,0,4]
    9 |   2 |  W |   4    2*   0 |  F  |    3 | cola=[0,4,2]
   10 |   3 |  R |   4    2    3*|  F  |    0 | cola=[4,2,3]
   11 |   0 |  W |   0*   2    3 |  F  |    4 | cola=[2,3,0]
   12 |   3 |  R |   0    2    3 |  H  |    - | cola=[2,3,0]
   13 |   2 |  R |   0    2    3 |  H  |    - | cola=[2,3,0]
   14 |   1 |  R |   0    1*   3 |  F  |    2 | cola=[3,0,1]
   15 |   2 |  W |   0    1    2*|  F  |    3 | cola=[0,1,2]
   16 |   0 |  R |   0    1    2 |  H  |    - | cola=[0,1,2]
   17 |   1 |  R |   0    1    2 |  H  |    - | cola=[0,1,2]
   18 |   7 |  R |   7*   1    2 |  F  |    0 | cola=[1,2,7]
   19 |   0 |  W |   7    0*   2 |  F  |    1 | cola=[2,7,0]
   20 |   1 |  R |   7    0    1*|  F  |    2 | cola=[7,0,1]
   21 |   3 |  W |   3*   0    1 |  F  |    7 | cola=[0,1,3]
   22 |   5 |  R |   3    5*   1 |  F  |    0 | cola=[1,3,5]
   23 |   2 |  W |   3    5    2*|  F  |    1 | cola=[3,5,2]
   24 |   0 |  W |   0*   5    2 |  F  |    3 | cola=[5,2,0]
   25 |   1 |  R |   0    1*   2 |  F  |    5 | cola=[2,0,1]
   26 |   4 |  R |   0    1    4*|  F  |    2 | cola=[0,1,4]
   27 |   2 |  R |   2*   1    4 |  F  |    0 | cola=[1,4,2]
   28 |   3 |  W |   2    3*   4 |  F  |    1 | cola=[4,2,3]
   29 |   0 |  W |   2    3    0*|  F  |    4 | cola=[2,3,0]
   30 |   1 |  R |   1*   3    0 |  F  |    2 | cola=[3,0,1]
----------------------------------------------------------------------------------------------------
 (*) pagina cargada en ese paso   F = fallo de pagina   H = acierto
 Fallos: 25 | Aciertos: 5 | Tasa de fallos: 83.33 % | Tasa de aciertos: 16.67 %
```

**Cómo leer la traza:** `Op` indica si la referencia es lectura (R) o escritura (W). `*` marca el marco donde entró la página. `Sale` es la víctima expulsada. La columna de la derecha muestra el estado interno del algoritmo; en FIFO es la cola de llegada, de la más antigua a la más nueva.

## 3.8 Diferencias con el boceto del ZIP

| Boceto (`simulador_paginacion.c`) | Nueva estructura |
|---|---|
| Un solo archivo de 628 líneas | 12 módulos más archivos comunes; un archivo por integrante |
| Cadena y marcos fijos en el código | Configurables con `-c` y `-m`, para las pruebas de Belády y validación |
| Solo marcos y F/H | Traza con operación R/W, víctima y **variables auxiliares** |
| Escrituras con `i % 2`, `i % 3` | Patrón fijo `ESCRITURA[]` del Paso 1 |
| CSV a una ruta inexistente | CSV a la ruta que elija el usuario con `-o`, avisando si hay error |
| Sin control de errores | Valida las opciones y devuelve un código de salida |

---

**Siguiente paso:** PASO 4. Implementar los 11 algoritmos restantes siguiendo la plantilla de `fifo.c` y las reglas del Paso 1.
