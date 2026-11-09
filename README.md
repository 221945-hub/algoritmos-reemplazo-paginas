# Algoritmos de Reemplazo de Páginas: Proyecto de Sistemas Operativos

**Universidad Nacional de San Antonio Abad del Cusco**
Escuela Profesional de Ingeniería Informática y de Sistemas
Curso: Sistemas Operativos | Docente: Ing. Emilio Palomino Olivera | Semestre 2026-II

Simulación en C (Linux/POSIX) de **12 algoritmos de reemplazo de páginas** con **3 marcos** y una cadena fija de **30 referencias**.

## Bitácora de avance

| Paso | Descripción | Estado | Documento |
|---|---|---|---|
| 1 | Fijar los parámetros del experimento | ✅ | [docs/PASO_01_parametros.md](docs/PASO_01_parametros.md) |
| 2 | Preparar el entorno Linux (WSL, gcc, make) | ✅ | [docs/PASO_02_entorno.md](docs/PASO_02_entorno.md) |
| 3 | Estructura modular del código en C | ✅ | [docs/PASO_03_estructura.md](docs/PASO_03_estructura.md) |
| 4 | Implementar los 12 algoritmos | ✅ | [docs/PASO_04_algoritmos.md](docs/PASO_04_algoritmos.md) |
| 5 | Validar resultados | ⏳ | — |
| 6 | Generar trazas, CSV y gráficas | ⏳ | — |
| 7 | Redactar el informe | ⏳ | — |
| 8 | Integración final y entrega | ⏳ | — |

## Estructura del repositorio

```
├── docs/        Documentación de cada paso
└── src/         Código fuente en C (+ Makefile)
```

## Compilar (Linux / WSL)

```bash
cd src
make                  # compila todo en ../build/
make run              # traza de los 12 algoritmos + tabla comparativa
../build/simulador -h # ver todas las opciones (-a, -r, -m, -c, -o, -l)
make test             # prueba de entorno y parámetros
make clean
```

## Integrantes

1. Angel Ismael Alvarez Catunta (221945)
2. *[Por completar]*
3. *[Por completar]*
4. *[Por completar]*
5. *[Por completar]*
6. *[Por completar]*
