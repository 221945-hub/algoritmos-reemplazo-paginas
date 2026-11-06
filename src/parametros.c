/*
 * parametros.c - Definición de la cadena de referencias y patrón de escrituras
 * Ver docs/PASO_01_parametros.md para la justificación de cada valor.
 */
#include "parametros.h"

/*                          paso: 1  2  3  4  5   6  7  8  9 10  11 12 13 14 15  16 17 18 19 20  21 22 23 24 25  26 27 28 29 30 */
const int REFS[NUM_REFS]      = { 7, 0, 1, 2, 0,  3, 0, 4, 2, 3,  0, 3, 2, 1, 2,  0, 1, 7, 0, 1,  3, 5, 2, 0, 1,  4, 2, 3, 0, 1 };
const int ESCRITURA[NUM_REFS] = { 0, 1, 0, 0, 1,  0, 0, 1, 1, 0,  1, 0, 0, 0, 1,  0, 0, 0, 1, 0,  1, 0, 1, 1, 0,  0, 0, 1, 1, 0 };
