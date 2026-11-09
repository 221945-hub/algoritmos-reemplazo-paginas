/*
 * aleatorio.c - Algoritmo 12: Aleatorio (RAND)
 * Responsable: Integrante 6
 *
 * Idea: victima elegida con LCG propio, semilla RANDOM_SEMILLA.
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 12.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_aleatorio(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "Aleatorio (RAND)", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
