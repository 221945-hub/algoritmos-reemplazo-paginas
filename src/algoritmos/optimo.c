/*
 * optimo.c - Algoritmo 2: Óptimo (OPT / MIN de Belády)
 * Responsable: Integrante 3 (Jhamil Huahualuque)
 *
 * Idea: se expulsa la página cuyo PRÓXIMO uso está más lejos en el futuro
 * (o que no se volverá a usar). Requiere conocer toda la cadena por
 * adelantado, por eso no es implementable en un SO real; sirve como
 * cota mínima de fallos para comparar a los demás algoritmos.
 *
 * Empate (varias páginas que no se vuelven a usar): menor índice de marco.
 * Variables auxiliares: paso del próximo uso de cada marco ("--" = nunca).
 *   En un reemplazo se muestran los valores con los que se decidió.
 */
#include "../algoritmos.h"

#define NUNCA 1000000   /* distancia "infinita": la página no se vuelve a usar */

/* Paso (0-based) del próximo uso de 'pagina' después de 'desde', o NUNCA */
static int proximo_uso(const Config *cfg, int pagina, int desde)
{
    for (int j = desde + 1; j < cfg->n; j++)
        if (cfg->refs[j] == pagina)
            return j;
    return NUNCA;
}

/* Texto "prox=[5,14,--]" con pasos en base 1 */
static const char *fmt_proximos(char *buf, size_t len, const Config *cfg,
                                const int marcos[], int i)
{
    size_t u = (size_t)snprintf(buf, len, "prox=[");
    for (int k = 0; k < cfg->marcos && u < len; k++) {
        const char *sep = (k + 1 < cfg->marcos) ? "," : "]";
        int prox = marcos[k] == MARCO_VACIO ? NUNCA : proximo_uso(cfg, marcos[k], i);
        if (marcos[k] == MARCO_VACIO)
            u += (size_t)snprintf(buf + u, len - u, "-%s", sep);
        else if (prox == NUNCA)
            u += (size_t)snprintf(buf + u, len - u, "--%s", sep);
        else
            u += (size_t)snprintf(buf + u, len - u, "%d%s", prox + 1, sep);
    }
    return buf;
}

void simular_optimo(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    char buf[AUX_LEN];

    resultado_iniciar(r, "Optimo (OPT)", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int marco, victima = -1;

        if (buscar_pagina(marcos, cfg->marcos, pagina) >= 0) {
            registrar_paso(r, cfg, i, marcos, -1, -1, "%s",
                           fmt_proximos(buf, sizeof buf, cfg, marcos, i));
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            int mas_lejano = -1;
            /* Decidir con el estado ANTES del reemplazo */
            fmt_proximos(buf, sizeof buf, cfg, marcos, i);
            for (int k = 0; k < cfg->marcos; k++) {
                int prox = proximo_uso(cfg, marcos[k], i);
                if (prox > mas_lejano) {        /* '>' estricto: empate -> menor índice */
                    mas_lejano = prox;
                    marco = k;
                }
            }
            victima = marcos[marco];
            marcos[marco] = pagina;
            registrar_paso(r, cfg, i, marcos, marco, victima, "%s -> sale la mas lejana", buf);
            continue;
        }

        marcos[marco] = pagina;
        registrar_paso(r, cfg, i, marcos, marco, victima, "%s",
                       fmt_proximos(buf, sizeof buf, cfg, marcos, i));
    }
}
