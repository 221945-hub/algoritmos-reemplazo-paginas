/*
 * working_set.c - Algoritmo 10: Working Set (Conjunto de Trabajo)
 * Responsable: Integrante 5 (Elvis Suca)
 *
 * Idea (Denning 1968; versión de reemplazo de Tanenbaum 3.4.8):
 * el conjunto de trabajo son las páginas usadas en los últimos WS_TAU tics.
 * Una página FUERA del conjunto de trabajo es buena víctima.
 *
 * Cada marco guarda R y TUU (tiempo virtual del último uso). El TUU NO se
 * actualiza en cada acierto (eso sería LRU exacto, muy caro): se actualiza
 * al cargar y durante el barrido en un fallo. Los bits R se limpian con
 * una interrupción de reloj cada PERIODO_RELOJ tics.
 *
 * Fallo con memoria llena, barrido de M1 a Mn (t = paso actual, base 1):
 *   - R = 1            -> TUU = t (está en el conjunto de trabajo).
 *   - R = 0, edad > τ  -> fuera del conjunto: la PRIMERA encontrada es la
 *                         víctima (el barrido sigue solo para actualizar TUU).
 *   - R = 0, edad <= τ -> se recuerda la de mayor edad.
 *   Sin víctima: la de mayor edad con R = 0; si todas tienen R = 1, M1.
 *
 * Variables auxiliares: bits R, TUU de cada marco y aviso de reloj.
 */
#include "../algoritmos.h"

void simular_working_set(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int bit_r[MAX_MARCOS] = {0};
    int tuu[MAX_MARCOS];
    char br[AUX_LEN / 3], bt[AUX_LEN / 3];

    resultado_iniciar(r, "Working Set", cfg);
    marcos_vaciar(marcos, cfg->marcos);
    marcos_vaciar(tuu, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int t = i + 1;
        int pagina = cfg->refs[i];
        int reset = (i > 0 && i % PERIODO_RELOJ == 0);
        int idx, marco, victima = -1;
        const char *motivo = "";

        if (reset)
            for (int k = 0; k < cfg->marcos; k++)
                bit_r[k] = 0;

        idx = buscar_pagina(marcos, cfg->marcos, pagina);
        if (idx >= 0) {
            bit_r[idx] = 1;
            registrar_paso(r, cfg, i, marcos, -1, -1, "R=%s TUU=%s t=%d%s",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bt, sizeof bt, tuu, cfg->marcos), t,
                           reset ? " [reloj: R<-0]" : "");
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            int fuera = -1, mas_viejo = -1, edad_max = -1;
            for (int k = 0; k < cfg->marcos; k++) {
                if (bit_r[k] == 1) {
                    tuu[k] = t;
                } else {
                    int edad = t - tuu[k];
                    if (edad > WS_TAU && fuera < 0)
                        fuera = k;
                    if (edad > edad_max) {
                        edad_max = edad;
                        mas_viejo = k;
                    }
                }
            }
            if (fuera >= 0) {
                marco = fuera;
                motivo = " fuera del WS";
            } else if (mas_viejo >= 0) {
                marco = mas_viejo;
                motivo = " todas en WS: la mas vieja";
            } else {
                marco = 0;
                motivo = " todas R=1: M1";
            }
            victima = marcos[marco];
        }
        marcos[marco] = pagina;
        bit_r[marco] = 1;
        tuu[marco] = t;

        registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s TUU=%s t=%d%s%s",
                       fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                       fmt_arreglo(bt, sizeof bt, tuu, cfg->marcos), t,
                       reset ? " [reloj: R<-0]" : "", motivo);
    }
}
