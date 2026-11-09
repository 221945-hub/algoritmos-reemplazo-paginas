#!/usr/bin/env bash
# generar_resultados.sh - PASO 6: genera todos los datos del informe
# desde el simulador en C. Ejecutar en Linux/WSL desde cualquier carpeta:
#     bash scripts/generar_resultados.sh        (o: cd src && make resultados)
#
# Salida en resultados/:
#   salida_consola.txt        traza completa de los 12 algoritmos + tabla
#   trazas/NN_nombre.txt      traza individual de cada algoritmo
#   resumen_3marcos.csv       métricas de los 12 algoritmos (experimento oficial)
#   trazas_3marcos.csv        traza paso a paso en formato tabla (12 x 30 filas)
#   curva_marcos.csv          métricas con 1..8 marcos (cadena oficial)
#   belady_tema3.csv          cadena del Tema 3 con 3 y 4 marcos
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SIM="$RAIZ/build/simulador"
OUT="$RAIZ/resultados"
BELADY="1,2,3,4,1,2,5,1,2,3,4,5"
NOMBRES=(fifo optimo lru reloj nru lfu mfu reloj_mejorado aging working_set wsclock aleatorio)

echo "==> Compilando"
make -s -C "$RAIZ/src" all

if ! "$SIM" -r > /dev/null; then
    echo "Error: el simulador no se ejecuta correctamente" >&2
    exit 1
fi

rm -rf "$OUT"
mkdir -p "$OUT/trazas"

echo "==> Traza completa (3 marcos, cadena oficial)"
"$SIM" > "$OUT/salida_consola.txt"

echo "==> Trazas individuales"
for id in $(seq 1 12); do
    archivo=$(printf "%s/trazas/%02d_%s.txt" "$OUT" "$id" "${NOMBRES[$((id - 1))]}")
    "$SIM" -a "$id" > "$archivo"
done

echo "==> CSV del experimento oficial"
"$SIM" -r -o "$OUT/resumen_3marcos.csv" -t "$OUT/trazas_3marcos.csv" > /dev/null

echo "==> Curva de fallos (1..8 marcos)"
tmp="$(mktemp)"
for m in $(seq 1 8); do
    "$SIM" -r -m "$m" -o "$tmp" > /dev/null
    if [ "$m" -eq 1 ]; then
        cat "$tmp" > "$OUT/curva_marcos.csv"
    else
        tail -n +2 "$tmp" >> "$OUT/curva_marcos.csv"
    fi
done

echo "==> Anomalia de Belady (cadena del Tema 3)"
"$SIM" -r -m 3 -c "$BELADY" -o "$tmp" > /dev/null
cat "$tmp" > "$OUT/belady_tema3.csv"
"$SIM" -r -m 4 -c "$BELADY" -o "$tmp" > /dev/null
tail -n +2 "$tmp" >> "$OUT/belady_tema3.csv"
rm -f "$tmp"

echo "==> Listo. Archivos generados en resultados/:"
( cd "$OUT" && find . -type f | sort | sed 's|^\./|    |' )
