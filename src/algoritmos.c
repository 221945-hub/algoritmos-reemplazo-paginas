/*
 * algoritmos.c - Registro de los 12 algoritmos (PASO 3)
 * Para agregar o reordenar algoritmos solo se modifica esta tabla.
 */
#include "algoritmos.h"

const Algoritmo ALGORITMOS[NUM_ALGORITMOS] = {
    {  1, "FIFO",              "Elvis Suca", simular_fifo },
    {  2, "Optimo (OPT)",      "Jhamil Huahualuque", simular_optimo },
    {  3, "LRU",               "Jhamil Huahualuque", simular_lru },
    {  4, "Reloj (Clock)",     "Haider Carpio", simular_reloj },
    {  5, "NRU",               "Angel Alvarez", simular_nru },
    {  6, "LFU",               "Elvis Suca", simular_lfu },
    {  7, "MFU",               "Angel Alvarez", simular_mfu },
    {  8, "Reloj Mejorado",    "Marcus Meza", simular_reloj_mejorado },
    {  9, "Aging",             "Marcus Meza", simular_aging },
    { 10, "Working Set",       "Elvis Suca", simular_working_set },
    { 11, "WSClock",           "Haider Carpio", simular_wsclock },
    { 12, "Aleatorio (RAND)",  "Jhamil Huahualuque", simular_aleatorio },
};
