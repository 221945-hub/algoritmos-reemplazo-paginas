# Makefile - Simulador de algoritmos de reemplazo de páginas
# Uso (desde src/):
#   make          compila el simulador y la prueba de parámetros
#   make run      compila y ejecuta el simulador completo
#   make test     compila y ejecuta la prueba de parámetros
#   make validar  validación formal completa (Paso 5)
#   make clean    borra los binarios

CC      = gcc
CFLAGS  = -std=c11 -Wall -Wextra -pedantic -O2
BUILD   = ../build

# Fuentes
COMUNES = parametros.c comun.c
ALGOS   = $(wildcard algoritmos/*.c)
SIM_SRC = main.c algoritmos.c $(COMUNES) $(ALGOS)
HEADERS = $(wildcard *.h)

# Objetos (se compilan por separado: solo se recompila lo que cambió)
SIM_OBJ = $(patsubst %.c,$(BUILD)/%.o,$(SIM_SRC))

.PHONY: all run test validar validar-rapido clean

all: $(BUILD)/simulador $(BUILD)/test_parametros

$(BUILD)/simulador: $(SIM_OBJ)
	$(CC) $(CFLAGS) -o $@ $^

$(BUILD)/test_parametros: $(BUILD)/test_parametros.o $(BUILD)/parametros.o
	$(CC) $(CFLAGS) -o $@ $^

# Regla genérica: .c -> .o (crea la subcarpeta si hace falta)
$(BUILD)/%.o: %.c $(HEADERS)
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c -o $@ $<

run: $(BUILD)/simulador
	$(BUILD)/simulador

test: $(BUILD)/test_parametros
	$(BUILD)/test_parametros

# Paso 5: validación formal (requiere python3)
validar:
	python3 ../tests/validar.py

validar-rapido:
	python3 ../tests/validar.py --rapido

clean:
	rm -rf $(BUILD)
