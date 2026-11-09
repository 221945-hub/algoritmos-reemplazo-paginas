/*
 * comun.h - Tipos y utilidades compartidas por los 12 algoritmos (PASO 3)
 *
 * Cada algoritmo recibe una Config (cadena, patrón de escrituras, nº de marcos)
 * y llena un Resultado con la traza paso a paso. La impresión y las métricas
 * son comunes, así todos los algoritmos se muestran con el mismo formato.
 */
#ifndef COMUN_H
#define COMUN_H

#include <stdio.h>
#include "parametros.h"

#define MAX_MARCOS  8    /* permite probar con más marcos (Belády)      */
#define MAX_REFS    64   /* permite cadenas personalizadas más largas   */
#define AUX_LEN     96   /* texto de variables auxiliares por paso      */

/* Datos de entrada de una simulación */
typedef struct {
    const int *refs;       /* cadena de referencias                        */
    const int *escritura;  /* 1 = escritura, 0 = lectura (NULL = lecturas) */
    int n;                 /* cantidad de referencias                      */
    int marcos;            /* cantidad de marcos físicos                   */
} Config;

/* Estado registrado en cada paso de la traza */
typedef struct {
    int pagina;                 /* página referenciada                     */
    int es_escritura;           /* tipo de acceso                          */
    int marcos[MAX_MARCOS];     /* contenido de los marcos tras el paso    */
    int marco_cargado;          /* marco donde entró la página, -1 = hit   */
    int victima;                /* página expulsada, -1 si ninguna         */
    char aux[AUX_LEN];          /* variables auxiliares (puntero, bits...) */
} Paso;

/* Resultado completo de un algoritmo */
typedef struct {
    const char *nombre;
    int implementado;           /* 0 = módulo pendiente                    */
    int n;
    int num_marcos;
    int fallos;
    int aciertos;
    int escrituras_disco;       /* páginas sucias escritas al expulsarlas  */
    Paso pasos[MAX_REFS];
} Resultado;

/* ---- Inicialización y registro ---- */
void resultado_iniciar(Resultado *r, const char *nombre, const Config *cfg);
void marcos_vaciar(int marcos[], int m);

/* Registra el paso i. marco_cargado = -1 indica acierto.
 * victima = página expulsada (-1 si se usó un marco libre o fue acierto).
 * aux: texto con formato printf para las variables auxiliares (puede ser NULL). */
void registrar_paso(Resultado *r, const Config *cfg, int i, const int marcos[],
                    int marco_cargado, int victima, const char *aux, ...)
    __attribute__((format(printf, 7, 8)));

/* ---- Búsquedas en los marcos ---- */
int buscar_pagina(const int marcos[], int m, int pagina);  /* índice o -1 */
int buscar_libre(const int marcos[], int m);               /* índice o -1 */
int es_escritura(const Config *cfg, int i);

/* ---- Formato de variables auxiliares ---- */
/* Escribe "[a,b,c]" en buf. Los valores MARCO_VACIO se muestran como '-'. */
const char *fmt_arreglo(char *buf, size_t len, const int v[], int m);

/* ---- Métricas ---- */
double tasa_fallos(const Resultado *r);
double tasa_aciertos(const Resultado *r);

/* ---- Salida ---- */
void imprimir_traza(FILE *f, const Resultado *r, int id, const char *responsable);
void imprimir_resumen(FILE *f, const Resultado *r);

#endif /* COMUN_H */
