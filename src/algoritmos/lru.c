/*
 * lru.c - Algoritmo 3: LRU
 * Responsable: Integrante 2
 *
 * Idea: expulsa la pagina que lleva mas tiempo sin usarse.
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 3.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_lru(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "LRU", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
