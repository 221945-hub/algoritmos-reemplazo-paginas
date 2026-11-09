/*
 * aging.c - Algoritmo 9: Aging
 * Responsable: Integrante 5
 *
 * Idea: registro de 8 bits desplazado cada tic; sale el de menor valor.
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 9.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_aging(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "Aging", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
