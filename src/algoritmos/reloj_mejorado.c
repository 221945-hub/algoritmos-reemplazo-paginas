/*
 * reloj_mejorado.c - Algoritmo 8: Reloj Mejorado
 * Responsable: Integrante 4
 *
 * Idea: reloj con clases (R,M); prefiere paginas no usadas y limpias.
 * Reglas exactas: ver docs/PASO_01_parametros.md, seccion 1.5, fila 8.
 *
 * ESTADO: PENDIENTE (se implementa en el PASO 4).
 * Usar src/algoritmos/fifo.c como plantilla:
 *   1. resultado_iniciar(r, "<nombre>", cfg);  marcos_vaciar(...)
 *   2. por cada referencia i: acierto -> registrar_paso(..., -1, -1, aux)
 *                             fallo   -> elegir marco/victima y registrar_paso(...)
 */
#include "../algoritmos.h"

void simular_reloj_mejorado(const Config *cfg, Resultado *r)
{
    resultado_iniciar(r, "Reloj Mejorado", cfg);
    r->implementado = 0;   /* TODO Paso 4 */
}
