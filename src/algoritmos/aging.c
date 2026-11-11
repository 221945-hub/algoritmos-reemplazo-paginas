/*
 * aging.c - Algoritmo 9: Envejecimiento (Aging)
 * Responsable: Integrante 4 (Marcus Meza)
 *
 * Idea (Tanenbaum 3.4.7): aproximación de LRU en software. Cada marco tiene
 * un registro de AGING_BITS bits. Al final de cada tic de reloj:
 *     reg = (reg >> 1) | (R << (AGING_BITS-1));   R = 0
 * Así el bit más significativo indica "usada en el último tic", el siguiente
 * "usada hace 2 tics", etc. El registro más PEQUEÑO es la página más
 * "vieja": esa es la víctima (empate: menor índice de marco).
 * Página recién cargada: registro 0 y R = 1.
 *
 * Variables auxiliares: registros en binario, DESPUÉS del tic.
 */
#include "../algoritmos.h"

/* Escribe los registros como "[10000000,01000000,-]" */
static const char *fmt_registros(char *buf, size_t len, const unsigned reg[],
                                 const int marcos[], int m)
{
    size_t u = (size_t)snprintf(buf, len, "reg=[");
    for (int k = 0; k < m && u < len; k++) {
        if (marcos[k] == MARCO_VACIO) {
            u += (size_t)snprintf(buf + u, len - u, "-");
        } else {
            for (int b = AGING_BITS - 1; b >= 0 && u < len; b--)
                u += (size_t)snprintf(buf + u, len - u, "%c", (reg[k] >> b) & 1u ? '1' : '0');
        }
        if (u < len)
            u += (size_t)snprintf(buf + u, len - u, "%s", (k + 1 < m) ? "," : "]");
    }
    return buf;
}

void simular_aging(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    unsigned reg[MAX_MARCOS] = {0};
    int bit_r[MAX_MARCOS] = {0};
    char buf[AUX_LEN];
    const unsigned mascara = (1u << AGING_BITS) - 1u;

    resultado_iniciar(r, "Aging", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int idx = buscar_pagina(marcos, cfg->marcos, pagina);
        int marco = -1, victima = -1;

        if (idx >= 0) {
            bit_r[idx] = 1;
        } else {
            marco = buscar_libre(marcos, cfg->marcos);
            if (marco < 0) {
                marco = 0;
                for (int k = 1; k < cfg->marcos; k++)
                    if (reg[k] < reg[marco])
                        marco = k;
                victima = marcos[marco];
            }
            marcos[marco] = pagina;
            reg[marco] = 0;
            bit_r[marco] = 1;
        }

        /* Tic de reloj: desplazar e insertar R por la izquierda */
        for (int k = 0; k < cfg->marcos; k++) {
            if (marcos[k] == MARCO_VACIO)
                continue;
            reg[k] = ((reg[k] >> 1) | ((unsigned)bit_r[k] << (AGING_BITS - 1))) & mascara;
            bit_r[k] = 0;
        }

        registrar_paso(r, cfg, i, marcos, marco, victima, "%s",
                       fmt_registros(buf, sizeof buf, reg, marcos, cfg->marcos));
    }
}
