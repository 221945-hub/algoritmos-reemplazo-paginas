# Makefile - Simulador de algoritmos de reemplazo de páginas
# Uso (desde src/):
#   make          compila todo
#   make test     compila y ejecuta la prueba de parámetros
#   make clean    borra los binarios

CC      = gcc
CFLAGS  = -std=c11 -Wall -Wextra -pedantic -O2
BUILD   = ../build

# Módulos comunes (se irán agregando en los pasos 3 y 4)
COMUNES = parametros.c

.PHONY: all test clean

all: $(BUILD)/test_parametros

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/test_parametros: test_parametros.c $(COMUNES) parametros.h | $(BUILD)
	$(CC) $(CFLAGS) -o $@ test_parametros.c $(COMUNES)

test: $(BUILD)/test_parametros
	$(BUILD)/test_parametros

clean:
	rm -rf $(BUILD)
