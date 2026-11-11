/*
 * app.js - Interfaz del simulador web (PASO 7)
 *
 * IMPORTANTE: este archivo NO implementa ningún algoritmo de reemplazo.
 * Todos los cálculos los hace el código C (src/algoritmos/*.c) compilado a
 * WebAssembly (motor.wasm). Aquí solo se leen entradas y se dibuja la traza.
 */
"use strict";

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));

let motor = null;      // funciones del módulo WebAssembly
let MAX_MARCOS = 8, MAX_REFS = 64;

const estado = {
  refs: [], ops: [], marcos: 3, algoritmo: 1,
  traza: null,         // resultado del algoritmo elegido
  paso: -1,            // -1 = antes de empezar
  reproduciendo: false, temporizador: null,
  orden: { col: "fallos", asc: true },
};

/* ------------------------------------------------------------------ */
/* Carga del motor C                                                   */
/* ------------------------------------------------------------------ */
function cargarMotor() {
  const insignia = $("#estado-motor");
  if (location.protocol === "file:") {
    insignia.textContent = "Ábrelo con un servidor: make web-servir";
    insignia.classList.add("mal");
    mostrarError("El navegador no permite cargar WebAssembly desde un archivo local. " +
      "Ejecuta «make web-servir» en src/ y abre http://localhost:8000");
    return;
  }
  if (typeof crearMotor !== "function") {
    insignia.textContent = "Falta motor.js (ejecuta make web)";
    insignia.classList.add("mal");
    return;
  }
  crearMotor().then((M) => {
    const f = (nombre, ret, args) => M.cwrap(nombre, ret, args);
    motor = {
      numAlgoritmos: f("web_num_algoritmos", "number", []),
      maxMarcos: f("web_max_marcos", "number", []),
      maxRefs: f("web_max_refs", "number", []),
      marcosOficial: f("web_marcos_oficial", "number", []),
      numRefsOficial: f("web_num_refs_oficial", "number", []),
      refOficial: f("web_ref_oficial", "number", ["number"]),
      escrituraOficial: f("web_escritura_oficial", "number", ["number"]),
      nombre: f("web_nombre_algoritmo", "string", ["number"]),
      responsable: f("web_responsable", "string", ["number"]),
      fijarRef: f("web_fijar_ref", null, ["number", "number"]),
      fijarEscritura: f("web_fijar_escritura", null, ["number", "number"]),
      simular: f("web_simular", "number", ["number", "number", "number"]),
      fallos: f("web_fallos", "number", []),
      aciertos: f("web_aciertos", "number", []),
      escrituras: f("web_escrituras", "number", []),
      marco: f("web_marco", "number", ["number", "number"]),
      cargado: f("web_marco_cargado", "number", ["number"]),
      victima: f("web_victima", "number", ["number"]),
      aux: f("web_aux", "string", ["number"]),
    };
    MAX_MARCOS = motor.maxMarcos();
    MAX_REFS = motor.maxRefs();
    insignia.textContent = "Motor C (WebAssembly) listo";
    insignia.classList.add("ok");
    iniciar();
  }).catch((e) => {
    insignia.textContent = "Error al cargar el motor";
    insignia.classList.add("mal");
    mostrarError("No se pudo cargar motor.wasm: " + e);
  });
}

/* Ejecuta un algoritmo en C y devuelve su traza como objeto JS */
function ejecutar(id, refs, ops, marcos) {
  refs.forEach((p, i) => { motor.fijarRef(i, p); motor.fijarEscritura(i, ops[i]); });
  if (motor.simular(id, refs.length, marcos) < 0) return null;
  const pasos = refs.map((_, i) => {
    const m = [];
    for (let k = 0; k < marcos; k++) m.push(motor.marco(i, k));
    return { pagina: refs[i], w: ops[i], marcos: m, cargado: motor.cargado(i),
             victima: motor.victima(i), aux: motor.aux(i) };
  });
  return { id, nombre: motor.nombre(id), fallos: motor.fallos(), aciertos: motor.aciertos(),
           escrituras: motor.escrituras(), pasos, marcos };
}

/* ------------------------------------------------------------------ */
/* Entradas                                                            */
/* ------------------------------------------------------------------ */
function mostrarError(msg) {
  const e = $("#error-entrada");
  e.textContent = msg || "";
  e.hidden = !msg;
}

function leerEntradas() {
  const texto = $("#in-cadena").value.trim();
  const partes = texto ? texto.split(/[\s,;]+/).filter(Boolean) : [];
  if (partes.length === 0) return "Escribe al menos una referencia.";
  if (partes.length > MAX_REFS) return `Máximo ${MAX_REFS} referencias (hay ${partes.length}).`;
  const refs = [];
  for (const p of partes) {
    if (!/^\d{1,3}$/.test(p)) return `«${p}» no es un número de página válido (0 a 999).`;
    refs.push(Number(p));
  }
  let opsTxt = $("#in-ops").value.replace(/[\s,;]/g, "").toUpperCase();
  if (opsTxt === "") opsTxt = "R".repeat(refs.length);
  if (!/^[RW01]*$/.test(opsTxt)) return "Las operaciones solo pueden ser R/W (o 0/1).";
  if (opsTxt.length !== refs.length)
    return `Hay ${refs.length} referencias pero ${opsTxt.length} operaciones.`;
  estado.refs = refs;
  estado.ops = [...opsTxt].map((c) => (c === "W" || c === "1") ? 1 : 0);
  estado.marcos = Number($("#in-marcos").value);
  estado.algoritmo = Number($("#in-algoritmo").value);
  return null;
}

function escribirEntradas(refs, ops, marcos) {
  $("#in-cadena").value = refs.join(", ");
  $("#in-ops").value = ops.map((w) => (w ? "W" : "R")).join("");
  if (marcos) $("#in-marcos").value = String(marcos);
}

function cargarPreset(nombre) {
  if (nombre === "oficial") {
    const n = motor.numRefsOficial();
    const refs = [], ops = [];
    for (let i = 0; i < n; i++) { refs.push(motor.refOficial(i)); ops.push(motor.escrituraOficial(i)); }
    escribirEntradas(refs, ops, motor.marcosOficial());
  } else if (nombre === "belady") {
    const refs = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5];
    escribirEntradas(refs, refs.map(() => 0), 3);
  } else {
    const n = 20 + Math.floor(Math.random() * 11);
    const refs = Array.from({ length: n }, () => Math.floor(Math.random() * 8));
    const ops = refs.map(() => (Math.random() < 0.3 ? 1 : 0));
    escribirEntradas(refs, ops);
  }
  recalcular();
}

/* ------------------------------------------------------------------ */
/* Vista paso a paso                                                   */
/* ------------------------------------------------------------------ */
function recalcular() {
  pausar();
  const err = leerEntradas();
  mostrarError(err);
  if (err) return;
  estado.traza = ejecutar(estado.algoritmo, estado.refs, estado.ops, estado.marcos);
  estado.paso = -1;
  dibujarMatriz();
  actualizarPaso();
  if (!$("#vista-comparar").hidden) dibujarComparacion();
}

function dibujarMatriz() {
  const t = estado.traza, tabla = $("#matriz");
  if (!t) { tabla.innerHTML = ""; return; }
  const n = t.pasos.length;
  let html = "<thead><tr><th scope=\"row\">Paso</th>";
  for (let i = 0; i < n; i++) html += `<th data-c="${i}">${i + 1}</th>`;
  html += "</tr></thead><tbody>";
  html += "<tr><th scope=\"row\">Ref</th>" + t.pasos.map((p, i) => `<td data-c="${i}"><strong>${p.pagina}</strong></td>`).join("") + "</tr>";
  html += "<tr><th scope=\"row\">Op</th>" + t.pasos.map((p, i) =>
    `<td data-c="${i}" class="op ${p.w ? "w" : ""}" title="Clic para cambiar lectura/escritura">${p.w ? "W" : "R"}</td>`).join("") + "</tr>";
  for (let k = 0; k < t.marcos; k++) {
    html += `<tr><th scope="row">M${k + 1}</th>` + t.pasos.map((p, i) =>
      `<td data-c="${i}" data-k="${k}" class="celda"></td>`).join("") + "</tr>";
  }
  html += "<tr><th scope=\"row\">Res</th>" + t.pasos.map((p, i) => `<td data-c="${i}" class="res"></td>`).join("") + "</tr>";
  html += "<tr><th scope=\"row\">Sale</th>" + t.pasos.map((p, i) => `<td data-c="${i}" class="sale"></td>`).join("") + "</tr>";
  html += "</tbody>";
  tabla.innerHTML = html;

  tabla.querySelectorAll("td.op").forEach((td) => td.addEventListener("click", () => {
    const i = Number(td.dataset.c);
    estado.ops[i] = estado.ops[i] ? 0 : 1;
    const pasoAnterior = estado.paso;
    escribirEntradas(estado.refs, estado.ops);
    recalcular();
    irA(pasoAnterior);
  }));
}

function actualizarPaso() {
  const t = estado.traza;
  if (!t) return;
  const n = t.pasos.length, actual = estado.paso;
  const revelar = $("#in-revelar").checked;
  const visible = (i) => revelar || i <= actual;

  $$("#matriz [data-c]").forEach((el) => el.classList.toggle("actual", Number(el.dataset.c) === actual));
  $$("#matriz td.celda").forEach((td) => {
    const i = Number(td.dataset.c), k = Number(td.dataset.k), p = t.pasos[i];
    const v = p.marcos[k];
    td.textContent = v < 0 ? "–" : v;
    td.className = "celda" + (v < 0 ? " vacio" : "");
    if (!visible(i)) { td.classList.add("oculta"); return; }
    if (p.cargado === k) td.classList.add("cargada");
    else if (p.cargado < 0 && v === p.pagina) td.classList.add("acierto");
    td.classList.toggle("actual", i === actual);
  });
  $$("#matriz td.res").forEach((td) => {
    const i = Number(td.dataset.c), p = t.pasos[i];
    td.textContent = visible(i) ? (p.cargado < 0 ? "H" : "F") : "";
    td.className = "res " + (visible(i) ? (p.cargado < 0 ? "res-h" : "res-f") : "") + (i === actual ? " actual" : "");
  });
  $$("#matriz td.sale").forEach((td) => {
    const i = Number(td.dataset.c), p = t.pasos[i];
    td.textContent = visible(i) && p.victima >= 0 ? p.victima : "";
  });

  // Indicadores acumulados hasta el paso actual
  let fallos = 0, aciertos = 0;
  for (let i = 0; i <= actual; i++) (t.pasos[i].cargado < 0) ? aciertos++ : fallos++;
  $("#k-paso").textContent = `${actual + 1} / ${n}`;
  $("#k-fallos").textContent = fallos;
  $("#k-aciertos").textContent = aciertos;
  $("#k-tasa").textContent = actual >= 0 ? `${(100 * fallos / (actual + 1)).toFixed(1)} %` : "—";
  $("#k-escr").textContent = actual === n - 1 ? t.escrituras : "al final";

  // Explicación en lenguaje natural del paso actual
  const exp = $("#txt-explicacion"), aux = $("#txt-aux");
  if (actual < 0) {
    exp.textContent = `${t.nombre}: ${n} referencias, ${t.marcos} marco(s) vacíos. Presiona ▶ o → para avanzar.`;
    aux.textContent = "—";
  } else {
    const p = t.pasos[actual];
    const op = p.w ? " (escritura: la página queda modificada)" : "";
    let txt;
    if (p.cargado < 0) {
      txt = `Paso ${actual + 1}: la página ${p.pagina} ya está en M${p.marcos.indexOf(p.pagina) + 1} → ACIERTO${op}.`;
    } else if (p.victima < 0) {
      txt = `Paso ${actual + 1}: la página ${p.pagina} no está en memoria → FALLO. Entra en el marco libre M${p.cargado + 1}${op}.`;
    } else {
      txt = `Paso ${actual + 1}: la página ${p.pagina} no está en memoria → FALLO. ${t.nombre} expulsa la página ${p.victima} de M${p.cargado + 1} y carga la ${p.pagina}${op}.`;
    }
    if (actual === n - 1) txt += ` Fin: ${t.fallos} fallos, ${t.aciertos} aciertos, ${t.escrituras} escrituras a disco.`;
    exp.textContent = txt;
    aux.textContent = p.aux || "—";
  }

  $("#b-ant").disabled = $("#b-inicio").disabled = actual < 0;
  $("#b-sig").disabled = $("#b-fin").disabled = actual >= n - 1;
  const celdaActual = document.querySelector(`#matriz thead th[data-c="${actual}"]`);
  if (celdaActual) celdaActual.scrollIntoView({ block: "nearest", inline: "center" });
}

function irA(paso) {
  if (!estado.traza) return;
  estado.paso = Math.max(-1, Math.min(paso, estado.traza.pasos.length - 1));
  actualizarPaso();
}

function retardo() { return 1100 - 100 * Number($("#in-velocidad").value); }

function reproducir() {
  if (!estado.traza) return;
  if (estado.paso >= estado.traza.pasos.length - 1) irA(-1);
  estado.reproduciendo = true;
  $("#b-play").textContent = "⏸ Pausa";
  const tic = () => {
    if (!estado.reproduciendo) return;
    if (estado.paso >= estado.traza.pasos.length - 1) { pausar(); return; }
    irA(estado.paso + 1);
    estado.temporizador = setTimeout(tic, retardo());
  };
  tic();
}

function pausar() {
  estado.reproduciendo = false;
  clearTimeout(estado.temporizador);
  $("#b-play").textContent = "▶ Reproducir";
}

/* ------------------------------------------------------------------ */
/* Vista comparar                                                      */
/* ------------------------------------------------------------------ */
function todos(marcos) {
  const res = [];
  for (let id = 1; id <= motor.numAlgoritmos(); id++) {
    const r = ejecutar(id, estado.refs, estado.ops, marcos);
    if (r) res.push(r);
  }
  return res;
}

function dibujarComparacion() {
  if (!estado.refs.length) return;
  const res = todos(estado.marcos);
  const n = estado.refs.length;

  // Gráfico de barras horizontales (SVG), ordenado de menos a más fallos
  const orden = [...res].sort((a, b) => a.fallos - b.fallos || a.id - b.id);
  const W = 560, filaH = 26, izq = 130, der = 70, top = 8;
  const H = top + orden.length * filaH + 24;
  const escala = (v) => izq + (W - izq - der) * v / n;
  let svg = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
  for (let v = 0; v <= n; v += Math.max(1, Math.ceil(n / 6))) {
    svg += `<line x1="${escala(v)}" x2="${escala(v)}" y1="${top}" y2="${H - 20}"/>`;
    svg += `<text class="eje" x="${escala(v)}" y="${H - 6}" text-anchor="middle">${v}</text>`;
  }
  orden.forEach((r, i) => {
    const y = top + i * filaH + 4;
    const opt = r.id === 2 ? " opt" : "";
    svg += `<text x="${izq - 8}" y="${y + 13}" text-anchor="end">${r.nombre}</text>`;
    svg += `<rect class="barra${opt}" data-id="${r.id}" x="${izq}" y="${y}" width="${Math.max(1, escala(r.fallos) - izq)}" height="18" rx="3">` +
           `<title>${r.nombre}: ${r.fallos} fallos de ${n} (${(100 * r.fallos / n).toFixed(1)} %), ${r.escrituras} escrituras</title></rect>`;
    svg += `<text x="${escala(r.fallos) + 6}" y="${y + 13}">${r.fallos}</text>`;
  });
  svg += "</svg>";
  $("#grafico").innerHTML = svg;
  $$("#grafico .barra").forEach((b) => b.addEventListener("click", () => verAlgoritmo(Number(b.dataset.id))));

  // Tabla comparativa ordenable
  const { col, asc } = estado.orden;
  const valor = (r) => ({ id: r.id, nombre: r.nombre, fallos: r.fallos, aciertos: r.aciertos,
                          tasa: r.fallos / n, escr: r.escrituras })[col];
  const filas = [...res].sort((a, b) => {
    const x = valor(a), y = valor(b);
    const c = typeof x === "string" ? x.localeCompare(y) : x - y;
    return (asc ? c : -c) || a.id - b.id;
  });
  $("#tabla-comp tbody").innerHTML = filas.map((r) =>
    `<tr data-id="${r.id}"><td>${r.id}</td><td>${r.nombre}</td><td class="num">${r.fallos}</td>` +
    `<td class="num">${r.aciertos}</td><td class="num">${(100 * r.fallos / n).toFixed(2)} %</td>` +
    `<td class="num">${r.escrituras}</td></tr>`).join("");
  $$("#tabla-comp tbody tr").forEach((tr) => tr.addEventListener("click", () => verAlgoritmo(Number(tr.dataset.id))));
  $$("#tabla-comp th").forEach((th) => {
    const base = th.textContent.replace(/ [▲▼]$/, "");
    th.textContent = base + (th.dataset.col === col ? (asc ? " ▲" : " ▼") : "");
  });

  // Belády: m frente a m + 1 marcos
  const m = estado.marcos, m1 = m + 1;
  $("#txt-m").textContent = m; $("#txt-m1").textContent = m1;
  $("#th-m").textContent = `${m} marcos`; $("#th-m1").textContent = `${m1} marcos`;
  if (m1 > MAX_MARCOS) {
    $("#tabla-belady tbody").innerHTML = `<tr><td colspan="4">El máximo es ${MAX_MARCOS} marcos: elige menos marcos para comparar.</td></tr>`;
    return;
  }
  const res1 = todos(m1);
  $("#tabla-belady tbody").innerHTML = res.map((r, i) => {
    const a = r.fallos, b = res1[i].fallos;
    const txt = b > a ? `<span class="anomalia">▲ anomalía: ${b - a} fallo(s) más</span>`
              : b < a ? `mejora: ${a - b} fallo(s) menos` : "sin cambio";
    return `<tr><td>${r.nombre}</td><td class="num">${a}</td><td class="num">${b}</td><td>${txt}</td></tr>`;
  }).join("");
}

function verAlgoritmo(id) {
  $("#in-algoritmo").value = String(id);
  mostrarPestana("paso");
  recalcular();
}

function mostrarPestana(cual) {
  const paso = cual === "paso";
  $("#vista-paso").hidden = !paso;
  $("#vista-comparar").hidden = paso;
  $("#tab-paso").setAttribute("aria-selected", String(paso));
  $("#tab-comparar").setAttribute("aria-selected", String(!paso));
  if (!paso) { pausar(); dibujarComparacion(); }
}

/* ------------------------------------------------------------------ */
/* Inicio                                                              */
/* ------------------------------------------------------------------ */
function iniciar() {
  $("#max-refs").textContent = MAX_REFS;
  $("#in-marcos").innerHTML = Array.from({ length: MAX_MARCOS }, (_, i) =>
    `<option value="${i + 1}">${i + 1}</option>`).join("");
  let opciones = "";
  for (let id = 1; id <= motor.numAlgoritmos(); id++)
    opciones += `<option value="${id}">${id}. ${motor.nombre(id)}</option>`;
  $("#in-algoritmo").innerHTML = opciones;

  $$("[data-preset]").forEach((b) => b.addEventListener("click", () => cargarPreset(b.dataset.preset)));
  ["#in-cadena", "#in-ops"].forEach((s) => $(s).addEventListener("change", recalcular));
  ["#in-marcos", "#in-algoritmo"].forEach((s) => $(s).addEventListener("change", recalcular));
  $("#in-revelar").addEventListener("change", actualizarPaso);

  $("#b-inicio").addEventListener("click", () => { pausar(); irA(-1); });
  $("#b-ant").addEventListener("click", () => { pausar(); irA(estado.paso - 1); });
  $("#b-sig").addEventListener("click", () => { pausar(); irA(estado.paso + 1); });
  $("#b-fin").addEventListener("click", () => { pausar(); irA(Infinity); });
  $("#b-play").addEventListener("click", () => (estado.reproduciendo ? pausar() : reproducir()));
  $("#tab-paso").addEventListener("click", () => mostrarPestana("paso"));
  $("#tab-comparar").addEventListener("click", () => mostrarPestana("comparar"));
  $$("#tabla-comp th").forEach((th) => th.addEventListener("click", () => {
    const col = th.dataset.col;
    estado.orden = { col, asc: estado.orden.col === col ? !estado.orden.asc : true };
    dibujarComparacion();
  }));

  document.addEventListener("keydown", (e) => {
    if (e.target.matches("input, select, textarea") || $("#vista-paso").hidden) return;
    if (e.key === "ArrowRight") { pausar(); irA(estado.paso + 1); }
    else if (e.key === "ArrowLeft") { pausar(); irA(estado.paso - 1); }
    else if (e.key === "Home") { pausar(); irA(-1); }
    else if (e.key === "End") { pausar(); irA(Infinity); }
    else if (e.key === " ") { e.preventDefault(); estado.reproduciendo ? pausar() : reproducir(); }
  });

  cargarPreset("oficial");
  aplicarUrl();
}

/* Estado inicial desde la URL, p. ej. ?preset=belady&marcos=4&alg=4&paso=18&vista=comparar
   (útil para compartir un enlace a un paso concreto o para capturas del informe). */
function aplicarUrl() {
  const q = new URLSearchParams(location.search);
  if (q.get("tema") === "claro") document.documentElement.dataset.theme = "light";
  if (q.get("tema") === "oscuro") document.documentElement.dataset.theme = "dark";
  if (q.has("preset")) cargarPreset(q.get("preset"));
  if (q.has("marcos")) $("#in-marcos").value = q.get("marcos");
  if (q.has("alg")) $("#in-algoritmo").value = q.get("alg");
  if (q.has("marcos") || q.has("alg")) recalcular();
  if (q.get("revelar") === "1") $("#in-revelar").checked = true;
  if (q.has("paso")) irA(Number(q.get("paso")) - 1);
  if (q.get("vista") === "comparar") mostrarPestana("comparar");
}

/* Tema claro/oscuro: por defecto sigue al sistema; el botón lo fija (se recuerda si se puede) */
(function tema() {
  const raiz = document.documentElement;
  try { const t = localStorage.getItem("tema"); if (t) raiz.dataset.theme = t; } catch (e) { /* sin almacenamiento */ }
  $("#b-tema").addEventListener("click", () => {
    const oscuro = raiz.dataset.theme ? raiz.dataset.theme === "dark"
                                      : matchMedia("(prefers-color-scheme: dark)").matches;
    raiz.dataset.theme = oscuro ? "light" : "dark";
    try { localStorage.setItem("tema", raiz.dataset.theme); } catch (e) { /* sin almacenamiento */ }
  });
})();

cargarMotor();
