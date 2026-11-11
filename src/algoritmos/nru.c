/*
 * nru.c - Algoritmo 5: NRU (Not Recently Used)
 * Responsable: Integrante 1 (Angel Alvarez)
 *
 * Idea (Tanenbaum 3.4.2): cada página tiene bits R (referenciada) y
 * M (modificada). Una interrupción de reloj cada PERIODO_RELOJ tics pone
 * todos los R en 0. Las páginas se agrupan en 4 clases:
 *     clase 0 = (R=0,M=0)  no usada, limpia     <- mejor víctima
 *     clase 1 = (R=0,M=1)  no usada, sucia
 *     clase 2 = (R=1,M=0)  usada, limpia
 *     clase 3 = (R=1,M=1)  usada, sucia
 * Se expulsa una página de la clase más baja; empate: la más antigua (FIFO).
 * A diferencia del Reloj Mejorado, revisa TODA la tabla (sin puntero).
 *
 * Variables auxiliares: bits R y M, y aviso cuando el reloj limpia R.
 */
#include "../algoritmos.h"

void simular_nru(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int bit_r[MAX_MARCOS] = {0};
    int bit_m[MAX_MARCOS] = {0};
    int llegada[MAX_MARCOS] = {0};
    char br[AUX_LEN / 3], bm[AUX_LEN / 3];

    resultado_iniciar(r, "NRU", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int w = es_escritura(cfg, i);
        int reset = (i > 0 && i % PERIODO_RELOJ == 0);
        int idx, marco, victima = -1, clase_victima = -1;

        /* Interrupción de reloj: limpia los bits R al inicio del tic */
        if (reset)
            for (int k = 0; k < cfg->marcos; k++)
                bit_r[k] = 0;

        idx = buscar_pagina(marcos, cfg->marcos, pagina);
        if (idx >= 0) {
            bit_r[idx] = 1;
            bit_m[idx] |= w;
            registrar_paso(r, cfg, i, marcos, -1, -1, "R=%s M=%s%s",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos),
                           reset ? " [reloj: R<-0]" : "");
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            int mejor = 0;
            for (int k = 1; k < cfg->marcos; k++) {
                int ck = 2 * bit_r[k] + bit_m[k];
                int cm = 2 * bit_r[mejor] + bit_m[mejor];
                if (ck < cm || (ck == cm && llegada[k] < llegada[mejor]))
                    mejor = k;
            }
            marco = mejor;
            clase_victima = 2 * bit_r[marco] + bit_m[marco];
            victima = marcos[marco];
        }
        marcos[marco] = pagina;
        bit_r[marco] = 1;
        bit_m[marco] = w;
        llegada[marco] = i;

        if (victima >= 0)
            registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s M=%s clase=%d%s",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos),
                           clase_victima, reset ? " [reloj: R<-0]" : "");
        else
            registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s M=%s%s",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos),
                           reset ? " [reloj: R<-0]" : "");
    }
}
