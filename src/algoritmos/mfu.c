/*
 * mfu.c - Algoritmo 7: MFU (Most Frequently Used)
 * Responsable: Integrante 4
 *
 * Idea: se expulsa la página con MAYOR contador de usos, bajo el
 * argumento de que una página muy usada "ya cumplió su función" y la de
 * contador bajo acaba de llegar y aún se usará. Mismo contador que LFU
 * (se reinicia a 1 al cargar). Empate: la que llegó primero (FIFO).
 *
 * Variables auxiliares: contador de frecuencia de cada marco.
 */
#include "../algoritmos.h"

void simular_mfu(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int frec[MAX_MARCOS] = {0};
    int llegada[MAX_MARCOS] = {0};
    char buf[AUX_LEN];

    resultado_iniciar(r, "MFU", cfg);
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
                if (frec[k] > frec[marco] ||
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
