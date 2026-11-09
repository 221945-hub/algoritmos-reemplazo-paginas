/*
 * mfu.c - Algoritmo 7: MFU
 * Responsable: Integrante 4
 *
 * Idea: expulsa la pagina con mayor contador de usos (empate FIFO).
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 7.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_mfu(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "MFU", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
