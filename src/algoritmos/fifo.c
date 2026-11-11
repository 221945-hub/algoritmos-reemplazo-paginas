/*
 * fifo.c - Algoritmo 1: FIFO (First-In, First-Out)
 * Responsable: Integrante 5 (Elvis Suca)
 *
 * Idea: se expulsa la página que lleva más tiempo en memoria.
 * Como los marcos vacíos se llenan en orden (M1, M2, M3) y cada reemplazo
 * ocurre en el marco más antiguo, basta un puntero circular que indica
 * "el marco que llegó primero". Un acierto NO modifica la cola.
 *
 * Variables auxiliares mostradas: cola de llegada (más antigua primero).
 *
 * Este módulo es la PLANTILLA de referencia para los demás algoritmos.
 */
#include "../algoritmos.h"

/* Arma la cola de llegada empezando por el marco más antiguo */
static const char *cola_fifo(char *buf, size_t len, const int marcos[], int m, int puntero)
{
    int cola[MAX_MARCOS];
    int cant = 0;

    for (int k = 0; k < m; k++) {
        int idx = (puntero + k) % m;
        if (marcos[idx] != MARCO_VACIO)
            cola[cant++] = marcos[idx];
    }
    return fmt_arreglo(buf, len, cola, cant);
}

void simular_fifo(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int puntero = 0;            /* marco con la página más antigua */
    char buf[AUX_LEN];

    resultado_iniciar(r, "FIFO", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int marco, victima = -1;

        if (buscar_pagina(marcos, cfg->marcos, pagina) >= 0) {
            /* Acierto: la cola no cambia */
            registrar_paso(r, cfg, i, marcos, -1, -1, "cola=%s",
                           cola_fifo(buf, sizeof buf, marcos, cfg->marcos, puntero));
            continue;
        }

        /* Fallo de página */
        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            marco = puntero;                       /* el más antiguo */
            victima = marcos[marco];
            puntero = (puntero + 1) % cfg->marcos;
        }
        marcos[marco] = pagina;

        registrar_paso(r, cfg, i, marcos, marco, victima, "cola=%s",
                       cola_fifo(buf, sizeof buf, marcos, cfg->marcos, puntero));
    }
}
