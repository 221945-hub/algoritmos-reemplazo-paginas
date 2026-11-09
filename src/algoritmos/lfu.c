/*
 * lfu.c - Algoritmo 6: LFU (Least Frequently Used)
 * Responsable: Integrante 3
 *
 * Idea: cada página en memoria lleva un contador de usos; se expulsa la
 * de MENOR contador. El contador se reinicia a 1 al cargar la página
 * (no se guarda historial de páginas que están fuera de memoria).
 * Empate: la que llegó primero (FIFO).
 *
 * Variables auxiliares: contador de frecuencia de cada marco.
 */
#include "../algoritmos.h"

void simular_lfu(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int frec[MAX_MARCOS] = {0};
    int llegada[MAX_MARCOS] = {0};
    char buf[AUX_LEN];

    resultado_iniciar(r, "LFU", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int idx = buscar_pagina(marcos, cfg->marcos, pagina);
        int marco, victima = -1;

        if (idx >= 0) {
            frec[idx]++;
            registrar_paso(r, cfg, i, marcos, -1, -1, "frec=%s",
                           fmt_arreglo(buf, sizeof buf, frec, cfg->marcos));
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            marco = 0;
            for (int k = 1; k < cfg->marcos; k++)
                if (frec[k] < frec[marco] ||
                    (frec[k] == frec[marco] && llegada[k] < llegada[marco]))
                    marco = k;
            victima = marcos[marco];
        }
        marcos[marco] = pagina;
        frec[marco] = 1;
        llegada[marco] = i;
        registrar_paso(r, cfg, i, marcos, marco, victima, "frec=%s",
                       fmt_arreglo(buf, sizeof buf, frec, cfg->marcos));
    }
}
