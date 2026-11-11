/*
 * main.c - Programa principal del simulador (PASO 3)
 *
 * Uso:
 *   ./simulador                 traza de los 12 algoritmos + tabla comparativa
 *   ./simulador -a 1            solo el algoritmo 1 (se puede repetir: -a 1 -a 3)
 *   ./simulador -r              solo la tabla comparativa (sin trazas)
 *   ./simulador -m 4            usar 4 marcos (1..MAX_MARCOS)
 *   ./simulador -c 1,2,3,4,1    cadena personalizada (todas lecturas)
 *   ./simulador -c 1,2,3 -w 0,1,0   patrón de escrituras propio (1 = W)
 *   ./simulador -o salida.csv   exportar resultados a CSV
 *   ./simulador -t trazas.csv   exportar la traza paso a paso a CSV
 *   ./simulador -l              listar algoritmos
 *   ./simulador -h              ayuda
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "algoritmos.h"

static Resultado resultados[NUM_ALGORITMOS];   /* static: evita usar mucha pila */

static void ayuda(const char *prog)
{
    printf("Uso: %s [opciones]\n"
           "  -a N        ejecutar solo el algoritmo N (1..%d), repetible\n"
           "  -r          mostrar solo la tabla comparativa\n"
           "  -m M        numero de marcos (1..%d, por defecto %d)\n"
           "  -c LISTA    cadena personalizada, ej: 1,2,3,4,1,2,5\n"
           "  -w LISTA    patron de escrituras (0=R, 1=W), mismo largo que la cadena\n"
           "  -o ARCHIVO  exportar resultados a CSV\n"
           "  -t ARCHIVO  exportar la traza paso a paso a CSV\n"
           "  -l          listar algoritmos\n"
           "  -h          esta ayuda\n",
           prog, NUM_ALGORITMOS, MAX_MARCOS, NUM_MARCOS);
}

static void listar(void)
{
    printf(" Nro | Algoritmo          | Responsable\n");
    printf("-----+--------------------+--------------------\n");
    for (int k = 0; k < NUM_ALGORITMOS; k++)
        printf(" %3d | %-18s | %s\n", ALGORITMOS[k].id, ALGORITMOS[k].nombre,
               ALGORITMOS[k].responsable);
}

/* Convierte "1,2,3" en un arreglo. Devuelve la cantidad o -1 si es inválida. */
static int parsear_cadena(const char *texto, int destino[], int max)
{
    int n = 0;
    const char *p = texto;

    while (*p != '\0') {
        char *fin;
        long v = strtol(p, &fin, 10);
        if (fin == p || v < 0 || v > 999 || n >= max)
            return -1;
        destino[n++] = (int)v;
        p = fin;
        if (*p == ',') {
            p++;
            if (*p == '\0')        /* coma final: "1,2," es inválida */
                return -1;
        } else if (*p != '\0') {
            return -1;
        }
    }
    return n > 0 ? n : -1;
}

static int leer_entero(const char *texto, int min, int max, int *valor)
{
    char *fin;
    long v = strtol(texto, &fin, 10);
    if (*texto == '\0' || *fin != '\0' || v < min || v > max)
        return 0;
    *valor = (int)v;
    return 1;
}

static void imprimir_cadena(const Config *cfg)
{
    printf(" Cadena (%d refs): ", cfg->n);
    for (int i = 0; i < cfg->n; i++)
        printf("%d ", cfg->refs[i]);
    printf("\n Operacion:       ");
    for (int i = 0; i < cfg->n; i++)
        printf("%c ", es_escritura(cfg, i) ? 'W' : 'R');
    printf("\n");
}

static void tabla_comparativa(const int seleccion[])
{
    printf("\n");
    printf("================================================================================================\n");
    printf("                     TABLA COMPARATIVA DE ALGORITMOS DE REEMPLAZO\n");
    printf("================================================================================================\n");
    printf(" Nro | %-18s | %-18s | Fallos | Aciertos | %% Fallos | %% Aciertos | Escr.\n",
           "Algoritmo", "Responsable");
    printf("-----+--------------------+--------------------+--------+----------+----------+------------+------\n");
    for (int k = 0; k < NUM_ALGORITMOS; k++) {
        const Resultado *r = &resultados[k];
        if (!seleccion[k])
            continue;
        if (!r->implementado) {
            printf(" %3d | %-18s | %-18s | %s\n", ALGORITMOS[k].id, ALGORITMOS[k].nombre,
                   ALGORITMOS[k].responsable, "PENDIENTE (Paso 4)");
            continue;
        }
        printf(" %3d | %-18s | %-18s | %6d | %8d | %7.2f%% | %9.2f%% | %4d\n",
               ALGORITMOS[k].id, ALGORITMOS[k].nombre, ALGORITMOS[k].responsable,
               r->fallos, r->aciertos, tasa_fallos(r), tasa_aciertos(r), r->escrituras_disco);
    }
    printf("================================================================================================\n");
}

/* Una fila por paso y algoritmo: sirve para armar las tablas del informe */
static int exportar_trazas_csv(const char *ruta, const int seleccion[], const Config *cfg)
{
    FILE *fp = fopen(ruta, "w");
    if (fp == NULL) {
        perror(ruta);
        return 0;
    }
    fprintf(fp, "ID,Algoritmo,Paso,Pagina,Operacion");
    for (int k = 0; k < cfg->marcos; k++)
        fprintf(fp, ",M%d", k + 1);
    fprintf(fp, ",Resultado,Victima,Auxiliar\n");

    for (int a = 0; a < NUM_ALGORITMOS; a++) {
        const Resultado *r = &resultados[a];
        if (!seleccion[a] || !r->implementado)
            continue;
        for (int i = 0; i < r->n; i++) {
            const Paso *p = &r->pasos[i];
            fprintf(fp, "%d,\"%s\",%d,%d,%c", ALGORITMOS[a].id, ALGORITMOS[a].nombre,
                    i + 1, p->pagina, p->es_escritura ? 'W' : 'R');
            for (int k = 0; k < cfg->marcos; k++) {
                if (p->marcos[k] == MARCO_VACIO)
                    fprintf(fp, ",-");
                else
                    fprintf(fp, ",%d", p->marcos[k]);
            }
            fprintf(fp, ",%c,", p->marco_cargado < 0 ? 'H' : 'F');
            if (p->victima >= 0)
                fprintf(fp, "%d", p->victima);
            else
                fprintf(fp, "-");
            fprintf(fp, ",\"%s\"\n", p->aux);   /* aux nunca contiene comillas */
        }
    }
    fclose(fp);
    printf(" Trazas exportadas a: %s\n", ruta);
    return 1;
}

static int exportar_csv(const char *ruta, const int seleccion[], const Config *cfg)
{
    FILE *fp = fopen(ruta, "w");
    if (fp == NULL) {
        perror(ruta);
        return 0;
    }
    fprintf(fp, "ID,Algoritmo,Responsable,Marcos,Referencias,Fallos,Aciertos,"
                "Tasa_Fallos_Pct,Tasa_Aciertos_Pct,Escrituras_Disco\n");
    for (int k = 0; k < NUM_ALGORITMOS; k++) {
        const Resultado *r = &resultados[k];
        if (!seleccion[k] || !r->implementado)
            continue;
        fprintf(fp, "%d,\"%s\",\"%s\",%d,%d,%d,%d,%.2f,%.2f,%d\n",
                ALGORITMOS[k].id, ALGORITMOS[k].nombre, ALGORITMOS[k].responsable,
                cfg->marcos, cfg->n, r->fallos, r->aciertos,
                tasa_fallos(r), tasa_aciertos(r), r->escrituras_disco);
    }
    fclose(fp);
    printf(" Resultados exportados a: %s\n", ruta);
    return 1;
}

int main(int argc, char *argv[])
{
    int seleccion[NUM_ALGORITMOS] = {0};
    int alguno_elegido = 0;
    int solo_resumen = 0;
    const char *ruta_csv = NULL;
    const char *ruta_trazas = NULL;
    int cadena_propia[MAX_REFS];
    int escritura_propia[MAX_REFS];
    const char *texto_w = NULL;
    Config cfg = { REFS, ESCRITURA, NUM_REFS, NUM_MARCOS };

    for (int a = 1; a < argc; a++) {
        const char *op = argv[a];
        int necesita_valor = (strcmp(op, "-a") == 0 || strcmp(op, "-m") == 0 ||
                              strcmp(op, "-c") == 0 || strcmp(op, "-o") == 0 ||
                              strcmp(op, "-w") == 0 || strcmp(op, "-t") == 0);
        const char *valor = NULL;

        if (necesita_valor) {
            if (a + 1 >= argc) {
                fprintf(stderr, "Error: la opcion %s necesita un valor\n", op);
                return 2;
            }
            valor = argv[++a];
        }

        if (strcmp(op, "-h") == 0) {
            ayuda(argv[0]);
            return 0;
        } else if (strcmp(op, "-l") == 0) {
            listar();
            return 0;
        } else if (strcmp(op, "-r") == 0) {
            solo_resumen = 1;
        } else if (strcmp(op, "-a") == 0) {
            int id;
            if (!leer_entero(valor, 1, NUM_ALGORITMOS, &id)) {
                fprintf(stderr, "Error: algoritmo invalido '%s' (1..%d)\n", valor, NUM_ALGORITMOS);
                return 2;
            }
            seleccion[id - 1] = 1;
            alguno_elegido = 1;
        } else if (strcmp(op, "-m") == 0) {
            if (!leer_entero(valor, 1, MAX_MARCOS, &cfg.marcos)) {
                fprintf(stderr, "Error: marcos invalidos '%s' (1..%d)\n", valor, MAX_MARCOS);
                return 2;
            }
        } else if (strcmp(op, "-c") == 0) {
            int n = parsear_cadena(valor, cadena_propia, MAX_REFS);
            if (n < 0) {
                fprintf(stderr, "Error: cadena invalida '%s' (max %d paginas, ej: 1,2,3)\n",
                        valor, MAX_REFS);
                return 2;
            }
            cfg.refs = cadena_propia;
            cfg.escritura = NULL;      /* cadena propia: todas lecturas */
            cfg.n = n;
        } else if (strcmp(op, "-w") == 0) {
            texto_w = valor;           /* se valida al final: depende de -c */
        } else if (strcmp(op, "-t") == 0) {
            ruta_trazas = valor;
        } else if (strcmp(op, "-o") == 0) {
            ruta_csv = valor;
        } else {
            fprintf(stderr, "Opcion desconocida: %s\n", op);
            ayuda(argv[0]);
            return 2;
        }
    }

    if (texto_w != NULL) {
        int n = parsear_cadena(texto_w, escritura_propia, MAX_REFS);
        int valido = (n == cfg.n);
        for (int i = 0; valido && i < n; i++)
            if (escritura_propia[i] != 0 && escritura_propia[i] != 1)
                valido = 0;
        if (!valido) {
            fprintf(stderr, "Error: patron de escrituras invalido '%s' "
                            "(solo 0/1 y %d valores, igual que la cadena)\n", texto_w, cfg.n);
            return 2;
        }
        cfg.escritura = escritura_propia;
    }

    if (!alguno_elegido)
        for (int k = 0; k < NUM_ALGORITMOS; k++)
            seleccion[k] = 1;

    printf("****************************************************************************************************\n");
    printf("*             SIMULADOR DE ALGORITMOS DE REEMPLAZO DE PAGINAS - Sistemas Operativos UNSAAC         *\n");
    printf("****************************************************************************************************\n");
    printf(" Marcos: %d\n", cfg.marcos);
    imprimir_cadena(&cfg);

    for (int k = 0; k < NUM_ALGORITMOS; k++) {
        if (!seleccion[k])
            continue;
        ALGORITMOS[k].simular(&cfg, &resultados[k]);
        if (!solo_resumen)
            imprimir_traza(stdout, &resultados[k], ALGORITMOS[k].id, ALGORITMOS[k].responsable);
    }

    tabla_comparativa(seleccion);

    if (ruta_trazas != NULL && !exportar_trazas_csv(ruta_trazas, seleccion, &cfg))
        return 1;
    if (ruta_csv != NULL && !exportar_csv(ruta_csv, seleccion, &cfg))
        return 1;
    return 0;
}
