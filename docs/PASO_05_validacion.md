# PASO 5: Validación formal del simulador

> **Estado:** ✅ Completado: **63/63 pruebas superadas**
> **Archivos generados:** `tests/referencia.py`, `tests/validar.py`, `docs/evidencias/validacion_paso05.txt`
> **Archivos modificados:** `src/main.c` (opción `-w` y coma final inválida), `src/Makefile` (objetivos `validar` y `validar-rapido`)

## Objetivo

Demostrar con pruebas **automáticas y repetibles** que el simulador calcula bien:
1. que los resultados coinciden con los **valores de control** y con la teoría del curso (Tema 3);
2. que cada traza coincide **paso a paso** con una **implementación de referencia independiente**;
3. que se cumplen las **propiedades** que cualquier algoritmo correcto debe respetar;
4. que el programa maneja bien los **casos de borde** y las **entradas inválidas**.

---

## 5.1 Cómo ejecutar la validación

```bash
cd src
make validar          # completa: ~35 s (400 casos al azar + 600 cadenas para Belády)
make validar-rapido   # rápida:   ~10 s (60 casos + 150 cadenas)
```
Requiere `python3`, que ya viene en Ubuntu. El script termina con **código 0 si todo pasa** y **1 si algo falla**, así que también sirve para revisar automáticamente el trabajo de cada integrante antes de subirlo.

## 5.2 Diseño de la validación

```
            parametros.h / parametros.c   (fuente única de parámetros)
                    │                          │
                    ▼                          ▼
          ┌──────────────────┐       ┌──────────────────────┐
          │ simulador (C)    │       │ referencia.py        │
          │ build/simulador  │       │ (12 algoritmos,      │
          │                  │       │  escritos aparte)    │
          └────────┬─────────┘       └──────────┬───────────┘
                   │ traza impresa              │ traza en memoria
                   └──────────────┬─────────────┘
                                  ▼
                        validar.py: compara
                  marcos + F/H + escrituras, paso a paso
                  + invariantes + casos de borde + CLI
```

- **`tests/referencia.py`** reimplementa los 12 algoritmos en Python a partir de las reglas escritas del Paso 1, **sin copiar el código C**. Lee la cadena, las escrituras y las constantes (τ, periodo de reloj, semilla, bits) **directamente de `parametros.h` y `parametros.c`**, así que si un parámetro cambia, la referencia lo sigue sin editarla.
- **`tests/validar.py`** ejecuta el simulador real, **lee su traza impresa** y la compara con la referencia.
- **Nueva opción `-w`** en el simulador: permite pasar un **patrón de escrituras propio** junto con `-c`. Sin ella, las cadenas personalizadas eran solo lecturas y no se podían probar a fondo NRU, Reloj Mejorado, WSClock ni el conteo de escrituras.
  ```bash
  ../build/simulador -c 1,2,3,1 -w 0,1,0,1
  ```

## 5.3 Resultados por grupo

| Grupo | Qué se prueba | Pruebas | Resultado |
|---|---|---|---|
| **V1** | `make -B all` sin errores y **0 advertencias** de gcc | 2 | ✅ 2/2 |
| **V2** | Valores de control: FIFO = 25, OPT = 15, LRU = 22, Reloj = 24; Belády del Tema 3 (9 → 10); ningún módulo pendiente | 6 | ✅ 6/6 |
| **V3** | Traza C **idéntica** a la referencia en los 30 pasos, para los 12 algoritmos, con **1 a 8 marcos** | 8 | ✅ 8/8 |
| **V4** | Invariantes en la cadena oficial con 1 a 8 marcos | 8 | ✅ 8/8 |
| **V5** | 10 casos de borde, más 3 comprobaciones de resultado exacto | 13 | ✅ 13/13 |
| **V6** | **400 cadenas al azar**: largo 1 a 64, páginas 0 a 9, escrituras al azar, 1 a 8 marcos. C = referencia e invariantes OK | 1 | ✅ 1/1 |
| **V7** | Propiedad de pila (OPT y LRU) y anomalía de Belády | 4 | ✅ 4/4 |
| **V8** | 15 entradas inválidas → código 2 y mensaje de error; `-h`, `-l` y `-w` válidos | 18 | ✅ 18/18 |
| **V9** | Reproducibilidad (dos ejecuciones idénticas, incluido Aleatorio); CSV correcto; CSV a ruta inválida → código 1 | 3 | ✅ 3/3 |
| | **Total** | **63** | ✅ **63/63** |

La salida completa está en [`docs/evidencias/validacion_paso05.txt`](evidencias/validacion_paso05.txt).

### Invariantes comprobados (V4, V5 y V6)

En **cada traza** de **cada algoritmo** se verifica que:
1. hay exactamente *n* pasos y **fallos + aciertos = n**;
2. el resumen impreso coincide con la cuenta de F en la traza;
3. **fallos ≥ páginas distintas**, porque los fallos obligatorios son inevitables;
4. **fallos ≥ fallos del Óptimo**, porque nadie puede superar al ideal;
5. escrituras a disco ≤ número de accesos W;
6. con **marcos ≥ páginas distintas**, fallos = páginas distintas (nunca hay reemplazo);
7. con **1 marco**, fallos = 1 + número de veces que la página cambia respecto a la anterior;
8. en cada paso la página pedida **queda en memoria** y **no hay páginas duplicadas**;
9. un **acierto no modifica** ningún marco y un **fallo modifica exactamente un** marco.

### Casos de borde (V5)

| Caso | Resultado esperado y obtenido |
|---|---|
| Una sola referencia | 1 fallo |
| Misma página 30 veces (todas W) | 1 fallo y 0 escrituras en los 12 |
| Sin repeticiones (0..29) | 30 fallos en los 12 |
| 1 marco, cadena oficial | 30 fallos (la cadena nunca repite la página anterior) |
| Marcos = páginas distintas (7) | 7 fallos en los 12 |
| Máximo de marcos (8) y cadena de largo máximo (64) | Sin desbordes; idéntico a la referencia |
| Todas escrituras | Idéntico a la referencia |
| Ciclo `0,1,2,3` × 7 con 3 marcos | FIFO y LRU fallan **siempre** (28/28): el peor caso clásico |
| Página con número alto (999) | Correcto |

## 5.4 Anomalía de Belády y propiedad de pila

### Cadena del Tema 3: `1,2,3,4,1,2,5,1,2,3,4,5` (todas lecturas)

| Algoritmo | 3 marcos | 4 marcos | ¿Anomalía? |
|---|---|---|---|
| FIFO | 9 | 10 | ⚠️ **Sí** (la del Tema 3, diapositiva 73) |
| Óptimo | 7 | 6 | No |
| LRU | 10 | 8 | No |
| Reloj | 9 | 10 | ⚠️ **Sí** |
| NRU | 9 | 8 | No |
| LFU | 10 | 8 | No |
| MFU | 9 | 10 | ⚠️ **Sí** |
| Reloj Mejorado | 9 | 10 | ⚠️ **Sí** |
| Aging | 10 | 8 | No |
| Working Set | 10 | 9 | No |
| WSClock | 9 | 10 | ⚠️ **Sí** |
| Aleatorio | 11 | 6 | No |

### Búsqueda en 600 cadenas al azar (6 páginas, largo 8 a 24, de *m* a *m*+1 marcos con *m* = 2..4)

| Algoritmo | Anomalías encontradas | Ejemplo |
|---|---|---|
| FIFO | 0 (pero sí en la cadena del Tema 3) | — |
| **Óptimo** | **0** | — |
| **LRU** | **0** | — |
| Reloj | 4 | `5,1,0,1,5,0,0,3,1,2,2,1,5,4,5,1`: 4 → 5 marcos, 7 → 8 fallos |
| NRU | 0 | — |
| LFU | 1 | `3,4,5,3,0,1,5,1,0,1,4,3,4,1,3,2,3`: 3 → 4 marcos, 9 → 11 fallos |
| MFU | 8 | `1,3,5,0,0,4,0,2,4,0,4,1,0,0,3,3,0,1`: 4 → 5 marcos, 10 → 11 fallos |
| Reloj Mejorado | 14 | `2,0,1,0,1,3,1,2,1,3,4,4,0,3,5,2,5,0,5`: 4 → 5 marcos, 7 → 8 fallos |
| Aging | 0 | — |
| Working Set | 12 | `1,5,2,2,4,2,3,0,0,3,3,3,3,2,0,1,0,5,2,5`: 4 → 5 marcos, 9 → 10 fallos |
| WSClock | 3 | `1,0,2,3,0,3,2,4,5,1,1,4,0,0,2,0,1,3,4`: 4 → 5 marcos, 10 → 11 fallos |
| Aleatorio | 91 | `5,1,0,4,2,4,3,2,5,3,2,4,0`: 2 → 3 marcos, 10 → 11 fallos |

**Conclusiones:**
- ✅ **OPT y LRU nunca presentan la anomalía**, ni en la cadena oficial ni en las 600 cadenas al azar. Lo confirma la teoría: son **algoritmos de pila** (diapositivas 73 a 76).
- ⚠️ FIFO, Reloj, LFU, MFU, Reloj Mejorado, Working Set (con asignación fija de marcos), WSClock y Aleatorio **sí pueden presentarla**: hay al menos un ejemplo concreto de cada uno.
- ℹ️ NRU y Aging no mostraron anomalías en esta búsqueda, pero **eso no demuestra que sean inmunes**: no son algoritmos de pila. Es una búsqueda limitada, y así debe decirse en el informe.
- ℹ️ La anomalía es **rara**: FIFO no la mostró en 600 cadenas cortas al azar, aunque sí en la cadena clásica de Belády. Por eso para FIFO se exige el caso conocido y no la búsqueda al azar (ver 5.6).

### Curva de fallos con la cadena oficial (1 a 8 marcos)

| Algoritmo | 1 | 2 | **3** | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| FIFO | 30 | 25 | **25** | 19 | 15 | 7 | 7 | 7 |
| Óptimo | 30 | 21 | **15** | 12 | 9 | 7 | 7 | 7 |
| LRU | 30 | 27 | **22** | 17 | 11 | 8 | 7 | 7 |
| Reloj | 30 | 25 | **24** | 17 | 13 | 7 | 7 | 7 |
| NRU | 30 | 26 | **21** | 13 | 11 | 7 | 7 | 7 |
| LFU | 30 | 23 | **19** | 13 | 9 | 8 | 7 | 7 |
| MFU | 30 | 25 | **25** | 19 | 13 | 10 | 7 | 7 |
| Reloj Mejorado | 30 | 27 | **21** | 16 | 12 | 7 | 7 | 7 |
| Aging | 30 | 27 | **22** | 17 | 11 | 8 | 7 | 7 |
| Working Set | 30 | 24 | **20** | 15 | 12 | 7 | 7 | 7 |
| WSClock | 30 | 26 | **19** | 14 | 12 | 7 | 7 | 7 |
| Aleatorio | 30 | 25 | **20** | 17 | 13 | 12 | 7 | 7 |

Observaciones útiles para el informe:
- Con **1 marco**, todos dan 30 fallos: la cadena oficial nunca repite la página inmediatamente anterior.
- Con **7 marcos o más**, todos dan **7 fallos**, los obligatorios, porque caben las 7 páginas distintas.
- **FIFO no mejora de 2 a 3 marcos** (25 → 25). Agregar memoria no siempre ayuda.
- **Aging coincide con LRU en todas las columnas**: su aproximación es exacta con esta cadena.
- **3 marcos** (la columna del experimento) es donde las diferencias entre algoritmos son más grandes: de 15 a 25 fallos. Es una buena elección de contención.

## 5.5 Cambios en el simulador durante este paso

| Cambio | Motivo |
|---|---|
| Nueva opción `-w LISTA` (0 = R, 1 = W) | Probar los algoritmos con bit M y el conteo de escrituras con cadenas arbitrarias. Valida que haya solo 0/1 y el mismo largo que la cadena. |
| `-c 1,2,` (coma final) ahora es **inválido** | Antes se aceptaba en silencio. Lo detectó el diseño de las pruebas V8. |
| Objetivos `make validar` y `make validar-rapido` | Que cualquier integrante valide con un solo comando. |

## 5.6 Problemas encontrados durante la validación

| Problema | Diagnóstico | Solución |
|---|---|---|
| En la primera ejecución, 62/63: falló "FIFO presenta anomalías en cadenas al azar" | **Error de la prueba, no del simulador**: la anomalía de FIFO es poco frecuente y no apareció en 150 cadenas cortas | La prueba ahora exige el caso determinista del Tema 3 (9 → 10 fallos). La búsqueda al azar queda como dato informativo. |

No se encontró **ningún error** en los 12 algoritmos en C.

## 5.7 Cómo usar la validación en el equipo

Antes de subir un cambio a GitHub, cada integrante debe ejecutar:
```bash
cd src && make validar-rapido
```
Si el resultado no es `VALIDACION EXITOSA`, el cambio no se sube. El mensaje de falla indica el algoritmo y el **primer paso** donde la traza difiere de la referencia.

---

**Siguiente paso:** PASO 6. Generar los entregables de datos: trazas completas en archivos, CSV consolidado y gráficas comparativas (fallos, escrituras y curva de fallos frente a marcos).
