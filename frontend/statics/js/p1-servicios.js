"use strict";

// P1: incidencias y valoraciones, integradas sin modificar los flujos P0.
let versionP1 = 0;
function avisoP1(texto) { mensaje(texto); }
function fechaLocalP1() { return hoy(); }
function entradaP1(s) {
  const caja = document.createElement("section");
  caja.className = "mt-3 border-top pt-3";
  caja.dataset.p1Solicitud = String(s.id);
  caja.innerHTML = `<h3 class="h6">Seguimiento del servicio</h3><div data-p1-contenido>Consultando incidencias y valoraciones…</div>`;
  return caja;
}
async function actualizarP1Solicitudes() {
  const actual = ++versionP1;
  const filtro = el("filtro-estado").value;
  const visibles = solicitudes.filter(s => !filtro || s.estado === filtro);
  const cards = [...el("lista-solicitudes").querySelectorAll("article.solicitud-card")];
  for (let i = 0; i < cards.length; i++) {
    const s = visibles[i];
    if (!s || !["ACEPTADA", "FINALIZADA"].includes(s.estado)) continue;
    const nodo = entradaP1(s);
    cards[i].append(nodo);
    try {
      const peticionInc = api(`/api/incidencias?solicitud_id=${s.id}`);
      const peticionVal = s.estado === "FINALIZADA" ? api(`/api/valoraciones?cuidador_id=${s.cuidador_id}`) : Promise.resolve(null);
      const [inc, val] = await Promise.all([peticionInc, peticionVal]);
      if (actual !== versionP1 || !nodo.isConnected) return;
      const permitido = usuario?.rol === "CUIDADOR" && s.estado === "ACEPTADA" && s.fecha_desde <= fechaLocalP1() && fechaLocalP1() <= s.fecha_hasta;
      const incidencias = (inc.incidencias || []).map(i => `<div class="list-entry mb-2"><strong>${html(i.tipo)} · ${html(i.estado)}</strong><p class="mb-1">${html(i.descripcion)}</p><p class="small mb-2">Medidas: ${html(i.medidas_tomadas || "No registradas")}</p>${usuario?.rol === "CUIDADOR" && i.estado === "ABIERTA" ? `<form data-p1-resolver="${i.id}" class="d-flex gap-2 flex-wrap"><input name="medidas_tomadas" class="form-control" maxlength="2000" aria-label="Medidas tomadas para resolver" placeholder="Medidas tomadas" required><button class="btn btn-outline-primary btn-sm">Resolver</button></form>` : ""}</div>`).join("");
      const crear = permitido ? `<form data-p1-incidencia="${s.id}" class="vstack gap-2 mt-3"><label>Tipo<select class="form-select" name="tipo" required><option value="SALUD">Salud</option><option value="CONDUCTA">Conducta</option><option value="EXTRAVIO">Extravío</option><option value="OTRO">Otro</option></select></label><label>Descripción<textarea class="form-control" name="descripcion" maxlength="2000" required></textarea></label><label>Medidas tomadas (opcional)<textarea class="form-control" name="medidas_tomadas" maxlength="2000"></textarea></label><button class="btn btn-primary btn-sm align-self-start">Registrar incidencia</button></form>` : "";
      const incidenciaUI = `<details class="mb-3"><summary>Incidencias (${(inc.incidencias || []).length})</summary><div class="mt-2">${incidencias || '<p class="field-note">No hay incidencias registradas.</p>'}${crear}</div></details>`;
      let valoracionUI = "";
      if (s.estado === "FINALIZADA") {
        const existente = val?.valoraciones?.find(v => v.solicitud_id === s.id);
        if (existente) valoracionUI = `<div class="list-entry"><strong>Valoración registrada: ${html(existente.puntaje)}/5</strong><p class="mb-0">${html(existente.comentario || "Sin comentario")}</p></div>`;
        else if (usuario?.rol === "DUENO") valoracionUI = `<form data-p1-valoracion="${s.id}" class="vstack gap-2"><label>Calificá el servicio<select class="form-select" name="puntaje" required><option value="5">5 estrellas</option><option value="4">4 estrellas</option><option value="3">3 estrellas</option><option value="2">2 estrellas</option><option value="1">1 estrella</option></select></label><label>Comentario (opcional)<textarea class="form-control" name="comentario" maxlength="2000"></textarea></label><button class="btn btn-primary btn-sm align-self-start">Publicar valoración</button></form>`;
        else valoracionUI = '<p class="field-note">Este servicio todavía no tiene valoración.</p>';
        valoracionUI = `<details><summary>Valoración del servicio</summary><div class="mt-2">${valoracionUI}</div></details>`;
      }
      nodo.querySelector("[data-p1-contenido]").innerHTML = incidenciaUI + valoracionUI;
    } catch (e) {
      if (actual === versionP1 && nodo.isConnected) nodo.querySelector("[data-p1-contenido]").textContent = `No se pudo cargar el seguimiento: ${e.message}`;
    }
  }
}

el("lista-solicitudes").addEventListener("submit", e => {
  const form = e.target.closest("form[data-p1-incidencia],form[data-p1-resolver],form[data-p1-valoracion]");
  if (!form) return;
  e.preventDefault();
  const boton = e.submitter || form.querySelector('button[type="submit"],button');
  tarea(async () => {
    const d = Object.fromEntries(new FormData(form).entries());
    if (form.dataset.p1Incidencia) {
      await api("/api/incidencias", "POST", {solicitud_id:Number(form.dataset.p1Incidencia),tipo:d.tipo,descripcion:d.descripcion,medidas_tomadas:d.medidas_tomadas || null});
      await cargarSolicitudes(); avisoP1("Incidencia registrada correctamente.");
    } else if (form.dataset.p1Resolver) {
      await api(`/api/incidencias/${form.dataset.p1Resolver}/resolver`, "PATCH", {medidas_tomadas:d.medidas_tomadas});
      await cargarSolicitudes(); avisoP1("Incidencia resuelta correctamente.");
    } else if (form.dataset.p1Valoracion) {
      await api("/api/valoraciones", "POST", {solicitud_id:Number(form.dataset.p1Valoracion),puntaje:Number(d.puntaje),comentario:d.comentario || null});
      await cargarSolicitudes(); avisoP1("Valoración publicada correctamente.");
    }
  }, boton);
});