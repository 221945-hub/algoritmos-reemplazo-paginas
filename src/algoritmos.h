/*
 * algoritmos.h - Interfaz común de los 12 algoritmos (PASO 3)
 *
 * Todos los algoritmos tienen la MISMA firma:
 *     void simular_xxx(const Config *cfg, Resultado *r);
 * Así main.c puede ejecutarlos desde una tabla (punteros a función).
 */
#ifndef ALGORITMOS_H
#define ALGORITMOS_H

#include "comun.h"

#define NUM_ALGORITMOS 12

typedef void (*FuncSimular)(const Config *cfg, Resultado *r);

typedef struct {
    int id;
    const char *nombre;
    const char *responsable;
    FuncSimular simular;
} Algoritmo;

extern const Algoritmo ALGORITMOS[NUM_ALGORITMOS];

/* Integrante 1 */
void simular_fifo(const Config *cfg, Resultado *r);
void simular_optimo(const Config *cfg, Resultado *r);
/* Integrante 2 */
void simular_lru(const Config *cfg, Resultado *r);
void simular_reloj(const Config *cfg, Resultado *r);
/* Integrante 3 */
void simular_nru(const Config *cfg, Resultado *r);
void simular_lfu(const Config *cfg, Resultado *r);
/* Integrante 4 */
void simular_mfu(const Config *cfg, Resultado *r);
void simular_reloj_mejorado(const Config *cfg, Resultado *r);
/* Integrante 5 */
void simular_aging(const Config *cfg, Resultado *r);
void simular_working_set(const Config *cfg, Resultado *r);
/* Integrante 6 */
void simular_wsclock(const Config *cfg, Resultado *r);
void simular_aleatorio(const Config *cfg, Resultado *r);

#endif /* ALGORITMOS_H */
