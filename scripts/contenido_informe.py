# -*- coding: utf-8 -*-
"""
contenido_informe.py - Texto del informe (PASO 8, versión breve centrada en el código).
Separado del generador para poder editar la redacción sin tocar el formato.
Marcado en línea: **negrita**, *cursiva* y `código`.
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
        "La **memoria virtual** permite ejecutar procesos más grandes que la memoria física manteniendo en RAM "
        "solo las páginas en uso; apareció con el computador Atlas (Kilburn et al., 1962) y hoy se implementa "
        "mediante **paginación por demanda** (Silberschatz et al., 2018). Cuando una página referenciada no está "
        "en memoria ocurre un **fallo de página** y, si no hay marcos libres, un **algoritmo de reemplazo** elige "
        "la página víctima. Desde el algoritmo óptimo de Belady (1966) hasta WSClock (Carr & Hennessy, 1981), "
        "estos algoritmos buscan reducir los accesos al disco.",
    ],
    "problema": [
        "Cada fallo de página requiere una operación de E/S miles de veces más lenta que un acceso a RAM: un "
        "fallo cada 1 000 accesos basta para que la memoria parezca unas 40 veces más lenta (Silberschatz et al., "
        "2018). Un mal algoritmo de reemplazo aumenta los fallos y puede llevar a la **hiperpaginación** "
        "(Denning, 1968).",
    ],
    "propuesta": [
        "Se implementan en **lenguaje C para Linux** 12 algoritmos de reemplazo y se comparan bajo las mismas "
        "condiciones: **3 marcos** y una **cadena fija de 30 referencias** con un patrón de lecturas y "
        "escrituras. El simulador muestra la traza paso a paso y cuenta fallos, aciertos y escrituras a disco.",
    ],
}

CAP1 = {
    "descripcion": [
        "El rendimiento de la memoria virtual depende de cuántos fallos de página se producen. El algoritmo "
        "óptimo los minimiza, pero necesita conocer el futuro; LRU se le acerca, pero es costoso de implementar "
        "en hardware. Las aproximaciones (Reloj, NRU, Aging, WSClock) equilibran complejidad y tasa de aciertos "
        "(Tanenbaum & Bos, 2015), y para elegir entre ellas se necesitan datos comparables.",
    ],
    "identificacion": [
        "**Disparidad memoria–disco:** un fallo cuesta miles de veces más que un acierto.",
        "**Pocos marcos** frente al número de páginas del proceso.",
        "**El futuro es desconocido:** el algoritmo óptimo no es realizable.",
        "**Páginas modificadas:** expulsarlas obliga a escribirlas en disco.",
        "**Anomalía de Belády:** en algunos algoritmos, más marcos producen más fallos (Belady et al., 1969).",
    ],
    "justificacion": [
        "El proyecto lleva a la práctica los conceptos de gestión de memoria del curso mediante código C real y "
        "medible, una competencia necesaria para optimizar sistemas donde la política de reemplazo determina el "
        "rendimiento (núcleos, bases de datos, cachés).",
    ],
    "limitaciones": [
        "Simulación en espacio de usuario: no se modifica el núcleo ni se miden tiempos reales de disco.",
        "Una única cadena de 30 referencias: los resultados no se generalizan a cualquier carga.",
        "Un solo proceso con 3 marcos fijos y tiempo virtual (1 referencia = 1 tic).",
        "El resultado del algoritmo Aleatorio depende de la semilla (42).",
    ],
    "delimitaciones": [
        "**Conceptual:** 12 algoritmos de reemplazo local de páginas.",
        "**Temporal:** Semestre 2026-II.",
        "**Hardware simulado:** 3 marcos de página.",
        "**Plataforma:** Linux (Ubuntu en WSL 2), gcc con C11 (`-Wall -Wextra -pedantic -O2`) y GNU Make.",
    ],
    "metodologia": [
        "Enfoque **cuantitativo y experimental por simulación**: la variable independiente es el algoritmo; las "
        "dependientes, los fallos, aciertos, tasa de fallos y escrituras a disco; y se controlan la cadena, el "
        "patrón de lecturas/escrituras y el número de marcos. Los 12 algoritmos comparten una estructura modular "
        "(un archivo `.c` por algoritmo) y sus resultados se validaron con una implementación de referencia "
        "independiente y 67 pruebas automáticas (`make validar`), todas superadas.",
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
    ("12", "Simulación y pruebas", "Validación formal del simulador", 3, "Integrantes 1 y 5", "6–11", "3"),
    ("13", "Simulación y pruebas", "Generación de trazas, CSV y gráficas", 2, "Integrante 6", "12", "3"),
    ("14", "Redacción y validación", "Redacción de Introducción y Capítulo I", 3, "Integrantes 2 y 3", "4", "3"),
    ("15", "Redacción y validación", "Redacción del Capítulo II (cada integrante, sus 2 algoritmos)", 5, "Integrantes 1–6", "13", "4"),
    ("16", "Redacción y validación", "Revisión integral, bibliografía APA 7 y entrega", 2, "Integrantes 1–6", "14, 15", "4"),
]

ANT_INTERNACIONALES = [
    ("Belady, L. A. (1966). *A study of replacement algorithms for a virtual-storage computer*.",
     "Comparó algoritmos de reemplazo mediante simulación de trazas y definió el algoritmo óptimo (MIN), que "
     "expulsa la página cuyo próximo uso está más lejos.",
     "Es el Óptimo que este proyecto usa como cota mínima (15 fallos)."),
    ("Denning, P. J. (1968). *The working set model for program behavior*.",
     "Definió el conjunto de trabajo W(t, τ) y explicó la hiperpaginación como resultado de asignar menos "
     "marcos que los que exige la localidad del programa.",
     "Fundamenta los algoritmos Working Set y WSClock implementados (τ = 4)."),
]

ANT_NACIONALES = [
    ("Ruiz L., E., & Raffo L., E. (2003). *Simulación de la memoria cache*. Industrial Data, 6(2), 48–55. "
     "Universidad Nacional Mayor de San Marcos.",
     "Simularon en C++ una memoria caché con reemplazo FIFO para estimar el porcentaje de aciertos y el tiempo "
     "medio de acceso, y hallaron un tamaño óptimo de caché a partir del cual los aciertos no mejoran.",
     "Comparte el enfoque de simulación en C/C++, el uso de FIFO y la métrica de aciertos."),
]

CONDICIONES = (
    "Todos los algoritmos se ejecutan con **3 marcos inicialmente vacíos** (las primeras cargas cuentan como "
    "fallo) sobre la cadena oficial de la Tabla 2, que tiene 7 páginas distintas (mínimo 7 fallos). Si hay un "
    "marco libre se usa el de menor índice. En cada traza, las filas M1–M3 muestran el contenido de los marcos "
    "**después** de cada referencia; la página cargada aparece **sombreada**, y la fila Res indica fallo (F) o "
    "acierto (H). Cada módulo se compila con los archivos comunes del proyecto (`make`) y se ejecuta con "
    "`./simulador -a N`."
)

# (id, archivo, nombre, integrante, principio, ventaja, desventaja, belady, observación, citas)
ALGORITMOS = [
    (1, "fifo", "FIFO (First-In, First-Out)", 1,
     "Expulsa la página que lleva **más tiempo en memoria**, como una cola; un acierto no cambia el orden. Se "
     "implementa con un puntero circular al marco más antiguo.",
     "muy simple y de costo O(1).", "ignora el uso de las páginas.", "**sí** (9 → 10 fallos con la cadena de Belády).",
     "Expulsa en el paso 6 la página 0, que se necesita en el paso 7.", "Silberschatz et al. (2018)"),
    (2, "optimo", "Óptimo (OPT / MIN)", 1,
     "Expulsa la página cuyo **próximo uso está más lejos** en el futuro. Da el mínimo de fallos posible, pero "
     "no es realizable porque requiere conocer la cadena completa; se usa como cota de comparación.",
     "mínimo de fallos.", "no realizable en un sistema real.", "**no** (algoritmo de pila).",
     "En el paso 18 expulsa la página 2, que no vuelve a usarse hasta el paso 23.", "Belady (1966)"),
    (3, "lru", "LRU (Least Recently Used)", 2,
     "Expulsa la página que lleva **más tiempo sin usarse**, aprovechando la localidad temporal. Cada marco "
     "guarda el paso de su último uso y sale el menor.",
     "buena aproximación del Óptimo.", "su versión exacta es costosa en hardware.", "**no** (algoritmo de pila).",
     "La víctima es siempre la página con el último uso más antiguo.", "Silberschatz et al. (2018)"),
    (4, "reloj", "Reloj o Segunda Oportunidad (Clock)", 2,
     "FIFO circular con **bit de referencia R**: si la página bajo el puntero tiene R = 1, se pone R = 0 y se "
     "avanza (segunda oportunidad); si R = 0, se expulsa.",
     "aproxima LRU con un solo bit.", "si todos tienen R = 1 se comporta como FIFO.", "**sí** (9 → 10).",
     "En el paso 18 los tres bits R valen 1 y el puntero da una vuelta completa.", "Corbató (1969)"),
    (5, "nru", "NRU (Not Recently Used)", 3,
     "Clasifica las páginas por sus bits (R, M) en 4 clases y expulsa una de la **clase más baja** "
     "(no usada y limpia primero). Cada 5 tics una interrupción de reloj pone R = 0. Empate: la más antigua.",
     "simple y evita escrituras.", "decisión gruesa (solo 4 clases).", "posible (no es de pila); no se observó.",
     "En el paso 21 el reloj acaba de limpiar R y sale la página 1, de clase 0.", "Tanenbaum y Bos (2015)"),
    (6, "lfu", "LFU (Least Frequently Used)", 3,
     "Expulsa la página con **menor contador de usos** (el contador vuelve a 1 al cargar). Empate: la más "
     "antigua.",
     "protege las páginas muy usadas.", "una página antigua muy usada puede quedarse sin necesitarse.",
     "posible (se halló un caso: 9 → 11).",
     "La página 0, la más usada y escrita, no es expulsada desde el paso 15.", "Silberschatz et al. (2018)"),
    (7, "mfu", "MFU (Most Frequently Used)", 4,
     "Expulsa la página con **mayor contador de usos**, suponiendo que la de contador bajo acaba de llegar y "
     "aún se usará. Empate: la más antigua.",
     "simple.", "expulsa las páginas más útiles.", "**sí** (9 → 10).",
     "Tras sacar las páginas más usadas, todas quedan con contador 1 y se comporta como FIFO.",
     "Silberschatz et al. (2018)"),
    (8, "reloj_mejorado", "Reloj Mejorado (Enhanced Second Chance)", 4,
     "Reloj con el par (R, M): primero busca (0,0) sin tocar bits; luego (0,1) poniendo R = 0 al pasar, y "
     "repite. Prefiere páginas **no usadas y limpias**.",
     "reduce escrituras a disco.", "hasta 4 vueltas del puntero.", "**sí** (9 → 10).",
     "Iguala a NRU en fallos (21) pero hace una escritura menos.", "Silberschatz et al. (2018)"),
    (9, "aging", "Envejecimiento (Aging)", 5,
     "Cada marco tiene un **registro de 8 bits**; en cada tic se desplaza a la derecha y entra R por la "
     "izquierda. Sale la página con el registro menor.",
     "aproxima LRU con pocos bits.", "solo recuerda los últimos 8 tics.", "posible (no es de pila); no se observó.",
     "Reproduce exactamente la traza de LRU en los 30 pasos.", "Tanenbaum y Bos (2015)"),
    (10, "working_set", "Conjunto de Trabajo (Working Set)", 5,
     "Expulsa una página **fuera del conjunto de trabajo**: con R = 0 y sin usarse en los últimos τ = 4 tics. "
     "Cada marco guarda R y el tiempo del último uso (TUU); R se limpia cada 5 tics.",
     "relaciona el reemplazo con la localidad.", "más costoso; depende de τ.",
     "posible con marcos fijos (se halló un caso).",
     "En el paso 23 la página 7 tenía edad 5 > τ y salió.", "Denning (1968)"),
    (11, "wsclock", "WSClock (Working Set Clock)", 6,
     "Reloj combinado con el conjunto de trabajo: expulsa una página **vieja y limpia**; si está vieja y "
     "sucia, **programa su escritura** y sigue buscando.",
     "eficiente y con pocas escrituras.", "más complejo que el Reloj.", "**sí** (9 → 10).",
     "Junto con LFU, es el mejor algoritmo realizable (19 fallos, 4 escrituras).", "Carr y Hennessy (1981)"),
    (12, "aleatorio", "Reemplazo Aleatorio (Random)", 6,
     "Elige la víctima al azar con un generador congruencial lineal propio, "
     "x = (1103515245·x + 12345) mod 2³¹, semilla 42, para que el resultado sea reproducible.",
     "costo mínimo.", "resultado variable según la semilla.", "**sí** (posible en cualquier caso).",
     "Con la semilla 42 obtiene 20 fallos; con otra semilla el resultado cambia.", "Belady (1966)"),
]

CONCLUSIONES = [
    "Los 12 algoritmos se implementaron en C para Linux en un simulador modular que compila sin advertencias "
    "y muestra la traza de cada uno.",
    "Con 3 marcos y 30 referencias, el **Óptimo** obtuvo 15 fallos (el mínimo); **LFU y WSClock**, 19 (los "
    "mejores realizables, con solo 4 escrituras); y **FIFO y MFU**, 25 (los peores).",
    "**Reloj Mejorado** igualó a **NRU** en fallos (21) pero escribió menos, y **Aging** reprodujo exactamente "
    "a **LRU** (22).",
    "Se verificó la **anomalía de Belády**: FIFO, Reloj, MFU, Reloj Mejorado y WSClock pasan de 9 a 10 fallos "
    "con un marco más; LRU y el Óptimo, algoritmos de pila, nunca la presentaron.",
]

RECOMENDACIONES = [
    "Repetir el experimento con cadenas de programas reales y con varios procesos.",
    "Ejecutar `make validar` antes de modificar el simulador.",
]

BIBLIOGRAFIA = [
    "Belady, L. A. (1966). A study of replacement algorithms for a virtual-storage computer. *IBM Systems Journal, 5*(2), 78–101. https://doi.org/10.1147/sj.52.0078",
    "Belady, L. A., Nelson, R. A., & Shedler, G. S. (1969). An anomaly in space-time characteristics of certain programs running in a paging machine. *Communications of the ACM, 12*(6), 349–353. https://doi.org/10.1145/363011.363155",
    "Carr, R. W., & Hennessy, J. L. (1981). WSCLOCK—A simple and effective algorithm for virtual memory management. En *Proceedings of the Eighth ACM Symposium on Operating Systems Principles* (pp. 87–95). ACM. https://doi.org/10.1145/800216.806596",
    "Corbató, F. J. (1969). A paging experiment with the Multics system. En H. Feshbach & K. U. Ingard (Eds.), *In honor of Philip M. Morse* (pp. 217–228). MIT Press.",
    "Denning, P. J. (1968). The working set model for program behavior. *Communications of the ACM, 11*(5), 323–333. https://doi.org/10.1145/363095.363141",
    "Kilburn, T., Edwards, D. B. G., Lanigan, M. J., & Sumner, F. H. (1962). One-level storage system. *IRE Transactions on Electronic Computers, EC-11*(2), 223–235. https://doi.org/10.1109/TEC.1962.5219356",
    "Ruiz L., E., & Raffo L., E. (2003). Simulación de la memoria cache. *Industrial Data, 6*(2), 48–55. https://www.redalyc.org/articulo.oa?id=81660207",
    "Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating system concepts* (10th ed.). Wiley.",
    "Tanenbaum, A. S., & Bos, H. (2015). *Modern operating systems* (4th ed.). Pearson.",
]
