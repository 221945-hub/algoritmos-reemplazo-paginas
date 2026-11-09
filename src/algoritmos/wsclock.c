/*
 * wsclock.c - Algoritmo 11: WSClock (Working Set Clock)
 * Responsable: Integrante 6
 *
 * Idea (Carr y Hennessy 1981; Tanenbaum 3.4.9): combina Reloj y conjunto de
 * trabajo. Cada marco guarda R, M y TUU (tiempo del último uso).
 * Acierto: R = 1, TUU = t, M |= W.
 * Fallo con memoria llena, el puntero recorre como máximo una vuelta:
 *   - R = 1                    -> R = 0, TUU = t, avanza.
 *   - R = 0, edad > τ, M = 0   -> VÍCTIMA (vieja y limpia).
 *   - R = 0, edad > τ, M = 1   -> se programa su escritura a disco
 *                                 (M = 0, cuenta 1 escritura) y avanza.
 *   - R = 0, edad <= τ         -> está en el conjunto de trabajo, avanza.
 * Si la vuelta termina sin víctima: el primer marco (desde el puntero) con
 * R = 0 y M = 0; si no existe, el marco bajo el puntero.
 *
 * Variables auxiliares: bits R, M, TUU, puntero y escrituras programadas.
 */
#include "../algoritmos.h"

void simular_wsclock(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int bit_r[MAX_MARCOS] = {0};
    int bit_m[MAX_MARCOS] = {0};
    int tuu[MAX_MARCOS];
    int puntero = 0;
    char br[AUX_LEN / 4], bm[AUX_LEN / 4], bt[AUX_LEN / 4];

    resultado_iniciar(r, "WSClock", cfg);
    marcos_vaciar(marcos, cfg->marcos);
    marcos_vaciar(tuu, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int t = i + 1;
        int pagina = cfg->refs[i];
        int w = es_escritura(cfg, i);
        int idx = buscar_pagina(marcos, cfg->marcos, pagina);
        int marco, victima = -1, programadas = 0;

        if (idx >= 0) {
            bit_r[idx] = 1;
            bit_m[idx] |= w;
            tuu[idx] = t;
            registrar_paso(r, cfg, i, marcos, -1, -1, "R=%s M=%s TUU=%s ptr=M%d",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos),
                           fmt_arreglo(bt, sizeof bt, tuu, cfg->marcos), puntero + 1);
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            marco = -1;
            for (int k = 0; k < cfg->marcos && marco < 0; k++) {
                int c = puntero;
                if (bit_r[c] == 1) {
                    bit_r[c] = 0;
                    tuu[c] = t;
                } else if (t - tuu[c] > WSCLOCK_TAU) {
                    if (bit_m[c] == 0) {
                        marco = c;                  /* vieja y limpia */
                        break;
                    }
                    bit_m[c] = 0;                   /* programar escritura */
                    marcar_escrito(r, c);
                    programadas++;
                }
                puntero = (puntero + 1) % cfg->marcos;
            }
            if (marco < 0) {
                for (int k = 0; k < cfg->marcos && marco < 0; k++) {
                    int c = (puntero + k) % cfg->marcos;
                    if (bit_r[c] == 0 && bit_m[c] == 0)
                        marco = c;
                }
                if (marco < 0)
                    marco = puntero;
            }
            victima = marcos[marco];
            puntero = (marco + 1) % cfg->marcos;
        }
        marcos[marco] = pagina;
        bit_r[marco] = 1;
        bit_m[marco] = w;
        tuu[marco] = t;

        if (programadas > 0)
            registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s M=%s TUU=%s ptr=M%d escr.prog=%d",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos),
                           fmt_arreglo(bt, sizeof bt, tuu, cfg->marcos), puntero + 1, programadas);
        else
            registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s M=%s TUU=%s ptr=M%d",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos),
                           fmt_arreglo(bt, sizeof bt, tuu, cfg->marcos), puntero + 1);
    }
}
