/*
 * api_web.c - Interfaz entre la página web y el motor en C (PASO 7)
 *
 * Se compila con Emscripten a WebAssembly junto con los MISMOS módulos que
 * usa el simulador de consola (comun.c, algoritmos.c, los 12 archivos de
 * src/algoritmos/ y parametros.c). La lógica de los 12 algoritmos NO se duplica en JavaScript.
 *
 * Uso desde JavaScript:
 *   1. web_fijar_ref(i, pagina) y web_fijar_escritura(i, 0|1)  para i = 0..n-1
 *   2. web_simular(id, n, marcos)          -> fallos, o -1 si los datos son inválidos
 *   3. web_marco(paso, k), web_marco_cargado(paso), web_victima(paso),
 *      web_aux(paso), web_fallos(), web_escrituras() ...  para leer la traza
 *
 * También compila con gcc (sin Emscripten), lo que permite probarla en Linux.
 */
#include "../algoritmos.h"

#ifdef __EMSCRIPTEN__
#include <emscripten/emscripten.h>
#define EXPORTAR EMSCRIPTEN_KEEPALIVE
#else
#define EXPORTAR
#endif

static int refs[MAX_REFS];
static int escrituras[MAX_REFS];
static Resultado resultado;
static int hay_resultado = 0;

/* Paso válido del último resultado */
static int paso_valido(int paso)
{
    return hay_resultado && paso >= 0 && paso < resultado.n;
}

/* ---------------- Información general ---------------- */

EXPORTAR int web_num_algoritmos(void) { return NUM_ALGORITMOS; }
EXPORTAR int web_max_marcos(void)     { return MAX_MARCOS; }
EXPORTAR int web_max_refs(void)       { return MAX_REFS; }
EXPORTAR int web_marcos_oficial(void) { return NUM_MARCOS; }
EXPORTAR int web_num_refs_oficial(void) { return NUM_REFS; }

EXPORTAR int web_ref_oficial(int i)
{
    return (i >= 0 && i < NUM_REFS) ? REFS[i] : -1;
}

EXPORTAR int web_escritura_oficial(int i)
{
    return (i >= 0 && i < NUM_REFS) ? ESCRITURA[i] : 0;
}

EXPORTAR const char *web_nombre_algoritmo(int id)
{
    return (id >= 1 && id <= NUM_ALGORITMOS) ? ALGORITMOS[id - 1].nombre : "";
}

EXPORTAR const char *web_responsable(int id)
{
    return (id >= 1 && id <= NUM_ALGORITMOS) ? ALGORITMOS[id - 1].responsable : "";
}

/* ---------------- Entrada ---------------- */

EXPORTAR void web_fijar_ref(int i, int pagina)
{
    if (i >= 0 && i < MAX_REFS)
        refs[i] = pagina;
}

EXPORTAR void web_fijar_escritura(int i, int es_escritura)
{
    if (i >= 0 && i < MAX_REFS)
        escrituras[i] = es_escritura ? 1 : 0;
}

/* Ejecuta el algoritmo 'id' (1..12). Devuelve los fallos o -1 si hay error. */
EXPORTAR int web_simular(int id, int n, int marcos)
{
    Config cfg;

    hay_resultado = 0;
    if (id < 1 || id > NUM_ALGORITMOS || n < 1 || n > MAX_REFS ||
        marcos < 1 || marcos > MAX_MARCOS)
        return -1;
    for (int i = 0; i < n; i++)
        if (refs[i] < 0 || refs[i] > 999)
            return -1;

    cfg.refs = refs;
    cfg.escritura = escrituras;
    cfg.n = n;
    cfg.marcos = marcos;
    ALGORITMOS[id - 1].simular(&cfg, &resultado);
    hay_resultado = resultado.implementado;
    return hay_resultado ? resultado.fallos : -1;
}

/* ---------------- Resultado del último algoritmo simulado ---------------- */

EXPORTAR int web_fallos(void)     { return hay_resultado ? resultado.fallos : -1; }
EXPORTAR int web_aciertos(void)   { return hay_resultado ? resultado.aciertos : -1; }
EXPORTAR int web_escrituras(void) { return hay_resultado ? resultado.escrituras_disco : -1; }
EXPORTAR int web_num_pasos(void)  { return hay_resultado ? resultado.n : 0; }

EXPORTAR int web_pagina(int paso)
{
    return paso_valido(paso) ? resultado.pasos[paso].pagina : -1;
}

EXPORTAR int web_es_escritura(int paso)
{
    return paso_valido(paso) ? resultado.pasos[paso].es_escritura : 0;
}

/* Contenido del marco k después del paso (MARCO_VACIO = -1) */
EXPORTAR int web_marco(int paso, int k)
{
    if (!paso_valido(paso) || k < 0 || k >= resultado.num_marcos)
        return MARCO_VACIO;
    return resultado.pasos[paso].marcos[k];
}

/* Marco donde se cargó la página (-1 = acierto) */
EXPORTAR int web_marco_cargado(int paso)
{
    return paso_valido(paso) ? resultado.pasos[paso].marco_cargado : -1;
}

/* Página expulsada (-1 = ninguna) */
EXPORTAR int web_victima(int paso)
{
    return paso_valido(paso) ? resultado.pasos[paso].victima : -1;
}

/* Texto de variables auxiliares (puntero, bits R/M, contadores...) */
EXPORTAR const char *web_aux(int paso)
{
    return paso_valido(paso) ? resultado.pasos[paso].aux : "";
}
