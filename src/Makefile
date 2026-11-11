# Makefile - Simulador de algoritmos de reemplazo de páginas
# Uso (desde src/):
#   make          compila el simulador y la prueba de parámetros
#   make run      compila y ejecuta el simulador completo
#   make test     compila y ejecuta la prueba de parámetros
#   make validar  validación formal completa (Paso 5)
#   make web      compila el motor C a WebAssembly (Paso 7, requiere Emscripten)
#   make web-servir  abre el simulador web en http://localhost:8000
#   make clean    borra los binarios

SHELL   = /bin/bash
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

.PHONY: all run test validar validar-rapido resultados web web-servir clean

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

# Paso 6: datos del informe (trazas, CSV) en ../resultados/
resultados: $(BUILD)/simulador
	bash ../scripts/generar_resultados.sh

# Paso 7: el MISMO código C compilado a WebAssembly para el simulador web.
# Si emcc no está en el PATH, se carga el entorno de ~/emsdk automáticamente.
WEB_DIR = ../web
WEB_SRC = web/api_web.c algoritmos.c $(COMUNES) $(ALGOS)
EMFLAGS = -sMODULARIZE=1 -sEXPORT_NAME=crearMotor -sENVIRONMENT=web,node \
          -sEXPORTED_RUNTIME_METHODS=ccall,cwrap,UTF8ToString
EMSDK_ENV = $(HOME)/emsdk/emsdk_env.sh

web: $(WEB_DIR)/motor.js

$(WEB_DIR)/motor.js: $(WEB_SRC) $(HEADERS)
	@if ! command -v emcc >/dev/null 2>&1; then \
	    if [ -f "$(EMSDK_ENV)" ]; then . "$(EMSDK_ENV)" >/dev/null 2>&1; \
	    else echo "Falta Emscripten: ver docs/PASO_07_simulador_web.md"; exit 1; fi; \
	fi; \
	emcc $(CFLAGS) $(EMFLAGS) -o $@ $(WEB_SRC) && echo "Generado: web/motor.js + web/motor.wasm"

web-servir: web
	@echo "Abre http://localhost:8000 en el navegador (Ctrl+C para detener)"
	python3 -m http.server 8000 --directory $(WEB_DIR)

clean:
	rm -rf $(BUILD)
