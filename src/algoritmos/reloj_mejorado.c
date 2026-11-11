/*
 * reloj_mejorado.c - Algoritmo 8: Reloj Mejorado (Enhanced Second Chance)
 * Responsable: Integrante 4 (Marcus Meza)
 *
 * Idea (Silberschatz): Reloj que considera el par (R, M):
 *     (0,0) no usada, limpia  -> mejor víctima
 *     (0,1) no usada, sucia   -> hay que escribirla antes
 *     (1,0) usada, limpia
 *     (1,1) usada, sucia      -> peor víctima
 * Búsqueda con el puntero, desde su posición actual:
 *   Pasada 1: buscar (0,0) dando una vuelta SIN modificar bits.
 *   Pasada 2: buscar (0,1) poniendo R = 0 en cada marco recorrido.
 *   Si no hubo víctima, se repite (ahora todos tienen R = 0).
 * Tras reemplazar, el puntero queda en el marco siguiente.
 *
 * Variables auxiliares: bits R y M, puntero y pasada en que se halló la víctima.
 */
#include "../algoritmos.h"

void simular_reloj_mejorado(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int bit_r[MAX_MARCOS] = {0};
    int bit_m[MAX_MARCOS] = {0};
    int puntero = 0;
    char br[AUX_LEN / 3], bm[AUX_LEN / 3];

    resultado_iniciar(r, "Reloj Mejorado", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int w = es_escritura(cfg, i);
        int idx = buscar_pagina(marcos, cfg->marcos, pagina);
        int marco, victima = -1, pasada = 0;

        if (idx >= 0) {
            bit_r[idx] = 1;
            bit_m[idx] |= w;
            registrar_paso(r, cfg, i, marcos, -1, -1, "R=%s M=%s ptr=M%d",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos), puntero + 1);
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            marco = -1;
            while (marco < 0) {
                /* Pasada 1: (0,0) sin tocar bits */
                pasada++;
                for (int k = 0; k < cfg->marcos; k++) {
                    int c = (puntero + k) % cfg->marcos;
                    if (bit_r[c] == 0 && bit_m[c] == 0) {
                        marco = c;
                        break;
                    }
                }
                if (marco >= 0)
                    break;
                /* Pasada 2: (0,1) limpiando R al pasar */
                pasada++;
                for (int k = 0; k < cfg->marcos; k++) {
                    int c = (puntero + k) % cfg->marcos;
                    if (bit_r[c] == 0 && bit_m[c] == 1) {
                        marco = c;
                        break;
                    }
                    bit_r[c] = 0;
                }
            }
            victima = marcos[marco];
            puntero = (marco + 1) % cfg->marcos;
        }
        marcos[marco] = pagina;
        bit_r[marco] = 1;
        bit_m[marco] = w;

        if (victima >= 0)
            registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s M=%s ptr=M%d (pasada %d)",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos), puntero + 1, pasada);
        else
            registrar_paso(r, cfg, i, marcos, marco, victima, "R=%s M=%s ptr=M%d",
                           fmt_arreglo(br, sizeof br, bit_r, cfg->marcos),
                           fmt_arreglo(bm, sizeof bm, bit_m, cfg->marcos), puntero + 1);
    }
}
