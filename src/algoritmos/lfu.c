/*
 * lfu.c - Algoritmo 6: LFU
 * Responsable: Integrante 3
 *
 * Idea: expulsa la pagina con menor contador de usos (empate FIFO).
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 6.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_lfu(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "LFU", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
