/*
 * nru.c - Algoritmo 5: NRU
 * Responsable: Integrante 3
 *
 * Idea: expulsa una pagina de la clase (R,M) mas baja; R se limpia cada PERIODO_RELOJ tics.
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 5.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_nru(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "NRU", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
