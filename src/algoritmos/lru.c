/*
 * lru.c - Algoritmo 3: LRU (Least Recently Used)
 * Responsable: Integrante 3 (Jhamil Huahualuque)
 *
 * Idea: se expulsa la página que lleva MÁS TIEMPO sin usarse.
 * Implementación con "contador/marca de tiempo" (Silberschatz): cada marco
 * guarda el paso de su último uso; la víctima es la marca más pequeña.
 * Es un algoritmo de pila: no sufre la anomalía de Belády.
 *
 * Variables auxiliares: ult = paso (base 1) del último uso de cada marco.
 */
#include "../algoritmos.h"

void simular_lru(const Config *cfg, Resultado *r)
{
    int marcos[MAX_MARCOS];
    int ultimo[MAX_MARCOS];     /* paso del último uso, base 1 */
    char buf[AUX_LEN];

    resultado_iniciar(r, "LRU", cfg);
    marcos_vaciar(marcos, cfg->marcos);
    marcos_vaciar(ultimo, cfg->marcos);

    for (int i = 0; i < cfg->n; i++) {
        int pagina = cfg->refs[i];
        int idx = buscar_pagina(marcos, cfg->marcos, pagina);
        int marco, victima = -1;

        if (idx >= 0) {
            ultimo[idx] = i + 1;
            registrar_paso(r, cfg, i, marcos, -1, -1, "ult=%s",
                           fmt_arreglo(buf, sizeof buf, ultimo, cfg->marcos));
            continue;
        }

        marco = buscar_libre(marcos, cfg->marcos);
        if (marco < 0) {
            marco = 0;
            for (int k = 1; k < cfg->marcos; k++)
                if (ultimo[k] < ultimo[marco])
                    marco = k;
            victima = marcos[marco];
        }
        marcos[marco] = pagina;
        ultimo[marco] = i + 1;
        registrar_paso(r, cfg, i, marcos, marco, victima, "ult=%s",
                       fmt_arreglo(buf, sizeof buf, ultimo, cfg->marcos));
    }
}
