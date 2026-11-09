"""
referencia.py - Implementación de REFERENCIA (independiente del código C)
de los 12 algoritmos, escrita desde las reglas de docs/PASO_01_parametros.md.

Los parámetros (cadena, escrituras, periodo de reloj, tau, semilla, bits)
se leen directamente de src/parametros.h y src/parametros.c, para que la
referencia y el simulador usen siempre los mismos valores.

Cada función recibe (refs, w, m) y devuelve un objeto Sim con:
    trace : lista de (tupla_de_marcos, 'F' | 'H') por paso
    esc   : escrituras a disco
"""
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "src")


def _leer(nombre):
    with open(os.path.join(SRC, nombre), encoding="utf-8") as f:
        return f.read()


def _define(texto, nombre):
    m = re.search(r"#define\s+%s\s+\(?(-?\d+)u?\)?" % nombre, texto)
    if not m:
        raise ValueError("No se encontró #define " + nombre)
    return int(m.group(1))


def _arreglo(texto, nombre):
    m = re.search(r"%s\s*\[[^\]]*\]\s*=\s*\{([^}]*)\}" % nombre, texto)
    if not m:
        raise ValueError("No se encontró el arreglo " + nombre)
    return [int(x) for x in m.group(1).replace("\n", " ").split(",") if x.strip()]


_H = _leer("parametros.h")
_C = _leer("parametros.c")
_COMUN = _leer("comun.h")

REFS = _arreglo(_C, "REFS")
ESCRITURA = _arreglo(_C, "ESCRITURA")
NUM_MARCOS = _define(_H, "NUM_MARCOS")
PERIODO = _define(_H, "PERIODO_RELOJ")
WS_TAU = _define(_H, "WS_TAU")
WSCLOCK_TAU = _define(_H, "WSCLOCK_TAU")
SEMILLA = _define(_H, "RANDOM_SEMILLA")
AGING_BITS = _define(_H, "AGING_BITS")
MAX_MARCOS = _define(_COMUN, "MAX_MARCOS")
MAX_REFS = _define(_COMUN, "MAX_REFS")


class Sim:
    """Estado común: marcos, bit sucio genérico y traza."""

    def __init__(self, refs, w, m):
        self.refs, self.w, self.m = refs, w, m
        self.f = [None] * m
        self.dirty = [0] * m
        self.esc = 0
        self.trace = []

    def libre(self):
        return self.f.index(None) if None in self.f else -1

    def hit(self, i):
        k = self.f.index(self.refs[i])
        if self.w[i]:
            self.dirty[k] = 1
        self.trace.append((tuple(self.f), "H"))

    def load(self, i, k, expulsa):
        if expulsa and self.dirty[k]:
            self.esc += 1
        self.f[k] = self.refs[i]
        self.dirty[k] = self.w[i]
        self.trace.append((tuple(self.f), "F"))

    def escribir(self, k):          # escritura programada (WSClock)
        if self.dirty[k]:
            self.esc += 1
            self.dirty[k] = 0


def fifo(refs, w, m):
    s, p = Sim(refs, w, m), 0
    for i, pg in enumerate(refs):
        if pg in s.f:
            s.hit(i)
            continue
        k = s.libre()
        if k < 0:
            k, p = p, (p + 1) % m
            s.load(i, k, True)
        else:
            s.load(i, k, False)
    return s


def optimo(refs, w, m):
    s = Sim(refs, w, m)

    def proximo(pg, i):
        for j in range(i + 1, len(refs)):
            if refs[j] == pg:
                return j
        return 10 ** 9

    for i, pg in enumerate(refs):
        if pg in s.f:
            s.hit(i)
            continue
        k = s.libre()
        if k < 0:
            mejor = -1
            for c in range(m):
                d = proximo(s.f[c], i)
                if d > mejor:
                    mejor, k = d, c
            s.load(i, k, True)
        else:
            s.load(i, k, False)
    return s


def lru(refs, w, m):
    s, u = Sim(refs, w, m), [0] * m
    for i, pg in enumerate(refs):
        if pg in s.f:
            u[s.f.index(pg)] = i
            s.hit(i)
            continue
        k = s.libre()
        ev = k < 0
        if ev:
            k = min(range(m), key=lambda c: (u[c], c))
        s.load(i, k, ev)
        u[k] = i
    return s


def reloj(refs, w, m):
    s, r, p = Sim(refs, w, m), [0] * m, 0
    for i, pg in enumerate(refs):
        if pg in s.f:
            r[s.f.index(pg)] = 1
            s.hit(i)
            continue
        k = s.libre()
        ev = k < 0
        if ev:
            while r[p]:
                r[p] = 0
                p = (p + 1) % m
            k, p = p, (p + 1) % m
        s.load(i, k, ev)
        r[k] = 1
    return s


def nru(refs, w, m):
    s = Sim(refs, w, m)
    r, mm, lleg = [0] * m, [0] * m, [0] * m
    for i, pg in enumerate(refs):
        if i > 0 and i % PERIODO == 0:
            r = [0] * m
        if pg in s.f:
            k = s.f.index(pg)
            r[k] = 1
            mm[k] |= w[i]
            s.hit(i)
            continue
        k = s.libre()
        ev = k < 0
        if ev:
            k = min(range(m), key=lambda c: (2 * r[c] + mm[c], lleg[c], c))
        s.load(i, k, ev)
        r[k], mm[k], lleg[k] = 1, w[i], i
    return s


def _frecuencia(refs, w, m, mayor):
    s, fr, lleg = Sim(refs, w, m), [0] * m, [0] * m
    for i, pg in enumerate(refs):
        if pg in s.f:
            fr[s.f.index(pg)] += 1
            s.hit(i)
            continue
        k = s.libre()
        ev = k < 0
        if ev:
            k = min(range(m), key=lambda c: ((-fr[c] if mayor else fr[c]), lleg[c], c))
        s.load(i, k, ev)
        fr[k], lleg[k] = 1, i
    return s


def lfu(refs, w, m):
    return _frecuencia(refs, w, m, False)


def mfu(refs, w, m):
    return _frecuencia(refs, w, m, True)


def reloj_mejorado(refs, w, m):
    s, r, mm, p = Sim(refs, w, m), [0] * m, [0] * m, 0
    for i, pg in enumerate(refs):
        if pg in s.f:
            k = s.f.index(pg)
            r[k] = 1
            mm[k] |= w[i]
            s.hit(i)
            continue
        k = s.libre()
        ev = k < 0
        if ev:
            k = -1
            while k < 0:
                for d in range(m):
                    c = (p + d) % m
                    if r[c] == 0 and mm[c] == 0:
                        k = c
                        break
                if k >= 0:
                    break
                for d in range(m):
                    c = (p + d) % m
                    if r[c] == 0 and mm[c] == 1:
                        k = c
                        break
                    r[c] = 0
            p = (k + 1) % m
        s.load(i, k, ev)
        r[k], mm[k] = 1, w[i]
    return s


def aging(refs, w, m):
    s, reg, r = Sim(refs, w, m), [0] * m, [0] * m
    tope = AGING_BITS - 1
    mascara = (1 << AGING_BITS) - 1
    for i, pg in enumerate(refs):
        if pg in s.f:
            r[s.f.index(pg)] = 1
            s.hit(i)
        else:
            k = s.libre()
            ev = k < 0
            if ev:
                k = min(range(m), key=lambda c: (reg[c], c))
            s.load(i, k, ev)
            reg[k], r[k] = 0, 1
        for c in range(m):
            if s.f[c] is not None:
                reg[c] = ((reg[c] >> 1) | (r[c] << tope)) & mascara
                r[c] = 0
    return s


def working_set(refs, w, m):
    s, r, tuu = Sim(refs, w, m), [0] * m, [0] * m
    for i, pg in enumerate(refs):
        t = i + 1
        if i > 0 and i % PERIODO == 0:
            r = [0] * m
        if pg in s.f:
            r[s.f.index(pg)] = 1
            s.hit(i)
            continue
        k = s.libre()
        ev = k < 0
        if ev:
            fuera, viejo, emax = -1, -1, -1
            for c in range(m):
                if r[c]:
                    tuu[c] = t
                else:
                    e = t - tuu[c]
                    if e > WS_TAU and fuera < 0:
                        fuera = c
                    if e > emax:
                        emax, viejo = e, c
            k = fuera if fuera >= 0 else (viejo if viejo >= 0 else 0)
        s.load(i, k, ev)
        r[k], tuu[k] = 1, t
    return s


def wsclock(refs, w, m):
    s = Sim(refs, w, m)
    r, mm, tuu, p = [0] * m, [0] * m, [0] * m, 0
    for i, pg in enumerate(refs):
        t = i + 1
        if pg in s.f:
            k = s.f.index(pg)
            r[k] = 1
            mm[k] |= w[i]
            tuu[k] = t
            s.hit(i)
            continue
        k = s.libre()
        ev = k < 0
        if ev:
            k = -1
            for _ in range(m):
                c = p
                if r[c]:
                    r[c], tuu[c] = 0, t
                elif t - tuu[c] > WSCLOCK_TAU:
                    if mm[c] == 0:
                        k = c
                        break
                    mm[c] = 0
                    s.escribir(c)
                p = (p + 1) % m
            if k < 0:
                for d in range(m):
                    c = (p + d) % m
                    if r[c] == 0 and mm[c] == 0:
                        k = c
                        break
                if k < 0:
                    k = p
            p = (k + 1) % m
        s.load(i, k, ev)
        r[k], mm[k], tuu[k] = 1, w[i], t
    return s


def aleatorio(refs, w, m):
    s, x = Sim(refs, w, m), SEMILLA
    for i, pg in enumerate(refs):
        if pg in s.f:
            s.hit(i)
            continue
        k = s.libre()
        ev = k < 0
        if ev:
            x = (1103515245 * x + 12345) % (2 ** 31)
            k = x % m
        s.load(i, k, ev)
    return s


# Mismo orden que src/algoritmos.c
ALGORITMOS = [
    ("FIFO", fifo), ("Optimo", optimo), ("LRU", lru), ("Reloj", reloj),
    ("NRU", nru), ("LFU", lfu), ("MFU", mfu), ("Reloj Mejorado", reloj_mejorado),
    ("Aging", aging), ("Working Set", working_set), ("WSClock", wsclock),
    ("Aleatorio", aleatorio),
]
