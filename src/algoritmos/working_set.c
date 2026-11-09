/*
 * working_set.c - Algoritmo 10: Working Set
 * Responsable: Integrante 5
 *
 * Idea: expulsa una pagina fuera del conjunto de trabajo (edad > WS_TAU).
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 10.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_working_set(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "Working Set", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
