/*
 * optimo.c - Algoritmo 2: Optimo (OPT)
 * Responsable: Integrante 1
 *
 * Idea: expulsa la pagina cuyo proximo uso esta mas lejos en el futuro.
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 2.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_optimo(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "Optimo (OPT)", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
