/*
 * comun.c - Implementación de utilidades compartidas (PASO 3)
 */
#include <stdarg.h>
#include <string.h>
#include "comun.h"

void marcos_vaciar(int marcos[], int m)
{
    for (int k = 0; k < m; k++)
        marcos[k] = MARCO_VACIO;
}

void resultado_iniciar(Resultado *r, const char *nombre, const Config *cfg)
{
    memset(r, 0, sizeof *r);
    r->nombre = nombre;
    r->implementado = 1;
    r->n = cfg->n;
    r->num_marcos = cfg->marcos;
}

int es_escritura(const Config *cfg, int i)
{
    return cfg->escritura != NULL && cfg->escritura[i] != 0;
}

void registrar_paso(Resultado *r, const Config *cfg, int i, const int marcos[],
                    int marco_cargado, int victima, const char *aux, ...)
{
    Paso *p = &r->pasos[i];

    p->pagina = cfg->refs[i];
    p->es_escritura = es_escritura(cfg, i);
    for (int k = 0; k < cfg->marcos; k++)
        p->marcos[k] = marcos[k];
    p->marco_cargado = marco_cargado;
    p->victima = victima;

    p->aux[0] = '\0';
    if (aux != NULL) {
        va_list args;
        va_start(args, aux);
        vsnprintf(p->aux, sizeof p->aux, aux, args);
        va_end(args);
    }

    if (marco_cargado < 0)
        r->aciertos++;
    else
        r->fallos++;
}

int buscar_pagina(const int marcos[], int m, int pagina)
{
    for (int k = 0; k < m; k++)
        if (marcos[k] == pagina)
            return k;
    return -1;
}

int buscar_libre(const int marcos[], int m)
{
    return buscar_pagina(marcos, m, MARCO_VACIO);
}

const char *fmt_arreglo(char *buf, size_t len, const int v[], int m)
{
    size_t usado = 0;

    if (len == 0)
        return buf;
    buf[0] = '\0';
    usado += (size_t)snprintf(buf + usado, len - usado, "[");
    for (int k = 0; k < m && usado < len; k++) {
        const char *sep = (k + 1 < m) ? "," : "";
        if (v[k] == MARCO_VACIO)
            usado += (size_t)snprintf(buf + usado, len - usado, "-%s", sep);
        else
            usado += (size_t)snprintf(buf + usado, len - usado, "%d%s", v[k], sep);
    }
    if (usado < len)
        snprintf(buf + usado, len - usado, "]");
    return buf;
}

double tasa_fallos(const Resultado *r)
{
    return r->n > 0 ? 100.0 * r->fallos / r->n : 0.0;
}

double tasa_aciertos(const Resultado *r)
{
    return r->n > 0 ? 100.0 * r->aciertos / r->n : 0.0;
}

static void linea(FILE *f, char c, int ancho)
{
    for (int k = 0; k < ancho; k++)
        fputc(c, f);
    fputc('\n', f);
}

void imprimir_traza(FILE *f, const Resultado *r, int id, const char *responsable)
{
    const int ancho = 100;

    fputc('\n', f);
    linea(f, '=', ancho);
    fprintf(f, " ALGORITMO %d: %s   |   Responsable: %s\n", id, r->nombre, responsable);
    fprintf(f, " Marcos: %d   |   Referencias: %d\n", r->num_marcos, r->n);
    linea(f, '=', ancho);

    if (!r->implementado) {
        fprintf(f, " [PENDIENTE] Este modulo aun no esta implementado (Paso 4).\n");
        return;
    }

    /* Encabezado: Paso | Ref | Op | M1 M2 M3 | Res | Sale | Auxiliares */
    fprintf(f, " Paso | Ref | Op |");
    for (int k = 0; k < r->num_marcos; k++)
        fprintf(f, "  M%d ", k + 1);
    fprintf(f, "| Res | Sale | Variables auxiliares\n");
    linea(f, '-', ancho);

    for (int i = 0; i < r->n; i++) {
        const Paso *p = &r->pasos[i];
        fprintf(f, " %4d | %3d |  %c |", i + 1, p->pagina, p->es_escritura ? 'W' : 'R');
        for (int k = 0; k < r->num_marcos; k++) {
            if (p->marcos[k] == MARCO_VACIO)
                fprintf(f, "   - ");
            else
                fprintf(f, " %3d%c", p->marcos[k], k == p->marco_cargado ? '*' : ' ');
        }
        fprintf(f, "|  %c  |", p->marco_cargado < 0 ? 'H' : 'F');
        if (p->victima >= 0)
            fprintf(f, " %4d |", p->victima);
        else
            fprintf(f, "    - |");
        fprintf(f, " %s\n", p->aux);
    }
    linea(f, '-', ancho);
    fprintf(f, " (*) pagina cargada en ese paso   F = fallo de pagina   H = acierto\n");
    imprimir_resumen(f, r);
}

void imprimir_resumen(FILE *f, const Resultado *r)
{
    fprintf(f, " Fallos: %d | Aciertos: %d | Tasa de fallos: %.2f %% | Tasa de aciertos: %.2f %%",
            r->fallos, r->aciertos, tasa_fallos(r), tasa_aciertos(r));
    if (r->escrituras_disco > 0)
        fprintf(f, " | Escrituras a disco: %d", r->escrituras_disco);
    fputc('\n', f);
}
