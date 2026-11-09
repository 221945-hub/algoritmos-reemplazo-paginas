# PASO 2: Preparar el entorno Linux (WSL + gcc + make)

> **Estado:** ✅ Completado
> **Archivos generados:** `docs/PASO_02_entorno.md`, `src/Makefile`, `src/test_parametros.c`, `.gitattributes`

## Objetivo

Tener un entorno **Linux/POSIX** donde el código C compile con `gcc` **sin advertencias**, como pide el enunciado (`gcc -Wall -O2`). También hay que comprobar que los parámetros del Paso 1 se leen bien desde C.

---

## 2.1 Entorno verificado

| Componente | Versión | Estado |
|---|---|---|
| Sistema anfitrión | Windows 11 Home 10.0.26200 | — |
| WSL | Versión 2 | ✅ |
| Distribución | Ubuntu 26.04.1 LTS | ✅ |
| Compilador | **gcc 15.2.0** | ✅ ya instalado |
| Herramienta de construcción | **GNU Make 4.4.1** | ✅ ya instalado |
| Control de versiones | git 2.53.0 (WSL) / 2.55.0 (Windows) | ✅ |
| Depurador `gdb` | — | ⚪ opcional, no instalado |
| `valgrind` (fugas de memoria) | — | ⚪ opcional, no instalado |

## 2.2 Instalación (para los demás integrantes)

Cada integrante repite estos pasos en su PC.

**1. Instalar WSL con Ubuntu** (PowerShell como administrador, solo la primera vez):
```powershell
wsl --install -d Ubuntu
```
Reinicia la PC y crea tu usuario y contraseña de Linux.

**2. Instalar las herramientas de compilación** (dentro de Ubuntu):
```bash
sudo apt update
sudo apt install -y build-essential git
# Opcionales, para depurar:
sudo apt install -y gdb valgrind
```

**3. Verificar:**
```bash
gcc --version     # debe mostrar gcc 11 o superior
make --version
```

**4. Clonar el repositorio.** Es recomendable hacerlo en el *home* de Linux, porque compila más rápido que en `/mnt/c`:
```bash
cd ~
git clone https://github.com/221945-hub/algoritmos-reemplazo-paginas.git
cd algoritmos-reemplazo-paginas/src
```
> El repositorio es privado. Para clonarlo, el dueño debe invitarte como colaborador en GitHub (Settings → Collaborators).

## 2.3 Opciones de compilación elegidas

```make
CFLAGS = -std=c11 -Wall -Wextra -pedantic -O2
```

| Opción | Para qué sirve |
|---|---|
| `-std=c11` | Usa C estándar ISO 2011. Permite declarar variables dentro de `for` y es portable a cualquier Linux. |
| `-Wall` | Activa las advertencias principales. Lo exige el enunciado. |
| `-Wextra` | Agrega advertencias adicionales, como parámetros sin usar o comparaciones con signo. |
| `-pedantic` | Rechaza extensiones propias de GNU, para que el código sea C estándar puro. |
| `-O2` | Optimización de nivel 2. Lo exige el enunciado. |

**Regla del proyecto:** ningún módulo se sube a GitHub si compila con advertencias.

## 2.4 Fin de línea LF (`.gitattributes`)

Windows guarda los archivos con fin de línea **CRLF** y Linux con **LF**. Un `Makefile` con CRLF puede fallar en WSL. Por eso se agregó `.gitattributes`:
```
* text=auto eol=lf
```
Con esto, git guarda y entrega siempre LF, sin importar desde qué sistema se edite.

## 2.5 Makefile

Ubicación: `src/Makefile`. Los binarios se generan en `build/`, que está excluido en `.gitignore`.

| Comando (desde `src/`) | Acción |
|---|---|
| `make` | Compila todo |
| `make test` | Compila y ejecuta la prueba de parámetros |
| `make clean` | Borra la carpeta `build/` |

En los Pasos 3 y 4 se agregarán los módulos de cada algoritmo y el ejecutable `simulador`.

## 2.6 Prueba de entorno: `test_parametros.c`

Es un programa corto que **enlaza** `parametros.c`. Comprueba que la cadena y el patrón de escrituras del Paso 1 son consistentes: 3 marcos, 30 referencias, 7 páginas distintas, la página 0 aparece 8 veces y hay 12 escrituras. Devuelve `0` si todo está bien, así que se puede usar en scripts.

**Ejecución real en WSL (2026-11-06):**
```
$ make clean && make test
rm -rf ../build
mkdir -p ../build
gcc -std=c11 -Wall -Wextra -pedantic -O2 -o ../build/test_parametros test_parametros.c parametros.c
../build/test_parametros
PRUEBA DE ENTORNO Y PARAMETROS
Compilador: gcc 15.2.0 | Estandar C: 201112

Cadena:     7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1 3 5 2 0 1 4 2 3 0 1
Escritura:  R W R R W R R W W R W R R R W R R R W R W R W W R R R W W R

Frecuencia por pagina:
  pagina 0: 8
  pagina 1: 6
  pagina 2: 6
  pagina 3: 5
  pagina 4: 2
  pagina 5: 1
  pagina 7: 2

Verificaciones:
  [ OK ] 3 marcos fisicos
  [ OK ] 30 referencias
  [ OK ] paginas dentro de rango
  [ OK ] 7 paginas distintas {0,1,2,3,4,5,7}
  [ OK ] pagina 0 referenciada 8 veces
  [ OK ] 12 escrituras (40%)
  [ OK ] periodo de reloj y ventanas tau definidos

Resultado: ENTORNO LISTO (0 fallas)
```

✅ **0 advertencias del compilador y 0 fallas en las verificaciones.**

## 2.7 Problemas comunes

| Síntoma | Causa | Solución |
|---|---|---|
| `make: *** missing separator` | El Makefile tiene espacios en lugar de **TAB** o tiene CRLF | Usar TAB en las recetas. `.gitattributes` ya fuerza LF. |
| `gcc: command not found` | Falta `build-essential` | `sudo apt install build-essential` |
| `/bin/bash^M: bad interpreter` | El script tiene CRLF | `sed -i 's/\r$//' archivo.sh` |
| Compila muy lento | El proyecto está en `/mnt/c/...` (OneDrive) | Clonar en `~/` dentro de Linux |
| `Permission denied` al clonar | El repositorio es privado | Pedir la invitación de colaborador |

---

**Siguiente paso:** PASO 3. Estructura modular del código en C (`comun.h`, interfaz común de los algoritmos, impresión de la traza y `main.c` con menú).
