# -*- coding: utf-8 -*-
"""
contenido_informe.py - Texto del informe (PASO 7).
Separado del generador para poder editar la redacción sin tocar el formato.
Marcado en línea: **negrita** y *cursiva*.
"""

INTEGRANTES = [
    ("Angel Ismael Alvarez Catunta", "221945"),
    ("[Nombre y Apellidos del Integrante 2]", "[Código 2]"),
    ("[Nombre y Apellidos del Integrante 3]", "[Código 3]"),
    ("[Nombre y Apellidos del Integrante 4]", "[Código 4]"),
    ("[Nombre y Apellidos del Integrante 5]", "[Código 5]"),
    ("[Nombre y Apellidos del Integrante 6]", "[Código 6]"),
]

INTRODUCCION = {
    "evolucion": [
        "La memoria principal ha sido, desde los primeros computadores, un recurso escaso frente a las "
        "necesidades de los programas. La respuesta de los sistemas operativos fue la **memoria virtual**: "
        "una abstracción que permite ejecutar procesos cuyo espacio de direcciones lógico supera la memoria "
        "física disponible, manteniendo en RAM solo las porciones que se están utilizando y el resto en el "
        "almacenamiento secundario. Su primera implementación fue el sistema de almacenamiento de un solo "
        "nivel del computador Atlas, en la Universidad de Mánchester (Kilburn et al., 1962).",
        "La técnica que hizo práctica esta idea es la **paginación por demanda**: el espacio lógico se divide "
        "en páginas de tamaño fijo y la memoria física en marcos del mismo tamaño, y cada página se carga "
        "únicamente cuando el proceso la referencia (Silberschatz et al., 2018). Cuando una página "
        "referenciada no está en memoria ocurre un **fallo de página**, y si todos los marcos están ocupados "
        "el sistema operativo debe elegir una página **víctima** para liberar un marco. La regla que hace esa "
        "elección es el **algoritmo de reemplazo de páginas**.",
        "El estudio de estos algoritmos tiene una larga trayectoria. Belady (1966) caracterizó el algoritmo "
        "óptimo (MIN) y comparó estrategias realizables; Belady et al. (1969) descubrieron que FIFO puede "
        "producir más fallos al recibir más memoria; Denning (1968) formalizó el modelo del conjunto de "
        "trabajo y explicó la hiperpaginación; Corbató (1969) introdujo el algoritmo del reloj en Multics y "
        "Carr y Hennessy (1981) lo combinaron con el conjunto de trabajo en WSClock. En el hardware moderno, "
        "aunque las unidades NVMe redujeron la latencia del almacenamiento a decenas de microsegundos, la "
        "distancia con la RAM (cerca de 100 ns) sigue siendo de dos a tres órdenes de magnitud, por lo que "
        "los núcleos actuales continúan usando aproximaciones eficientes de LRU (Tanenbaum & Bos, 2015).",
    ],
    "problema": [
        "Cada fallo de página interrumpe al proceso, provoca una operación de entrada/salida y, si la página "
        "expulsada fue modificada, una escritura adicional a disco. El impacto se mide con el tiempo efectivo "
        "de acceso: con un acceso a memoria de 200 ns y un servicio de fallo de 8 ms, basta un fallo cada "
        "1 000 accesos para que el tiempo efectivo suba a unos 8,2 µs, es decir, la memoria se vuelve unas "
        "40 veces más lenta (Silberschatz et al., 2018).",
        "Cuando los procesos disponen de menos marcos que los que exige su localidad de referencia, el sistema "
        "entra en **hiperpaginación** (*thrashing*): dedica más tiempo a mover páginas entre disco y memoria "
        "que a ejecutar instrucciones útiles (Denning, 1968). Un algoritmo de reemplazo inadecuado agrava "
        "este fenómeno, mientras que uno bien elegido lo mitiga sin necesidad de más hardware.",
    ],
    "propuesta": [
        "El presente proyecto propone un **análisis empírico y comparativo de 12 algoritmos de reemplazo de "
        "páginas** bajo condiciones idénticas de contención de memoria: **3 marcos físicos** y una **cadena "
        "fija de 30 referencias** con un patrón definido de lecturas y escrituras. Para ello se desarrolló un "
        "simulador modular en lenguaje C para Linux que registra, paso a paso, el contenido de los marcos, "
        "los fallos, los aciertos, las variables internas de cada algoritmo y las escrituras a disco.",
        "Los resultados fueron validados con una implementación de referencia independiente y con 67 pruebas "
        "automáticas (todas superadas), y se complementan con un análisis de sensibilidad (1 a 8 marcos) y con la verificación "
        "experimental de la anomalía de Belády.",
        "Finalmente, el mismo código C se compiló a **WebAssembly** para ofrecer un **simulador web "
        "interactivo**, que permite reproducir paso a paso cada algoritmo con cualquier cadena y número de marcos.",
    ],
}

CAP1 = {
    "descripcion": [
        "El cuello de botella de la memoria virtual es el fallo de página. Mientras la CPU accede a la RAM en "
        "nanosegundos, el almacenamiento secundario responde en micro o milisegundos; por ello, la eficiencia "
        "de todo el sistema depende de cuántas veces se recurre al disco. El algoritmo de reemplazo decide qué "
        "página abandona la memoria y, en consecuencia, cuántos fallos futuros se producirán.",
        "El problema tiene un componente de **compromiso**: el algoritmo óptimo (OPT) minimiza los fallos, "
        "pero requiere conocer el futuro y no puede implementarse; LRU se acerca a él, pero su implementación "
        "exacta exige actualizar una marca de tiempo en cada acceso a memoria, lo que resulta costoso en "
        "hardware. Entre ambos extremos existe una familia de aproximaciones (Reloj, NRU, Aging, WSClock, "
        "entre otras) que equilibran la **complejidad algorítmica** con la **tasa de aciertos** (*hit ratio*) "
        "y con el costo de escritura de las páginas modificadas (Tanenbaum & Bos, 2015).",
        "Elegir entre estas alternativas sin datos comparables conduce a decisiones basadas en intuición. Se "
        "requiere, por tanto, un estudio que evalúe los algoritmos bajo las mismas condiciones y con métricas "
        "reproducibles.",
    ],
    "identificacion": [
        "**Disparidad de velocidad memoria–disco:** cada fallo cuesta miles de veces más que un acierto.",
        "**Memoria física limitada:** la cantidad de marcos es menor que el número de páginas del proceso.",
        "**Desconocimiento del futuro:** el algoritmo óptimo no es realizable; los algoritmos reales deben "
        "predecir el uso futuro a partir del pasado.",
        "**Costo de las aproximaciones:** LRU exacto es caro; las aproximaciones con bits R y M sacrifican "
        "precisión a cambio de eficiencia.",
        "**Páginas modificadas:** expulsar una página sucia agrega una escritura a disco.",
        "**Anomalía de Belády:** en algunos algoritmos, agregar marcos puede aumentar los fallos.",
        "**Hiperpaginación:** con pocos marcos, el sistema puede pasar más tiempo paginando que ejecutando.",
    ],
    "justificacion": [
        "**Justificación teórica.** El proyecto integra los conceptos centrales de la gestión de memoria "
        "(paginación por demanda, localidad de referencia, conjunto de trabajo, algoritmos de pila y anomalía "
        "de Belády) y los contrasta con datos medidos, en lugar de limitarse a su descripción.",
        "**Justificación técnica.** El simulador en C reproduce las estructuras que emplea un núcleo real "
        "(bits de referencia y modificación, punteros circulares, registros de desplazamiento) y produce "
        "trazas verificables. Su diseño modular permite agregar algoritmos y parámetros sin rehacer el código.",
        "**Justificación práctica.** En la formación del Ingeniero Informático y de Sistemas, comprender cómo "
        "el núcleo administra la memoria es la base para optimizar servidores, bases de datos, sistemas "
        "embebidos y máquinas virtuales, donde las políticas de reemplazo (de páginas, de caché o de búferes) "
        "determinan el rendimiento.",
    ],
    "limitaciones": [
        "La simulación se ejecuta en **espacio de usuario**; no modifica el núcleo de Linux ni mide tiempos "
        "reales de acceso a disco.",
        "Se usa una **única cadena estática de 30 referencias**; los resultados son válidos para esa cadena y "
        "no deben generalizarse a cualquier carga de trabajo.",
        "Se modela **un solo proceso con asignación fija** de marcos; no hay competencia entre procesos ni "
        "asignación global.",
        "No se modela **contención multinúcleo** ni concurrencia en tiempo real; el tiempo es virtual "
        "(1 referencia = 1 tic).",
        "El **patrón de escrituras** fue definido por el equipo para representar páginas de código y de datos; "
        "no proviene de la traza de un programa real.",
        "El resultado del algoritmo **Aleatorio** depende de la semilla (42); con otra semilla puede variar.",
        "La búsqueda de la anomalía de Belády en cadenas aleatorias es **limitada** (600 cadenas): no "
        "observarla no demuestra que un algoritmo sea inmune.",
    ],
    "delimitaciones": [
        "**Conceptual:** reemplazo local de páginas en paginación por demanda; 12 algoritmos: FIFO, Óptimo, "
        "LRU, Reloj, NRU, LFU, MFU, Reloj Mejorado, Aging, Working Set, WSClock y Aleatorio.",
        "**Temporal:** Semestre académico 2026-II.",
        "**Hardware simulado:** 3 marcos de página físicos (con un análisis complementario de 1 a 8 marcos); "
        "el tamaño de página no interviene porque se simulan números de página.",
        "**Plataforma:** Linux Ubuntu 26.04 LTS sobre WSL 2, compilador gcc 15.2 con C estándar ISO C11 "
        "(`-std=c11 -Wall -Wextra -pedantic -O2`), GNU Make y Python 3 para validación y gráficas.",
        "**Espacial:** Escuela Profesional de Ingeniería Informática y de Sistemas, UNSAAC, Cusco.",
    ],
    "metodologia": [
        "**Enfoque:** cuantitativo. **Tipo:** aplicado. **Diseño:** experimental por simulación, en el que se "
        "controlan todas las condiciones excepto la política de reemplazo.",
        "**Variable independiente:** el algoritmo de reemplazo (12 niveles). En el análisis de sensibilidad, "
        "también el número de marcos (1 a 8). **Variables dependientes:** fallos de página, aciertos, tasa de "
        "fallos y escrituras a disco. **Variables controladas:** cadena de referencias, patrón de lecturas y "
        "escrituras, número de marcos, estado inicial y parámetros de cada algoritmo.",
        "**Procedimiento:** (1) fijar los parámetros del experimento; (2) preparar el entorno Linux; "
        "(3) construir una estructura modular común; (4) implementar los 12 algoritmos; (5) validar; "
        "(6) generar trazas, métricas y gráficas; (7) analizar y redactar.",
        "**Recolección de datos:** el propio simulador registra cada paso y exporta los resultados a archivos "
        "de texto y CSV, lo que evita la transcripción manual.",
        "**Validación:** (a) valores de control calculados de forma independiente (FIFO = 25, OPT = 15, "
        "LRU = 22, Reloj = 24 fallos); (b) reproducción del ejemplo de Belády del material del curso; "
        "(c) comparación paso a paso contra una implementación de referencia escrita por separado en Python; "
        "(d) invariantes, casos de borde y 400 casos aleatorios. Resultado: 67 de 67 pruebas superadas, incluidas las del simulador web.",
        "**Control de versiones:** todo el trabajo se registró en un repositorio Git con una etiqueta por "
        "cada fase (`paso-01`, `paso-02`, etc.).",
    ],
}

# (ID, Fase, Tarea, Duración en días, Recursos, Predecesoras, Semana)
CRONOGRAMA = [
    ("1", "Planificación", "Definir alcance, cadena de referencias y parámetros", 2, "Integrantes 1–6", "—", "1"),
    ("2", "Planificación", "Reparto de algoritmos y creación del repositorio", 1, "Integrante 1", "1", "1"),
    ("3", "Marco teórico", "Revisión bibliográfica de memoria virtual", 4, "Integrantes 2 y 3", "2", "1–2"),
    ("4", "Marco teórico", "Búsqueda y síntesis de antecedentes", 3, "Integrantes 4 y 5", "3", "2"),
    ("5", "Implementación en C", "Entorno Linux y estructura modular común", 2, "Integrante 1", "2", "1"),
    ("6", "Implementación en C", "FIFO y Óptimo", 4, "Integrante 1", "5", "2"),
    ("7", "Implementación en C", "LRU y Reloj", 4, "Integrante 2", "5", "2"),
    ("8", "Implementación en C", "NRU y LFU", 4, "Integrante 3", "5", "2"),
    ("9", "Implementación en C", "MFU y Reloj Mejorado", 4, "Integrante 4", "5", "2"),
    ("10", "Implementación en C", "Aging y Working Set", 4, "Integrante 5", "5", "2"),
    ("11", "Implementación en C", "WSClock y Aleatorio", 4, "Integrante 6", "5", "2"),
    ("12", "Simulación y pruebas", "Validación formal (referencia, invariantes, casos de borde)", 3, "Integrantes 1 y 5", "6–11", "3"),
    ("13", "Simulación y pruebas", "Generación de trazas, CSV y gráficas", 2, "Integrante 6", "12", "3"),
    ("14", "Redacción y validación", "Redacción de Introducción y Capítulo I", 3, "Integrantes 2 y 3", "4", "3"),
    ("15", "Redacción y validación", "Redacción del Capítulo II (cada integrante, sus 2 algoritmos)", 5, "Integrantes 1–6", "13", "4"),
    ("16", "Redacción y validación", "Revisión integral, bibliografía APA 7 y entrega", 2, "Integrantes 1–6", "14, 15", "4"),
]

ANT_INTERNACIONALES = [
    ("Belady, L. A. (1966). *A study of replacement algorithms for a virtual-storage computer*. IBM Systems Journal.",
     "Estudió el comportamiento de distintos algoritmos de reemplazo sobre trazas de programas reales en un "
     "computador con almacenamiento virtual de IBM. Definió el algoritmo **MIN** (óptimo), que expulsa la "
     "página cuya próxima referencia está más lejos, y lo usó como cota inferior para comparar estrategias "
     "realizables como la aleatoria y FIFO. Concluyó que la información sobre el uso reciente mejora "
     "significativamente las decisiones de reemplazo.",
     "Proporciona el algoritmo Óptimo que este proyecto utiliza como referencia (15 fallos) y el método de "
     "evaluación por simulación de trazas."),
    ("Denning, P. J. (1968). *The working set model for program behavior*. Communications of the ACM.",
     "Propuso el modelo del **conjunto de trabajo** W(t, τ): el conjunto de páginas referenciadas en la "
     "ventana de las últimas τ referencias. Demostró que un proceso solo progresa eficientemente si su "
     "conjunto de trabajo cabe en memoria y explicó la **hiperpaginación** como consecuencia de asignar "
     "menos marcos que los que exige la localidad del programa.",
     "Sustenta los algoritmos Working Set y WSClock implementados (τ = 4) y la interpretación de la curva de "
     "fallos frente al número de marcos."),
    ("Carr, R. W., & Hennessy, J. L. (1981). *WSCLOCK—A simple and effective algorithm for virtual memory management*. ACM SOSP.",
     "Propusieron **WSClock**, que combina la estructura circular del algoritmo del reloj con el criterio del "
     "conjunto de trabajo y con la escritura anticipada de páginas modificadas. Mediante simulación "
     "mostraron que alcanza un rendimiento comparable al de políticas más costosas con una implementación "
     "sencilla.",
     "WSClock fue, junto con LFU, el algoritmo realizable con menos fallos (19) y menos escrituras (4) en "
     "este proyecto, lo que concuerda con lo reportado por los autores."),
    ("Megiddo, N., & Modha, D. S. (2003). *ARC: A self-tuning, low overhead replacement cache*. USENIX FAST.",
     "Presentaron **ARC**, una política que mantiene dos listas, una para páginas usadas una vez "
     "(recencia) y otra para páginas usadas varias veces (frecuencia), y ajusta dinámicamente el espacio de "
     "cada una. En trazas reales superó a LRU con un costo de implementación bajo.",
     "Muestra que la combinación de **recencia y frecuencia** es una línea actual de investigación; en este "
     "proyecto, LFU (frecuencia) y LRU (recencia) obtuvieron 19 y 22 fallos, respectivamente."),
]

ANT_NACIONALES = [
    ("Ruiz L., E., & Raffo L., E. (2003). *Simulación de la memoria cache*. Industrial Data, 6(2), 48–55. "
     "Universidad Nacional Mayor de San Marcos, Lima.",
     "Desarrollaron un programa en C++ que simula una memoria caché modelada como una **cola FIFO**, con "
     "accesos generados mediante una distribución uniforme, para estimar el **porcentaje de aciertos** y el "
     "**tiempo medio de acceso**. Concluyeron que, para un tamaño dado de memoria principal, existe un "
     "**tamaño óptimo de caché** por encima del cual el porcentaje de aciertos ya no mejora, por lo que no "
     "conviene aumentarla indefinidamente.",
     "Comparte el enfoque de simulación en lenguaje C/C++, el uso de FIFO como política de reemplazo y las "
     "métricas de aciertos. Su conclusión es análoga a la observada en la curva de fallos de este proyecto: "
     "a partir de 7 marcos, agregar memoria ya no reduce los fallos."),
]

CONCLUSIONES = [
    "Se implementaron en lenguaje C, para Linux, los 12 algoritmos de reemplazo de páginas planteados, en un "
    "simulador modular que compila sin advertencias con `gcc -std=c11 -Wall -Wextra -pedantic -O2` y que "
    "muestra la traza completa de cada algoritmo con sus variables auxiliares.",
    "Con la cadena de 30 referencias y 3 marcos, el algoritmo **Óptimo** obtuvo 15 fallos (50 %), el mínimo "
    "posible. Entre los algoritmos realizables, **LFU y WSClock** obtuvieron el mejor resultado (19 fallos, "
    "63,33 %) y además el menor número de escrituras a disco (4); **FIFO y MFU** obtuvieron el peor (25 "
    "fallos, 83,33 %).",
    "Contar solo los fallos oculta el costo de las escrituras: **Reloj Mejorado** y **NRU** empataron en 21 "
    "fallos, pero Reloj Mejorado realizó una escritura menos al preferir víctimas limpias.",
    "**Aging** reprodujo exactamente la traza de **LRU** en los 30 pasos, lo que confirma que un registro de "
    "8 bits es una aproximación eficaz de LRU para esta cadena.",
    "Se verificó experimentalmente la **anomalía de Belády**: con la cadena del material del curso, FIFO, "
    "Reloj, MFU, Reloj Mejorado y WSClock pasan de 9 a 10 fallos al aumentar de 3 a 4 marcos, mientras que "
    "**LRU y Óptimo**, por ser algoritmos de pila, nunca la presentaron.",
    "El orden de los algoritmos **depende del número de marcos**: con 4 marcos, NRU (13 fallos) queda a un "
    "fallo del Óptimo y supera a LRU (17). No existe un algoritmo mejor en todas las condiciones.",
    "La validación con una implementación de referencia independiente, invariantes, casos de borde y 400 "
    "casos aleatorios (67 de 67 pruebas superadas) respalda la exactitud de los resultados.",
]

RECOMENDACIONES = [
    "Repetir el experimento con cadenas obtenidas de programas reales (por ejemplo, con herramientas de "
    "trazado en Linux) para evaluar los algoritmos con cargas de trabajo representativas.",
    "Ampliar el estudio a políticas modernas que combinan recencia y frecuencia, como ARC o LRU-K.",
    "Modelar varios procesos con asignación global de marcos para estudiar la hiperpaginación de forma "
    "directa.",
    "Ejecutar `make validar` antes de cualquier modificación del simulador para preservar su exactitud.",
]

BIBLIOGRAFIA = [
    "Belady, L. A. (1966). A study of replacement algorithms for a virtual-storage computer. *IBM Systems Journal, 5*(2), 78–101. https://doi.org/10.1147/sj.52.0078",
    "Belady, L. A., Nelson, R. A., & Shedler, G. S. (1969). An anomaly in space-time characteristics of certain programs running in a paging machine. *Communications of the ACM, 12*(6), 349–353. https://doi.org/10.1145/363011.363155",
    "Carr, R. W., & Hennessy, J. L. (1981). WSCLOCK—A simple and effective algorithm for virtual memory management. En *Proceedings of the Eighth ACM Symposium on Operating Systems Principles* (pp. 87–95). ACM. https://doi.org/10.1145/800216.806596",
    "Corbató, F. J. (1969). A paging experiment with the Multics system. En H. Feshbach & K. U. Ingard (Eds.), *In honor of Philip M. Morse* (pp. 217–228). MIT Press.",
    "Denning, P. J. (1968). The working set model for program behavior. *Communications of the ACM, 11*(5), 323–333. https://doi.org/10.1145/363095.363141",
    "Denning, P. J. (1970). Virtual memory. *ACM Computing Surveys, 2*(3), 153–189. https://doi.org/10.1145/356571.356573",
    "Kilburn, T., Edwards, D. B. G., Lanigan, M. J., & Sumner, F. H. (1962). One-level storage system. *IRE Transactions on Electronic Computers, EC-11*(2), 223–235. https://doi.org/10.1109/TEC.1962.5219356",
    "Mattson, R. L., Gecsei, J., Slutz, D. R., & Traiger, I. L. (1970). Evaluation techniques for storage hierarchies. *IBM Systems Journal, 9*(2), 78–117. https://doi.org/10.1147/sj.92.0078",
    "Megiddo, N., & Modha, D. S. (2003). ARC: A self-tuning, low overhead replacement cache. En *Proceedings of the 2nd USENIX Conference on File and Storage Technologies* (pp. 115–130). USENIX Association.",
    "Ruiz L., E., & Raffo L., E. (2003). Simulación de la memoria cache. *Industrial Data, 6*(2), 48–55. https://www.redalyc.org/articulo.oa?id=81660207",
    "Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating system concepts* (10th ed.). Wiley.",
    "Stallings, W. (2018). *Operating systems: Internals and design principles* (9th ed.). Pearson.",
    "Tanenbaum, A. S., & Bos, H. (2015). *Modern operating systems* (4th ed.). Pearson.",
]

FUNDAMENTOS = [
    ("Paginación por demanda y fallo de página",
     ["La memoria lógica de un proceso se divide en **páginas** y la física en **marcos** del mismo tamaño. "
      "La tabla de páginas indica en qué marco está cada página y, mediante el bit de validez, si está en "
      "memoria. Al referenciar una página no válida se produce un **fallo de página**: el sistema operativo "
      "localiza la página en disco, la carga en un marco libre (o en el de una víctima), actualiza la tabla y "
      "reinicia la instrucción (Silberschatz et al., 2018).",
      "El **tiempo efectivo de acceso** es EAT = (1 − p) × t_memoria + p × t_fallo, donde p es la tasa de "
      "fallos. Como t_fallo es miles de veces mayor que t_memoria, reducir p es el objetivo de todo algoritmo "
      "de reemplazo."]),
    ("Localidad de referencia y bits R y M",
     ["Los programas presentan **localidad temporal** (lo usado recientemente se volverá a usar) y "
      "**localidad espacial** (se usan direcciones cercanas). Los algoritmos realizables explotan la localidad "
      "temporal para predecir el futuro a partir del pasado (Denning, 1970).",
      "El hardware mantiene por página un **bit de referencia R**, que se activa en cada acceso, y un **bit de "
      "modificación M**, que se activa en cada escritura. Una página con M = 1 (sucia) debe escribirse en "
      "disco antes de reutilizar su marco, lo que duplica el costo de E/S de ese reemplazo."]),
    ("Algoritmos de pila y anomalía de Belády",
     ["Un algoritmo es **de pila** si el conjunto de páginas en memoria con m marcos está siempre contenido "
      "en el conjunto con m + 1 marcos; en ese caso, más marcos nunca producen más fallos (Mattson et al., "
      "1970). LRU y el Óptimo son algoritmos de pila; FIFO no lo es, y por ello puede presentar la "
      "**anomalía de Belády**: más fallos con más memoria (Belady et al., 1969)."]),
    ("Conjunto de trabajo e hiperpaginación",
     ["El **conjunto de trabajo** W(t, τ) contiene las páginas referenciadas en las últimas τ referencias. Si "
      "los marcos asignados son menos que |W|, el proceso falla continuamente y el sistema entra en "
      "**hiperpaginación** (Denning, 1968)."]),
    ("Condiciones del experimento",
     ["Todos los algoritmos se evaluaron con **3 marcos** inicialmente vacíos (las primeras cargas cuentan "
      "como fallo) y con la cadena oficial de 30 referencias, que contiene 7 páginas distintas (mínimo 7 "
      "fallos obligatorios). Cada referencia es una lectura (R) o una escritura (W) según el patrón de la "
      "Tabla 2. Si hay un marco libre se usa el de menor índice; los empates se resuelven como indica cada "
      "algoritmo o, en su defecto, a favor del marco de menor índice.",
      "En las trazas, las columnas M1, M2 y M3 muestran el contenido de los marcos **después** de cada "
      "referencia; la página cargada en ese paso aparece en **negrita**; F indica fallo y H acierto; "
      "*Víctima* es la página expulsada, y la última columna muestra las variables internas del algoritmo."]),
]

# Por algoritmo: (id, archivo, nombre largo, integrante, teoría[], ventajas[], desventajas[],
#                 complejidad, belady, análisis de la traza[], citas)
ALGORITMOS = [
    (1, "fifo", "FIFO (First-In, First-Out)", 1,
     ["FIFO expulsa la página que lleva **más tiempo en memoria**, como una cola de llegada. No considera si "
      "la página se usa con frecuencia o no; un acierto no modifica el orden de la cola. Se implementa con un "
      "puntero circular al marco más antiguo (Silberschatz et al., 2018)."],
     ["Muy simple de implementar y de bajo costo.", "No requiere apoyo especial del hardware."],
     ["Ignora el uso de las páginas: puede expulsar una página muy utilizada.",
      "Presenta la anomalía de Belády."],
     "O(1) por reemplazo con puntero circular (O(m) para buscar la página); espacio O(m).",
     "**Sí.** Con la cadena 1,2,3,4,1,2,5,1,2,3,4,5 produce 9 fallos con 3 marcos y 10 con 4.",
     ["FIFO obtiene 25 fallos. Es especialmente desfavorable en el paso 6, donde expulsa la página 0 justo "
      "antes de que se vuelva a necesitar en el paso 7. La columna auxiliar muestra la cola, de la página más "
      "antigua a la más reciente."],
     "Silberschatz et al. (2018); Belady et al. (1969)."),
    (2, "optimo", "Óptimo (OPT / MIN de Belády)", 1,
     ["El algoritmo óptimo expulsa la página cuya **próxima referencia está más lejos en el futuro**, o que no "
      "se volverá a usar. Produce el menor número de fallos posible para cualquier cadena y número de marcos "
      "(Belady, 1966). Como exige conocer la cadena completa por adelantado, no puede implementarse en un "
      "sistema operativo real; se usa como **cota inferior** para evaluar los demás algoritmos."],
     ["Mínimo número de fallos posible.", "Es un algoritmo de pila: no presenta la anomalía de Belády."],
     ["No es realizable: requiere conocer el futuro.", "Costoso de calcular: debe recorrer la cadena futura."],
     "O(m·n) por reemplazo con búsqueda directa en la cadena futura; espacio O(n).",
     "**No** (algoritmo de pila). Con la cadena de Belády: 7 fallos con 3 marcos y 6 con 4.",
     ["Obtiene 15 fallos (50 %). La columna *prox* indica el paso en que se volverá a referenciar la página "
      "de cada marco (“--” significa nunca); en un reemplazo se muestran los valores con que se decidió. Por "
      "ejemplo, en el paso 18 se expulsa la página 2, que no se vuelve a usar hasta el paso 23."],
     "Belady (1966); Mattson et al. (1970)."),
    (3, "lru", "LRU (Least Recently Used)", 2,
     ["LRU expulsa la página que lleva **más tiempo sin usarse**, bajo el supuesto de localidad temporal: el "
      "pasado reciente predice el futuro cercano. Se implementó con una marca de tiempo del último uso por "
      "marco; la víctima es la marca menor (Silberschatz et al., 2018)."],
     ["Buena aproximación del Óptimo en programas con localidad.", "Es un algoritmo de pila."],
     ["Su implementación exacta exige actualizar una marca en cada acceso a memoria, lo que es costoso en "
      "hardware.", "Falla siempre ante recorridos cíclicos mayores que la memoria."],
     "O(m) por referencia con marcas de tiempo (O(1) con lista doblemente enlazada y tabla hash); espacio O(m).",
     "**No** (algoritmo de pila). Con la cadena de Belády: 10 fallos con 3 marcos y 8 con 4.",
     ["Obtiene 22 fallos. La columna *ult* muestra el paso del último uso de la página de cada marco; la "
      "víctima es siempre la de menor valor."],
     "Silberschatz et al. (2018); Mattson et al. (1970)."),
    (4, "reloj", "Reloj o Segunda Oportunidad (Clock)", 2,
     ["Es una variante de FIFO con un **bit de referencia R** y un puntero circular. Si la página bajo el "
      "puntero tiene R = 1, se le da una segunda oportunidad (R = 0) y el puntero avanza; si tiene R = 0, se "
      "expulsa. Fue introducido en el sistema Multics (Corbató, 1969)."],
     ["Aproxima LRU con un solo bit por página.", "Implementación eficiente, usada en sistemas reales."],
     ["Si todas las páginas tienen R = 1, degenera en FIFO.", "Puede presentar la anomalía de Belády."],
     "O(1) amortizado y O(m) en el peor caso (una vuelta completa); espacio: 1 bit por marco.",
     "**Sí.** Con la cadena de Belády: 9 fallos con 3 marcos y 10 con 4.",
     ["Obtiene 24 fallos, cerca de FIFO. En varios pasos todas las páginas tienen R = 1 (por ejemplo, el paso "
      "18) y el puntero da una vuelta completa antes de elegir la víctima: en esos casos se comporta como FIFO."],
     "Corbató (1969); Tanenbaum y Bos (2015)."),
    (5, "nru", "NRU (Not Recently Used)", 3,
     ["NRU clasifica las páginas según sus bits (R, M) en cuatro clases: 0 = (0,0), 1 = (0,1), 2 = (1,0) y "
      "3 = (1,1), y expulsa una página de la clase más baja. Una interrupción de reloj periódica pone los bits "
      "R en 0, de modo que R indica uso **reciente** (Tanenbaum & Bos, 2015). En este proyecto el periodo es "
      "de 5 tics y los empates se resuelven por antigüedad (FIFO)."],
     ["Simple y de bajo costo.", "Considera el costo de escritura (prefiere páginas limpias)."],
     ["Solo distingue cuatro clases: decisión de grano grueso.", "Depende del periodo de la interrupción de reloj."],
     "O(m) por reemplazo (revisión de toda la tabla); espacio: 2 bits por marco.",
     "Posible, pues no es un algoritmo de pila; no se observó en las pruebas realizadas.",
     ["Obtiene 21 fallos y 7 escrituras. La marca [reloj: R<-0] indica los pasos (6, 11, 16, 21 y 26) en que "
      "la interrupción limpia los bits R. En el paso 21, las páginas 1 y 7 eran de clase 0 y se expulsó la 1, "
      "que había llegado antes."],
     "Tanenbaum y Bos (2015)."),
    (6, "lfu", "LFU (Least Frequently Used)", 3,
     ["LFU mantiene un **contador de usos** por página y expulsa la de menor contador. El contador se "
      "reinicia en 1 al cargar la página; los empates se resuelven por antigüedad (Silberschatz et al., 2018)."],
     ["Protege las páginas usadas con mucha frecuencia.", "Simple de implementar."],
     ["Una página muy usada en el pasado puede quedar en memoria aunque ya no se necesite.",
      "No es algoritmo de pila."],
     "O(m) por reemplazo (O(log m) con un montículo); espacio: un contador por marco.",
     "**Sí, posible:** en la búsqueda aleatoria se encontró al menos un caso (9 → 11 fallos al pasar de 3 a 4 marcos).",
     ["Obtiene 19 fallos y solo 4 escrituras, el mejor resultado realizable junto con WSClock. La página 0, la "
      "más referenciada (8 veces) y la más escrita, acumula un contador alto y no es expulsada en ninguno "
      "de los pasos 15 a 30."],
     "Silberschatz et al. (2018)."),
    (7, "mfu", "MFU (Most Frequently Used)", 4,
     ["MFU expulsa la página con **mayor** contador de usos, bajo el argumento de que una página con contador "
      "bajo acaba de llegar y aún se usará (Silberschatz et al., 2018). Usa el mismo contador que LFU y "
      "desempate FIFO."],
     ["Simple de implementar.", "Útil solo en patrones donde lo más usado ya no se necesita."],
     ["Expulsa justamente las páginas más útiles en programas con localidad.", "Puede presentar la anomalía de Belády."],
     "O(m) por reemplazo; espacio: un contador por marco.",
     "**Sí.** Con la cadena de Belády: 9 fallos con 3 marcos y 10 con 4.",
     ["Obtiene 25 fallos, igual que FIFO. Tras expulsar las páginas más usadas, casi todas quedan con "
      "contador 1 y el desempate FIFO decide; por eso su comportamiento coincide con el de FIFO."],
     "Silberschatz et al. (2018)."),
    (8, "reloj_mejorado", "Reloj Mejorado (Enhanced Second Chance)", 4,
     ["Extiende el Reloj con el par (R, M). El puntero busca primero una página (0,0) sin modificar los bits; "
      "si no la encuentra, busca una (0,1) poniendo R = 0 en cada marco que recorre, y repite hasta encontrar "
      "víctima. Así prefiere páginas no usadas **y limpias**, que no requieren escritura (Silberschatz et al., 2018)."],
     ["Reduce las escrituras a disco.", "Mantiene el bajo costo del Reloj."],
     ["Puede requerir hasta cuatro pasadas del puntero.", "Puede presentar la anomalía de Belády."],
     "O(m) por reemplazo (hasta 4 vueltas); espacio: 2 bits por marco.",
     "**Sí.** Con la cadena de Belády: 9 fallos con 3 marcos y 10 con 4.",
     ["Obtiene 21 fallos, como NRU, pero solo 6 escrituras (frente a 7). En el paso 18 las pasadas 1 y 2 no "
      "encuentran víctima y en la pasada 3 expulsa la página 1, limpia, protegiendo a las páginas sucias 0 y 2."],
     "Silberschatz et al. (2018)."),
    (9, "aging", "Envejecimiento (Aging)", 5,
     ["Aproxima LRU en software. Cada marco tiene un registro de 8 bits; al final de cada tic el registro se "
      "desplaza una posición a la derecha y el bit R entra por la izquierda. El registro de menor valor "
      "corresponde a la página usada hace más tiempo y es la víctima (Tanenbaum & Bos, 2015)."],
     ["Muy buena aproximación de LRU con pocos bits.", "Bajo costo de hardware (solo el bit R)."],
     ["Tiene memoria limitada: solo recuerda los últimos 8 tics.", "Requiere desplazar todos los registros en cada tic."],
     "O(m) por tic (desplazamiento) y O(m) por reemplazo; espacio: 8 bits por marco.",
     "Posible, pues no es un algoritmo de pila; no se observó en las pruebas realizadas.",
     ["Obtiene 22 fallos y reproduce **exactamente la traza de LRU** en los 30 pasos. La columna *reg* "
      "muestra los registros en binario después de cada tic."],
     "Tanenbaum y Bos (2015)."),
    (10, "working_set", "Conjunto de Trabajo (Working Set)", 5,
     ["Basado en el modelo de Denning (1968): una página que no se ha usado en las últimas τ referencias está "
      "**fuera del conjunto de trabajo** y es buena candidata a salir. Se implementó la versión de Tanenbaum y "
      "Bos (2015): cada marco guarda R y el tiempo del último uso (TUU), los bits R se limpian cada 5 tics y, "
      "en un fallo, se recorre la tabla expulsando la primera página con R = 0 y edad mayor que τ = 4."],
     ["Relaciona el reemplazo con la localidad real del programa.", "Base teórica para evitar la hiperpaginación."],
     ["Más costoso: requiere recorrer la tabla y mantener tiempos.", "Depende de la elección de τ."],
     "O(m) por reemplazo; espacio: R y un tiempo por marco.",
     "**Sí, posible** con asignación fija de marcos: en la búsqueda aleatoria se encontraron casos (por ejemplo, 9 → 10 fallos al pasar de 4 a 5 marcos).",
     ["Obtiene 20 fallos, distinto de LRU (22). En el paso 23 la página 7 tenía TUU = 18 (edad 5 > τ) y salió "
      "por estar fuera del conjunto de trabajo."],
     "Denning (1968); Tanenbaum y Bos (2015)."),
    (11, "wsclock", "WSClock (Working Set Clock)", 6,
     ["Combina el Reloj con el conjunto de trabajo. El puntero recorre los marcos: si R = 1, lo pone en 0; si "
      "R = 0 y la página es más vieja que τ, la expulsa si está limpia o **programa su escritura** si está "
      "sucia, y continúa buscando una víctima limpia (Carr & Hennessy, 1981)."],
     ["Eficiente y con buen rendimiento; base de implementaciones reales.", "Evita esperar escrituras de páginas sucias."],
     ["Más complejo que el Reloj simple.", "Depende de τ."],
     "O(m) por reemplazo (una vuelta del puntero); espacio: R, M y un tiempo por marco.",
     "**Sí.** Con la cadena de Belády: 9 fallos con 3 marcos y 10 con 4.",
     ["Obtiene 19 fallos y 4 escrituras, el mejor resultado realizable junto con LFU. Conserva en memoria la "
      "página 2, sucia y muy usada, lo que produce un acierto en el paso 23."],
     "Carr y Hennessy (1981); Tanenbaum y Bos (2015)."),
    (12, "aleatorio", "Reemplazo Aleatorio (Random)", 6,
     ["Elige la víctima al azar entre los marcos ocupados. Sirve como referencia de un algoritmo sin "
      "información de uso (Belady, 1966). Para que el resultado sea reproducible se usa un generador "
      "congruencial lineal propio, x = (1103515245·x + 12345) mod 2³¹, con semilla 42."],
     ["Costo mínimo, sin estructuras auxiliares.", "No tiene casos patológicos sistemáticos."],
     ["Resultados variables según la semilla.", "Puede expulsar páginas muy utilizadas."],
     "O(1) por reemplazo; espacio: el estado del generador.",
     "**Sí, posible:** fue el algoritmo con más anomalías en la búsqueda aleatoria (91 casos).",
     ["Obtiene 20 fallos con la semilla 42. La columna auxiliar muestra el número generado y el marco elegido "
      "(x mod 3). Con otra semilla el resultado cambia, por lo que no debe interpretarse como un rendimiento "
      "estable."],
     "Belady (1966)."),
]
