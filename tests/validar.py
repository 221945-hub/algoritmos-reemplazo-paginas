#!/usr/bin/env python3
"""
validar.py - Validación formal del simulador (PASO 5)

Uso (desde src/):   make validar
     o directamente: python3 ../tests/validar.py [--rapido]

Grupos de pruebas:
  V1  Compilación limpia (0 advertencias)
  V2  Valores de control del Paso 1
  V3  Traza paso a paso C vs. referencia Python (cadena oficial, 1..8 marcos)
  V4  Invariantes en cada traza (consistencia interna)
  V5  Casos de borde (1 marco, sin repeticiones, una sola página, etc.)
  V6  Pruebas aleatorias diferenciales (cadenas y escrituras al azar)
  V7  Anomalía de Belády y propiedad de pila
  V8  Línea de comandos: errores y códigos de salida
  V9  Reproducibilidad y exportación CSV
Termina con código 0 si todo pasa, 1 si alguna prueba falla.
"""
import os
import random
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import referencia as ref  # noqa: E402

SIM = os.path.join(ref.RAIZ, "build", "simulador")
RAPIDO = "--rapido" in sys.argv
N_ALEATORIAS = 60 if RAPIDO else 400

resultados = []      # (grupo, nombre, ok, detalle)


def prueba(grupo, nombre, ok, detalle=""):
    resultados.append((grupo, nombre, bool(ok), detalle))
    marca = "OK  " if ok else "FALLA"
    print(f"  [{marca}] {grupo} {nombre}" + (f"  -> {detalle}" if (detalle and not ok) else ""))
    return ok


def ejecutar(args):
    p = subprocess.run([SIM] + args, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def lista(v):
    return ",".join(str(x) for x in v)


def parsear(salida):
    """{id: {'trace': [(marcos, 'F'|'H')], 'fallos', 'aciertos', 'esc'}}"""
    res = {}
    bloques = re.split(r"\n ALGORITMO (\d+):", salida)[1:]
    for j in range(0, len(bloques), 2):
        aid, cuerpo = int(bloques[j]), bloques[j + 1]
        traza = []
        for ln in cuerpo.split("\n"):
            m = re.match(r"\s*(\d+) \|\s*(\d+) \|\s*[RW] \|(.*?)\|\s*([FH])\s*\|", ln)
            if m:
                celdas = m.group(3).replace("*", " ").split()
                traza.append((tuple(None if c == "-" else int(c) for c in celdas), m.group(4)))
        mf = re.search(r"Fallos: (\d+) \| Aciertos: (\d+)", cuerpo)
        me = re.search(r"Escrituras a disco: (\d+)", cuerpo)
        res[aid] = {
            "trace": traza,
            "fallos": int(mf.group(1)) if mf else -1,
            "aciertos": int(mf.group(2)) if mf else -1,
            "esc": int(me.group(1)) if me else 0,
        }
    return res


def simular_c(refs, w, m):
    args = ["-m", str(m), "-c", lista(refs)]
    if w is not None:
        args += ["-w", lista(w)]
    code, out, err = ejecutar(args)
    if code != 0:
        raise RuntimeError(f"simulador devolvió {code}: {err.strip()}")
    return parsear(out)


def comparar(refs, w, m):
    """Lista de diferencias entre C y referencia (vacía = idénticos)."""
    c = simular_c(refs, w, m)
    ww = w if w is not None else [0] * len(refs)
    difs = []
    for n, (nombre, f) in enumerate(ref.ALGORITMOS, 1):
        s = f(refs, ww, m)
        py_fallos = sum(1 for _, x in s.trace if x == "F")
        r = c[n]
        if r["trace"] != s.trace:
            paso = next((i + 1 for i, (a, b) in enumerate(zip(r["trace"], s.trace)) if a != b),
                        min(len(r["trace"]), len(s.trace)) + 1)
            difs.append(f"{nombre}: traza distinta desde el paso {paso}")
        elif r["fallos"] != py_fallos or r["esc"] != s.esc:
            difs.append(f"{nombre}: fallos {r['fallos']}/{py_fallos} esc {r['esc']}/{s.esc}")
    return difs, c


def invariantes(refs, m, c, w=None):
    """Comprueba reglas que TODO algoritmo correcto debe cumplir."""
    errores = []
    n, distintas = len(refs), len(set(refs))
    opt = c[2]["fallos"]
    nw = sum(w) if w is not None else 0
    for aid, r in c.items():
        t = r["trace"]
        nombre = ref.ALGORITMOS[aid - 1][0]
        if len(t) != n:
            errores.append(f"{nombre}: {len(t)} pasos en vez de {n}")
            continue
        if r["fallos"] + r["aciertos"] != n:
            errores.append(f"{nombre}: fallos+aciertos != {n}")
        if r["fallos"] != sum(1 for _, x in t if x == "F"):
            errores.append(f"{nombre}: el resumen no coincide con la traza")
        if r["fallos"] < distintas:
            errores.append(f"{nombre}: {r['fallos']} fallos < {distintas} paginas distintas")
        if r["fallos"] < opt:
            errores.append(f"{nombre}: {r['fallos']} fallos < OPT ({opt})")
        if r["esc"] > nw:
            errores.append(f"{nombre}: {r['esc']} escrituras > {nw} accesos W")
        if m >= distintas and r["fallos"] != distintas:
            errores.append(f"{nombre}: con marcos suficientes deberia tener {distintas} fallos")
        if m == 1:
            esperado = 1 + sum(1 for i in range(1, n) if refs[i] != refs[i - 1])
            if r["fallos"] != esperado:
                errores.append(f"{nombre}: con 1 marco esperaba {esperado} fallos")
        prev = (None,) * m
        for i, (marcos, res) in enumerate(t):
            ocupados = [x for x in marcos if x is not None]
            cambios = [k for k in range(m) if marcos[k] != prev[k]]
            if refs[i] not in marcos:
                errores.append(f"{nombre} paso {i+1}: la pagina pedida no quedo en memoria")
            elif len(ocupados) != len(set(ocupados)):
                errores.append(f"{nombre} paso {i+1}: pagina duplicada en marcos")
            elif res == "H" and (cambios or refs[i] not in prev):
                errores.append(f"{nombre} paso {i+1}: acierto que modifica marcos o pagina ausente")
            elif res == "F" and (len(cambios) != 1 or refs[i] in prev):
                errores.append(f"{nombre} paso {i+1}: fallo que no cambia exactamente un marco")
            prev = marcos
            if errores:
                break
    return errores


def cadena_aleatoria(rng):
    n = rng.randint(1, ref.MAX_REFS)
    paginas = rng.randint(1, 10)
    refs = [rng.randrange(paginas) for _ in range(n)]
    w = [1 if rng.random() < rng.choice([0.0, 0.3, 0.6, 1.0]) else 0 for _ in range(n)]
    return refs, w, rng.randint(1, ref.MAX_MARCOS)


def main():
    if not os.path.exists(os.path.join(ref.SRC, "Makefile")):
        print("No se encontró src/Makefile")
        return 1

    # ---------------- V1 ----------------
    print("\nV1. Compilacion limpia")
    p = subprocess.run(["make", "-C", ref.SRC, "-B", "all"], capture_output=True, text=True)
    salida = p.stdout + p.stderr
    adv = [ln for ln in salida.split("\n") if "warning" in ln.lower() or "error" in ln.lower()]
    prueba("V1", "make -B all termina sin errores", p.returncode == 0, salida[-300:])
    prueba("V1", "0 advertencias de gcc (-Wall -Wextra -pedantic)", not adv, "; ".join(adv[:3]))
    if p.returncode != 0:
        return 1

    # ---------------- V2 ----------------
    print("\nV2. Valores de control (Paso 1)")
    code, out, _ = ejecutar([])
    oficial = parsear(out)
    control = {1: 25, 2: 15, 3: 22, 4: 24}
    for aid, esperado in control.items():
        prueba("V2", f"{ref.ALGORITMOS[aid-1][0]} = {esperado} fallos",
               oficial[aid]["fallos"] == esperado, f"obtuvo {oficial[aid]['fallos']}")
    belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    f3 = simular_c(belady, None, 3)[1]["fallos"]
    f4 = simular_c(belady, None, 4)[1]["fallos"]
    prueba("V2", "FIFO Belady (Tema 3): 9 fallos con 3 marcos, 10 con 4", (f3, f4) == (9, 10),
           f"obtuvo {f3} y {f4}")
    prueba("V2", "los 12 algoritmos estan implementados", "PENDIENTE" not in out)

    # ---------------- V3 ----------------
    print("\nV3. Traza C vs. referencia Python (cadena oficial)")
    curva = {}
    for m in range(1, ref.MAX_MARCOS + 1):
        difs, c = comparar(ref.REFS, ref.ESCRITURA, m)
        curva[m] = {aid: r["fallos"] for aid, r in c.items()}
        prueba("V3", f"{m} marco(s): 12 trazas identicas", not difs, "; ".join(difs[:3]))

    # ---------------- V4 ----------------
    print("\nV4. Invariantes en cada traza")
    for m in range(1, ref.MAX_MARCOS + 1):
        c = simular_c(ref.REFS, ref.ESCRITURA, m)
        err = invariantes(ref.REFS, m, c, ref.ESCRITURA)
        prueba("V4", f"cadena oficial, {m} marco(s)", not err, "; ".join(err[:3]))

    # ---------------- V5 ----------------
    print("\nV5. Casos de borde")
    casos = [
        ("una sola referencia", [5], None, 3),
        ("misma pagina 30 veces", [4] * 30, [1] * 30, 3),
        ("sin repeticiones (0..29)", list(range(30)), None, 3),
        ("1 marco, cadena oficial", ref.REFS, ref.ESCRITURA, 1),
        ("marcos = paginas distintas (7)", ref.REFS, ref.ESCRITURA, 7),
        ("maximo de marcos (8)", ref.REFS, ref.ESCRITURA, ref.MAX_MARCOS),
        ("cadena de largo maximo (64)", [i % 9 for i in range(ref.MAX_REFS)], None, 4),
        ("todas escrituras", ref.REFS, [1] * 30, 3),
        ("ciclo 0,1,2,3 (peor caso LRU/FIFO)", [0, 1, 2, 3] * 7, None, 3),
        ("pagina 999 (valor alto)", [999, 1, 999, 2, 3, 999], None, 2),
    ]
    for nombre, refs, w, m in casos:
        difs, c = comparar(refs, w, m)
        err = invariantes(refs, m, c, w)
        prueba("V5", nombre, not difs and not err, "; ".join((difs + err)[:3]))
    c = simular_c(list(range(30)), None, 3)
    prueba("V5", "sin repeticiones: 30 fallos en los 12",
           all(r["fallos"] == 30 for r in c.values()))
    c = simular_c([4] * 30, [1] * 30, 3)
    prueba("V5", "misma pagina: 1 fallo y 0 escrituras en los 12",
           all(r["fallos"] == 1 and r["esc"] == 0 for r in c.values()))
    c = simular_c([0, 1, 2, 3] * 7, None, 3)
    prueba("V5", "ciclo de 4 paginas con 3 marcos: FIFO y LRU fallan siempre (28)",
           c[1]["fallos"] == 28 and c[3]["fallos"] == 28)

    # ---------------- V6 ----------------
    print(f"\nV6. Pruebas aleatorias diferenciales ({N_ALEATORIAS} casos, semilla 2026)")
    rng = random.Random(2026)
    fallidas = []
    for caso in range(N_ALEATORIAS):
        refs, w, m = cadena_aleatoria(rng)
        difs, c = comparar(refs, w, m)
        err = invariantes(refs, m, c, w)
        if difs or err:
            fallidas.append(f"caso {caso}: m={m} refs={lista(refs)} -> {(difs + err)[0]}")
    prueba("V6", f"{N_ALEATORIAS} cadenas al azar: C == referencia e invariantes OK",
           not fallidas, fallidas[0] if fallidas else "")

    # ---------------- V7 ----------------
    print("\nV7. Anomalia de Belady y propiedad de pila")
    print("    Cadena del Tema 3 (1,2,3,4,1,2,5,1,2,3,4,5), todas lecturas:")
    c3, c4 = simular_c(belady, None, 3), simular_c(belady, None, 4)
    tabla_belady = []
    for aid in range(1, 13):
        a, b = c3[aid]["fallos"], c4[aid]["fallos"]
        tabla_belady.append((ref.ALGORITMOS[aid - 1][0], a, b))
        print(f"      {ref.ALGORITMOS[aid-1][0]:<15} 3 marcos={a:>2}  4 marcos={b:>2}"
              f"{'   <- ANOMALIA' if b > a else ''}")
    for aid in (2, 3):
        serie = [curva[m][aid] for m in range(1, ref.MAX_MARCOS + 1)]
        prueba("V7", f"{ref.ALGORITMOS[aid-1][0]} (pila): fallos no aumentan con mas marcos "
               f"(oficial: {serie})", all(x >= y for x, y in zip(serie, serie[1:])))

    # Búsqueda de anomalías en cadenas aleatorias (informativo + pila)
    rng = random.Random(7)
    conteo = {aid: 0 for aid in range(1, 13)}
    ejemplo = {}
    n_busqueda = 150 if RAPIDO else 600
    for _ in range(n_busqueda):
        refs = [rng.randrange(6) for _ in range(rng.randint(8, 24))]
        for m in (2, 3, 4):
            a = simular_c(refs, None, m)
            b = simular_c(refs, None, m + 1)
            for aid in range(1, 13):
                if b[aid]["fallos"] > a[aid]["fallos"]:
                    conteo[aid] += 1
                    ejemplo.setdefault(aid, (refs, m, a[aid]["fallos"], b[aid]["fallos"]))
    print(f"    Busqueda en {n_busqueda} cadenas al azar (m -> m+1, m = 2..4):")
    for aid in range(1, 13):
        ej = ejemplo.get(aid)
        txt = (f"ej: {lista(ej[0])} con {ej[1]}->{ej[1]+1} marcos: {ej[2]}->{ej[3]} fallos"
               if ej else "")
        print(f"      {ref.ALGORITMOS[aid-1][0]:<15} anomalias={conteo[aid]:>4}  {txt}")
    prueba("V7", "OPT y LRU: 0 anomalias en cadenas al azar (son de pila)",
           conteo[2] == 0 and conteo[3] == 0, f"OPT={conteo[2]} LRU={conteo[3]}")
    # La anomalía es rara en cadenas cortas al azar: para FIFO se exige el caso
    # conocido del Tema 3 (determinista) y la búsqueda al azar queda informativa.
    prueba("V7", "FIFO presenta la anomalia en la cadena del Tema 3 (no es de pila)",
           c4[1]["fallos"] > c3[1]["fallos"])

    # ---------------- V8 ----------------
    print("\nV8. Linea de comandos")
    malos = [
        ["-a", "0"], ["-a", "13"], ["-a", "x"], ["-m", "0"], ["-m", str(ref.MAX_MARCOS + 1)],
        ["-c", ""], ["-c", "1,,2"], ["-c", "1,2,"], ["-c", "1,-2"],
        ["-c", lista(range(ref.MAX_REFS + 1))], ["-c", "1,2,3", "-w", "0,1"],
        ["-c", "1,2,3", "-w", "0,2,1"], ["-w", "1"], ["-z"], ["-m"],
    ]
    for args in malos:
        code, _, err = ejecutar(args)
        prueba("V8", f"{' '.join(args) or '(vacio)':<22} -> codigo 2 y mensaje en stderr",
               code == 2 and err.strip() != "", f"codigo {code}")
    code, out, _ = ejecutar(["-h"])
    prueba("V8", "-h muestra la ayuda (codigo 0)", code == 0 and "Uso:" in out)
    code, out, _ = ejecutar(["-l"])
    prueba("V8", "-l lista 12 algoritmos", code == 0 and len(re.findall(r"^\s+\d+ \|", out, re.M)) == 12)
    code, out, _ = ejecutar(["-c", "1,2,3", "-w", "0,1,0", "-a", "1"])
    prueba("V8", "-c con -w valido se acepta", code == 0 and " W " in out)

    # ---------------- V9 ----------------
    print("\nV9. Reproducibilidad y CSV")
    _, o1, _ = ejecutar([])
    _, o2, _ = ejecutar([])
    prueba("V9", "dos ejecuciones dan salida identica (incluye Aleatorio)", o1 == o2)
    with tempfile.TemporaryDirectory() as d:
        ruta = os.path.join(d, "r.csv")
        code, _, _ = ejecutar(["-r", "-o", ruta])
        filas = open(ruta, encoding="utf-8").read().strip().split("\n") if code == 0 else []
        ok = code == 0 and len(filas) == 13
        if ok:
            for fila, aid in zip(filas[1:], range(1, 13)):
                campos = fila.split(",")
                ok &= int(campos[5]) == oficial[aid]["fallos"] and int(campos[9]) == oficial[aid]["esc"]
        prueba("V9", "CSV con 12 filas y valores iguales a la traza", ok)
        code, _, err = ejecutar(["-r", "-o", os.path.join(d, "no_existe", "x.csv")])
        prueba("V9", "CSV a carpeta inexistente -> codigo 1 y error", code == 1 and err.strip() != "")

    # ---------------- Resumen ----------------
    print("\nCurva de fallos con la cadena oficial (marcos 1..8):")
    print("      " + "".join(f"{m:>4}" for m in range(1, ref.MAX_MARCOS + 1)))
    for aid in range(1, 13):
        print(f"      {ref.ALGORITMOS[aid-1][0]:<15}"[:21].ljust(21)
              + "".join(f"{curva[m][aid]:>4}" for m in range(1, ref.MAX_MARCOS + 1)))

    total = len(resultados)
    ok = sum(1 for r in resultados if r[2])
    print("\n" + "=" * 70)
    print(f" RESULTADO: {ok}/{total} pruebas superadas"
          + ("  ->  VALIDACION EXITOSA" if ok == total else "  ->  HAY FALLAS"))
    print("=" * 70)
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
