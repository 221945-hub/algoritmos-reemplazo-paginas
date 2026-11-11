// web_volcado.js - Ejecuta el motor WebAssembly (web/motor.js) en Node.js
// y vuelca las trazas en JSON para que tests/validar.py las compare (PASO 7).
//
// Entrada (stdin):  [{"refs":[...], "w":[...], "m":3}, ...]
// Salida  (stdout): [[{"fallos":n,"aciertos":n,"esc":n,"trace":[[[marcos],"F"|"H"],...]}, x12], ...]
"use strict";
const path = require("path");
const crearMotor = require(path.join(__dirname, "..", "web", "motor.js"));

let entrada = "";
process.stdin.on("data", (d) => (entrada += d));
process.stdin.on("end", async () => {
  const M = await crearMotor();
  const f = (n, r, a) => M.cwrap(n, r, a);
  const simular = f("web_simular", "number", ["number", "number", "number"]);
  const fijarRef = f("web_fijar_ref", null, ["number", "number"]);
  const fijarEsc = f("web_fijar_escritura", null, ["number", "number"]);
  const marco = f("web_marco", "number", ["number", "number"]);
  const cargado = f("web_marco_cargado", "number", ["number"]);
  const fallos = f("web_fallos", "number", []);
  const aciertos = f("web_aciertos", "number", []);
  const escr = f("web_escrituras", "number", []);
  const nAlg = f("web_num_algoritmos", "number", [])();

  const salida = JSON.parse(entrada).map(({ refs, w, m }) => {
    const res = [];
    for (let id = 1; id <= nAlg; id++) {
      refs.forEach((p, i) => { fijarRef(i, p); fijarEsc(i, w[i]); });
      if (simular(id, refs.length, m) < 0) { res.push(null); continue; }
      const trace = refs.map((_, i) => {
        const marcos = [];
        for (let k = 0; k < m; k++) { const v = marco(i, k); marcos.push(v < 0 ? null : v); }
        return [marcos, cargado(i) < 0 ? "H" : "F"];
      });
      res.push({ fallos: fallos(), aciertos: aciertos(), esc: escr(), trace });
    }
    return res;
  });
  process.stdout.write(JSON.stringify(salida));
});
