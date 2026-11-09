/*
 * reloj.c - Algoritmo 4: Reloj / Segunda Oportunidad (Clock)
 * Responsable: Integrante 2
 *
 * Idea: FIFO circular con bit de referencia R. El puntero (manecilla)
 * recorre los marcos: si R = 1 se le da una "segunda oportunidad"
 * (R = 0 y avanza); si R = 0, esa página es la víctima.
 * Al cargar o en un acierto: R = 1. Tras reemplazar, el puntero avanza.
 * El puntero empieza en M1 y no se mueve mientras se llenan marcos libres.
 *
 * Variables auxiliares: bits R de cada marco y posición del puntero.
 */
#include "../algoritmos.h"

void simular_reloj(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int bit_r[MAX_MARCOS] = {0};
    int puntero = 0;
    char buf[AUX_LEN];

    resultado_iniciar(r, "Reloj (Clock)", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int idx = buscar_pagina(marcos, cfg->marcos, pagina);
        int marco, victima = -1, segundas = 0;

        if (idx >= 0) {
            bit_r[idx] = 1;
            registrar_paso(r, cfg, i, marcos, -1, -1, "R=%s ptr=M%d",
                           fmt_arreglo(buf, sizeof buf, bit_r, cfg->marcos), puntero + 1);
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            while (bit_r[puntero] == 1) {       /* segunda oportunidad */
                bit_r[puntero] = 0;
                puntero = (puntero + 1) % cfg->marcos;
                segundas++;
            }
            marco = puntero;
            victima = marcos[marco];
            puntero = (puntero + 1) % cfg->marcos;
        }
        marcos[marco] = pagina;
        bit_r[marco] = 1;

        if (victima >= 0)
            registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s ptr=M%d (2das oport.: %d)",
                           fmt_arreglo(buf, sizeof buf, bit_r, cfg->marcos), puntero + 1, segundas);
        else
            registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s ptr=M%d",
                           fmt_arreglo(buf, sizeof buf, bit_r, cfg->marcos), puntero + 1);
    }
}
