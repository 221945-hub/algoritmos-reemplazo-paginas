/*
 * reloj.c - Algoritmo 4: Reloj (Clock)
 * Responsable: Integrante 2
 *
 * Idea: FIFO circular con bit R; si R=1 se da segunda oportunidad.
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 4.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_reloj(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "Reloj (Clock)", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
