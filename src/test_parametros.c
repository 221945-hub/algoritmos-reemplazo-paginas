/*
 * test_parametros.c - Prueba del entorno (PASO 2)
 * Comprueba que gcc compila sin advertencias y que los parámetros fijados
 * en el PASO 1 son consistentes. Retorna 0 si todo es correcto.
 */
#include <stdio.h>
#include "parametros.h"

#define MAX_PAGINA 16

static int fallas = 0;

static void verificar(int condicion, const char *descripcion)
{
    printf("  [%s] %s\n", condicion ? " OK " : "FALLA", descripcion);
    if (!condicion)
        fallas++;
}

int main(void)
{
    int escrituras = 0, distintas = 0, rango_ok = 1;
    int frecuencia[MAX_PAGINA] = {0};

    for (int i = 0; i < NUM_REFS; i++) {
        if (REFS[i] < 0 || REFS[i] >= MAX_PAGINA) {
            rango_ok = 0;
            continue;
        }
        frecuencia[REFS[i]]++;
        escrituras += ESCRITURA[i];
    }
    for (int p = 0; p < MAX_PAGINA; p++)
        if (frecuencia[p] > 0)
            distintas++;

    printf("PRUEBA DE ENTORNO Y PARAMETROS\n");
    printf("Compilador: gcc %d.%d.%d | Estandar C: %ld\n\n",
           __GNUC__, __GNUC_MINOR__, __GNUC_PATCHLEVEL__, (long)__STDC_VERSION__);

    printf("Cadena:     ");
    for (int i = 0; i < NUM_REFS; i++)
        printf("%d ", REFS[i]);
    printf("\nEscritura:  ");
    for (int i = 0; i < NUM_REFS; i++)
        printf("%c ", ESCRITURA[i] ? 'W' : 'R');
    printf("\n\nFrecuencia por pagina:\n");
    for (int p = 0; p < MAX_PAGINA; p++)
        if (frecuencia[p] > 0)
            printf("  pagina %d: %d\n", p, frecuencia[p]);

    printf("\nVerificaciones:\n");
    verificar(NUM_MARCOS == 3, "3 marcos fisicos");
    verificar(NUM_REFS == 30, "30 referencias");
    verificar(rango_ok, "paginas dentro de rango");
    verificar(distintas == 7, "7 paginas distintas {0,1,2,3,4,5,7}");
    verificar(frecuencia[0] == 8, "pagina 0 referenciada 8 veces");
    verificar(escrituras == 12, "12 escrituras (40%)");
    verificar(SFIFO_PRIMARIA + SFIFO_SECUNDARIA == NUM_MARCOS,
              "FIFO segmentado: primaria + secundaria = 3 marcos");

    printf("\nResultado: %s (%d fallas)\n", fallas ? "ERROR" : "ENTORNO LISTO", fallas);
    return fallas ? 1 : 0;
}
