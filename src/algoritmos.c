/*
 * algoritmos.c - Registro de los 12 algoritmos (PASO 3)
 * Para agregar o reordenar algoritmos solo se modifica esta tabla.
 */
#include "algoritmos.h"

const Algoritmo ALGORITMOS[NUM_ALGORITMOS] = {
    {  1, "FIFO",              "Integrante 1", simular_fifo },
    {  2, "Optimo (OPT)",      "Integrante 1", simular_optimo },
    {  3, "LRU",               "Integrante 2", simular_lru },
    {  4, "Reloj (Clock)",     "Integrante 2", simular_reloj },
    {  5, "NRU",               "Integrante 3", simular_nru },
    {  6, "LFU",               "Integrante 3", simular_lfu },
    {  7, "MFU",               "Integrante 4", simular_mfu },
    {  8, "Reloj Mejorado",    "Integrante 4", simular_reloj_mejorado },
    {  9, "Aging",             "Integrante 5", simular_aging },
    { 10, "Working Set",       "Integrante 5", simular_working_set },
    { 11, "WSClock",           "Integrante 6", simular_wsclock },
    { 12, "Aleatorio (RAND)",  "Integrante 6", simular_aleatorio },
};
