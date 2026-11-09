/*
 * aleatorio.c - Algoritmo 12: Aleatorio (Random Replacement, RAND)
 * Responsable: Integrante 6
 *
 * Idea: la víctima se elige al azar entre los marcos ocupados. No usa
 * ninguna información de uso; sirve como referencia de "sin inteligencia".
 *
 * Para que el resultado sea REPRODUCIBLE en cualquier compilador se usa un
 * generador congruencial lineal (LCG) propio en lugar de rand():
 *     x = (1103515245 * x + 12345) mod 2^31,   semilla x0 = RANDOM_SEMILLA
 *     víctima = x mod n_marcos
 * El generador solo avanza cuando hay que reemplazar.
 *
 * Variables auxiliares: valor x generado y marco elegido.
 */
#include <stdint.h>
#include "../algoritmos.h"

static uint32_t lcg_siguiente(uint32_t *x)
{
    *x = (1103515245u * *x + 12345u) & 0x7FFFFFFFu;   /* mod 2^31 */
    return *x;
}

void simular_aleatorio(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    uint32_t x = RANDOM_SEMILLA;

    resultado_iniciar(r, "Aleatorio (RAND)", cfg);
    marcos_vaciar(marcos, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int marco, victima = -1;

        if (buscar_pagina(marcos, cfg->marcos, pagina) >= 0) {
            registrar_paso(r, cfg, i, marcos, -1, -1, "x=%lu", (unsigned long)x);
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            uint32_t v = lcg_siguiente(&x);
            marco = (int)(v % (uint32_t)cfg->marcos);
            victima = marcos[marco];
            marcos[marco] = pagina;
            registrar_paso(r, cfg, i, marcos, marco, victima, "x=%lu -> x mod %d = %d (M%d)",
                           (unsigned long)v, cfg->marcos, marco, marco + 1);
            continue;
        }
        marcos[marco] = pagina;
        registrar_paso(r, cfg, i, marcos, marco, victima, "x=%lu", (unsigned long)x);
    }
}
