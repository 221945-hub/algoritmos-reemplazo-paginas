/*
 * parametros.h - Parámetros fijos del experimento (PASO 1)
 * Proyecto: Algoritmos de reemplazo de páginas - Sistemas Operativos UNSAAC 2026-II
 *
 * Todos los algoritmos DEBEN usar exactamente estos valores para que la
 * comparación sea válida. Ver docs/PASO_01_parametros.md.
 */
#ifndef PARAMETROS_H
#define PARAMETROS_H

/* ---- Entorno de memoria ---- */
#define NUM_MARCOS      3    /* marcos físicos disponibles              */
#define NUM_REFS        30   /* longitud de la cadena de referencias    */
#define MARCO_VACIO     (-1) /* valor de un marco sin página cargada    */

/* ---- Parámetros específicos de algoritmos ---- */
#define AGING_BITS      8    /* ancho del registro de envejecimiento    */
#define WSCLOCK_TAU     4    /* ventana del conjunto de trabajo (tics)  */
#define RANDOM_SEMILLA  42u  /* semilla del generador LCG propio        */
#define SFIFO_PRIMARIA  2    /* marcos de la lista primaria (FIFO)      */
#define SFIFO_SECUNDARIA 1   /* marcos de la lista secundaria (LRU)     */
#define PB_BUFFER       2    /* capacidad total listas libre+modificada */

/* Cadena oficial de 30 referencias (idéntica para los 12 algoritmos) */
extern const int REFS[NUM_REFS];

/* Tipo de acceso de cada referencia: 0 = lectura (R), 1 = escritura (W) */
extern const int ESCRITURA[NUM_REFS];

#endif /* PARAMETROS_H */
