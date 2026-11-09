# PASO 4: Implementación de los 12 algoritmos

> **Estado:** ✅ Completado
> **Archivos modificados:** los 11 módulos de `src/algoritmos/` (todos menos `fifo.c`, que ya estaba listo) y `src/comun.h` / `src/comun.c`, que ahora cuentan las escrituras a disco.

## Objetivo

Implementar en C los 11 algoritmos que estaban pendientes. Cada uno sigue **exactamente** las reglas fijadas en `docs/PASO_01_parametros.md` (sección 1.5), usa la plantilla de `fifo.c` y muestra en la traza sus **variables auxiliares**.

---

## 4.1 Resultados con la cadena oficial (3 marcos, 30 referencias)

Salida de `./simulador -r`:

| Nro | Algoritmo | Responsable | Fallos | Aciertos | % Fallos | % Aciertos | Escrituras a disco |
|---|---|---|---|---|---|---|---|
| 1 | FIFO | Integrante 1 | 25 | 5 | 83.33 % | 16.67 % | 9 |
| 2 | **Óptimo (OPT)** | Integrante 1 | **15** | 15 | **50.00 %** | 50.00 % | 6 |
| 3 | LRU | Integrante 2 | 22 | 8 | 73.33 % | 26.67 % | 8 |
| 4 | Reloj (Clock) | Integrante 2 | 24 | 6 | 80.00 % | 20.00 % | 9 |
| 5 | NRU | Integrante 3 | 21 | 9 | 70.00 % | 30.00 % | 7 |
| 6 | **LFU** | Integrante 3 | **19** | 11 | 63.33 % | 36.67 % | **4** |
| 7 | MFU | Integrante 4 | 25 | 5 | 83.33 % | 16.67 % | 9 |
| 8 | Reloj Mejorado | Integrante 4 | 21 | 9 | 70.00 % | 30.00 % | 6 |
| 9 | Aging | Integrante 5 | 22 | 8 | 73.33 % | 26.67 % | 8 |
| 10 | Working Set | Integrante 5 | 20 | 10 | 66.67 % | 33.33 % | 7 |
| 11 | **WSClock** | Integrante 6 | **19** | 11 | 63.33 % | 36.67 % | **4** |
| 12 | Aleatorio (RAND) | Integrante 6 | 20 | 10 | 66.67 % | 33.33 % | 8 |

✅ Los 4 **valores de control** del Paso 1 se cumplen: FIFO = 25, OPT = 15, LRU = 22 y Reloj = 24.
✅ Ningún algoritmo baja de 15 fallos, que es el mínimo que da el Óptimo.

### Nueva métrica: escrituras a disco

`comun.c` ahora lleva la cuenta de las **páginas sucias** (bit M = 1) en todos los algoritmos:
- En una **escritura** (W), el marco queda marcado como sucio.
- Cuando se **expulsa** una página sucia, se suma **1 escritura a disco**, porque hay que guardarla antes de reutilizar el marco.
- WSClock **programa** escrituras antes de expulsar (`marcar_escrito()`). Esas también se cuentan, pero una sola vez.

Así se compara con el mismo criterio el **costo real de E/S**, no solo los fallos. Por ejemplo, NRU y Reloj Mejorado empatan en fallos (21), pero Reloj Mejorado escribe menos (6 frente a 7), porque prefiere víctimas limpias.

---

## 4.2 Detalle por algoritmo

Cada extracto muestra los **pasos 18 a 24** de la traza real. En ese tramo la cadena cambia de localidad (`7 0 1 3 5 2 0`) y los algoritmos se diferencian claramente. Para ver la traza completa: `./simulador -a N`.

### 1. FIFO (`fifo.c`): Integrante 1
Usa un puntero circular al marco más antiguo; un acierto no altera la cola. **Auxiliar:** `cola`, de la página más antigua a la más nueva. Detalle completo en el Paso 3.

### 2. Óptimo (`optimo.c`): Integrante 1
- En cada fallo calcula, para cada marco, el **paso del próximo uso** de su página y expulsa la más lejana. `--` significa que la página no vuelve a usarse.
- Empate entre varias que no vuelven a usarse: gana el menor índice de marco.
- En un reemplazo, `prox` muestra los valores **con los que se decidió**, es decir, antes de cargar la página nueva.
```
   18 |   7 |  R |   7*   0    1 |  F  |    2 | prox=[23,19,20] -> sale la mas lejana
   19 |   0 |  W |   7    0    1 |  H  |    - | prox=[--,24,20]
   21 |   3 |  W |   3*   0    1 |  F  |    7 | prox=[--,24,25] -> sale la mas lejana
   22 |   5 |  R |   5*   0    1 |  F  |    3 | prox=[28,24,25] -> sale la mas lejana
```
En el paso 18, la página 2 se vuelve a pedir en el paso 23, la 0 en el 19 y la 1 en el 20. Sale la 2, la más lejana.

### 3. LRU (`lru.c`): Integrante 2
Cada marco guarda el paso de su último uso (`ult`) y sale el menor. Es un **algoritmo de pila**.
```
   18 |   7 |  R |   1    0    7*|  F  |    2 | ult=[17,16,18]
   21 |   3 |  W |   1    0    3*|  F  |    7 | ult=[20,19,21]
   22 |   5 |  R |   1    5*   3 |  F  |    0 | ult=[20,22,21]
```

### 4. Reloj / Segunda Oportunidad (`reloj.c`): Integrante 2
Bit `R` y puntero `ptr`. Si R = 1, la página recibe una segunda oportunidad (R pasa a 0 y el puntero avanza). La traza muestra **cuántas segundas oportunidades** se dieron antes de encontrar la víctima.
```
   18 |   7 |  R |   0    7*   2 |  F  |    1 | R=[0,1,0] ptr=M3 (2das oport.: 3)
   19 |   0 |  W |   0    7    2 |  H  |    - | R=[1,1,0] ptr=M3
   20 |   1 |  R |   0    7    1*|  F  |    2 | R=[1,1,1] ptr=M1 (2das oport.: 0)
```
En el paso 18 los tres bits R eran 1. El puntero dio una vuelta completa poniéndolos en 0 y expulsó la página en M2. Cuando todos los R son 1, Reloj se comporta igual que FIFO.

### 5. NRU (`nru.c`): Integrante 3
- Usa los bits `R` y `M`. Al inicio de los pasos 6, 11, 16, 21 y 26, la **interrupción de reloj** pone todos los R en 0; la traza lo indica con `[reloj: R<-0]`.
- Sale una página de la clase 2·R + M más baja. Empate: la más antigua.
```
   18 |   7 |  R |   1    0    7*|  F  |    2 | R=[1,1,1] M=[0,1,0] clase=1
   21 |   3 |  W |   3*   0    7 |  F  |    1 | R=[1,0,0] M=[1,1,0] clase=0 [reloj: R<-0]
   22 |   5 |  R |   3    0    5*|  F  |    7 | R=[1,0,1] M=[1,1,0] clase=0
```
En el paso 21 el reloj acababa de limpiar los R. Las páginas 1 y 7 eran clase 0 (no usadas y limpias) y salió la 1, que llegó antes.

### 6. LFU (`lfu.c`): Integrante 3
Contador `frec` que vuelve a 1 cada vez que se carga una página. Sale la de menor contador; empate: FIFO.
```
   18 |   7 |  R |   3    0    7*|  F  |    1 | frec=[2,5,1]
   19 |   0 |  W |   3    0    7 |  H  |    - | frec=[2,6,1]
   21 |   3 |  W |   3    0    1 |  H  |    - | frec=[3,6,1]
```
La página 0, la más usada de la cadena (8 veces), acumula frecuencia alta y **nunca sale** en la segunda mitad. Por eso LFU es uno de los mejores aquí: **19 fallos y solo 4 escrituras**, porque la 0 es justamente la página sucia más escrita.

### 7. MFU (`mfu.c`): Integrante 4
Usa el mismo contador, pero sale la de **mayor** frecuencia.
```
   18 |   7 |  R |   7*   1    2 |  F  |    0 | frec=[1,2,1]
   19 |   0 |  W |   7    0*   2 |  F  |    1 | frec=[1,1,1]
   24 |   0 |  W |   0*   5    2 |  F  |    3 | frec=[1,1,1]
```
Expulsa justamente las páginas más usadas (la 0 en el paso 18) y luego casi todas quedan con frecuencia 1. Al quedar empatadas, el desempate FIFO decide, y **MFU termina igual que FIFO (25 fallos)**. Demuestra por qué MFU rara vez se usa.

### 8. Reloj Mejorado (`reloj_mejorado.c`): Integrante 4
- Usa `R`, `M` y `ptr`.
- **Pasada 1:** busca (0,0) sin tocar los bits. **Pasada 2:** busca (0,1) limpiando R. Si no encuentra víctima, se repite como pasadas 3 y 4.
- La traza indica en qué pasada se encontró la víctima.
```
   18 |   7 |  R |   0    7*   2 |  F  |    1 | R=[0,1,0] M=[1,0,1] ptr=M3 (pasada 3)
   22 |   5 |  R |   0    3    5*|  F  |    1 | R=[0,1,1] M=[1,1,0] ptr=M1 (pasada 1)
```
En el paso 18 todas tenían R = 1. Las pasadas 1 y 2 fallaron (la 2 limpió los R) y en la **pasada 3** encontró (0,0): la página 1, que estaba limpia. Así **evita expulsar las páginas sucias 0 y 2**. Tiene los mismos fallos que NRU (21), pero menos escrituras (6).

### 9. Aging (`aging.c`): Integrante 5
- Registro de 8 bits por marco. Al final de cada tic se calcula `reg = (reg >> 1) | (R << 7)`. Sale el registro de menor valor.
- La traza muestra los registros **después** del tic.
```
   18 |   7 |  R |   1    0    7*|  F  |    2 | reg=[01001000,00100000,10000000]
   20 |   1 |  R |   1    0    7 |  H  |    - | reg=[10010010,01001000,00100000]
   21 |   3 |  W |   1    0    3*|  F  |    7 | reg=[01001001,00100100,10000000]
```
En el paso 21, antes de decidir, los registros eran `[10010010, 01001000, 00100000]` (los del paso 20). El menor era el de la página 7 (`00100000`: usada por última vez hace 3 tics) y salió. Aging coincide con **LRU en los 30 pasos**, no solo en los 22 fallos: con esta cadena, la aproximación de 8 bits es exacta.

### 10. Working Set (`working_set.c`): Integrante 5
- Usa bits `R` (limpiados cada 5 tics) y `TUU`, el tiempo del último uso, que **solo se actualiza al cargar o en el barrido**.
- Con τ = 4, sale la primera página **fuera del conjunto de trabajo** (edad > 4). La traza explica el motivo de cada elección.
```
   18 |   7 |  R |   1    0    7*|  F  |    2 | R=[1,1,1] TUU=[18,18,18] t=18 todas en WS: la mas vieja
   22 |   5 |  R |   3    5*   7 |  F  |    0 | R=[1,1,0] TUU=[22,22,18] t=22 todas en WS: la mas vieja
   23 |   2 |  W |   3    5    2*|  F  |    7 | R=[1,1,1] TUU=[23,23,23] t=23 fuera del WS
   24 |   0 |  W |   0*   5    2 |  F  |    3 | R=[1,1,1] TUU=[24,24,24] t=24 todas R=1: M1
```
En el paso 23 la página 7 tenía TUU = 18, es decir, edad 5 > τ: estaba fuera del conjunto de trabajo y salió. **Da resultados distintos a LRU (20 frente a 22)**, a diferencia del boceto, donde Working Set era en realidad LRU.

### 11. WSClock (`wsclock.c`): Integrante 6
- Usa `R`, `M`, `TUU` y `ptr`. Recorre como máximo una vuelta: las páginas viejas (edad > 4) y limpias son la víctima; las viejas y sucias **programan su escritura** (`escr.prog`).
- Si la vuelta termina sin víctima, elige la primera página con R = 0 y M = 0; si no hay ninguna, la que está bajo el puntero.
```
   20 |   1 |  R |   1*   0    2 |  F  |    7 | R=[1,0,0] M=[0,1,1] TUU=[20,20,18] ptr=M2
   22 |   5 |  R |   3    5*   2 |  F  |    0 | R=[0,1,0] M=[1,0,1] TUU=[22,22,18] ptr=M3
   23 |   2 |  W |   3    5    2 |  H  |    - | R=[0,1,1] M=[1,0,1] TUU=[22,22,23] ptr=M3
```
Junto con LFU, es el **mejor algoritmo realizable** con esta cadena: **19 fallos y 4 escrituras**. Mantiene en memoria la página 2 (sucia y muy usada), lo que da un acierto en el paso 23.

### 12. Aleatorio (`aleatorio.c`): Integrante 6
LCG propio con semilla 42. La víctima es `x mod 3`. La traza muestra el número generado y el marco elegido.
```
   18 |   7 |  R |   1    0    7*|  F  |    2 | x=1314989459 -> x mod 3 = 2 (M3)
   21 |   3 |  W |   1    0    3*|  F  |    7 | x=1535244752 -> x mod 3 = 2 (M3)
   23 |   2 |  W |   2*   0    5 |  F  |    1 | x=1108520142 -> x mod 3 = 0 (M1)
```
Con esta semilla obtuvo 20 fallos, un resultado "con suerte": otra semilla puede dar un valor muy distinto. Por eso la semilla está fija y documentada, para que el resultado sea **reproducible**.

---

## 4.3 Verificación cruzada (preliminar)

Para asegurar que el código C es correcto, se escribió **una segunda implementación independiente en Python** de las mismas reglas del Paso 1. Se comparó **paso a paso** con la salida del simulador: contenido de los 3 marcos, F/H en los 30 pasos y escrituras a disco.

| Algoritmo | Fallos C | Fallos Python | Escr. C | Escr. Python | Traza de 30 pasos |
|---|---|---|---|---|---|
| FIFO | 25 | 25 | 9 | 9 | ✅ idéntica |
| Óptimo | 15 | 15 | 6 | 6 | ✅ idéntica |
| LRU | 22 | 22 | 8 | 8 | ✅ idéntica |
| Reloj | 24 | 24 | 9 | 9 | ✅ idéntica |
| NRU | 21 | 21 | 7 | 7 | ✅ idéntica |
| LFU | 19 | 19 | 4 | 4 | ✅ idéntica |
| MFU | 25 | 25 | 9 | 9 | ✅ idéntica |
| Reloj Mejorado | 21 | 21 | 6 | 6 | ✅ idéntica |
| Aging | 22 | 22 | 8 | 8 | ✅ idéntica |
| Working Set | 20 | 20 | 7 | 7 | ✅ idéntica |
| WSClock | 19 | 19 | 4 | 4 | ✅ idéntica |
| Aleatorio | 20 | 20 | 8 | 8 | ✅ idéntica |

**Resultado: las 12 implementaciones coinciden al 100 %.** La validación completa queda para el **Paso 5**: el script de verificación entra al repositorio y se prueba la anomalía de Belády en los 12 algoritmos.

## 4.4 Compilación

```
$ make
... (16 módulos)
```
✅ **0 advertencias** con `-std=c11 -Wall -Wextra -pedantic -O2` (gcc 15.2, Ubuntu 26.04 / WSL).

## 4.5 Ajuste en el Paso 1

Se precisó la regla de **Working Set** en `PASO_01_parametros.md`: al encontrar la primera página fuera del conjunto de trabajo, el barrido **continúa solo para actualizar el TUU** de las demás, como describe Tanenbaum. No cambia ningún otro parámetro.

---

**Siguiente paso:** PASO 5. Validación formal: script de verificación en el repositorio, prueba de Belády con 3 y 4 marcos para los 12 algoritmos y casos de borde (1 marco, cadena sin repeticiones, etc.).
