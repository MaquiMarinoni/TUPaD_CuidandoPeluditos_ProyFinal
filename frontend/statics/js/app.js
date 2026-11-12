"use strict";

// La API es la autoridad para permisos, precios y cupos. La interfaz solo guía.
const el = id => document.getElementById(id);
const todos = selector => [...document.querySelectorAll(selector)];
const html = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"})[c]);
const datosForm = id => Object.fromEntries(new FormData(el(id)).entries());
const dinero = value => value == null ? "No ofrece" : new Intl.NumberFormat("es-AR", {style:"currency", currency:"ARS"}).format(Number(value));
const fecha = value => value ? new Intl.DateTimeFormat("es-AR").format(new Date(`${value}T12:00:00`)) : "—";
const hoy = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`; };
const estado = value => ({PENDIENTE:"Pendiente", ACEPTADA:"Aceptada", RECHAZADA:"Rechazada", CANCELADA:"Cancelada", FINALIZADA:"Finalizada"})[value] || value;
let csrf = null, usuario = null, mascotas = [], cuidadores = [], disponibilidades = [], solicitudes = [];
let mascotaEditada = null, agendaEditada = null, tienePerfil = false;
let versionSesion = 0;
let filtrosInicio = null;
const vacio = (titulo, texto, enlace="", accion="") => `<div class="empty-state"><h3>${html(titulo)}</h3><p class="mb-0">${html(texto)}</p>${enlace ? `<a href="${enlace}" class="btn btn-outline-primary mt-3">${html(accion)}</a>` : ""}</div>`;

function mensaje(texto, error=false) {
  const nodo = el("mensaje");
  nodo.className = `alert alert-${error ? "danger" : "success"}`;
  nodo.textContent = texto;
  nodo.focus({preventScroll:true});
  nodo.scrollIntoView({behavior:"smooth", block:"nearest"});
}

async function token() {
  const r = await fetch("/api/auth/csrf-token", {credentials:"same-origin"});
  if (!r.ok) throw new Error("No pudimos obtener el token de seguridad. Recargá la página.");
  csrf = (await r.json()).csrf_token;
}

async function api(ruta, metodo="GET", datos) {
  const headers = {Accept:"application/json"};
  if (datos !== undefined) headers["Content-Type"] = "application/json";
  if (!["GET", "HEAD"].includes(metodo)) {
    if (!csrf) await token();
    headers["X-CSRFToken"] = csrf;
  }
  let r;
  try {
    r = await fetch(ruta, {method:metodo, headers, credentials:"same-origin", ...(datos === undefined ? {} : {body:JSON.stringify(datos)})});
  } catch { throw new Error("No pudimos conectar con el servidor. Verificá la conexión y volvé a intentar."); }
  let body;
  try { body = await r.json(); } catch { throw new Error("El servidor no pudo completar la operación. Volvé a intentar en unos momentos."); }
  if (!r.ok) {
    if (r.status === 401 && ruta !== "/api/auth/login") {
      limpiarSesion(); actualizarAcceso(); location.hash = "cuenta";
    }
    if (r.status === 400 && /token/i.test(body.error || "")) csrf = null;
    const error = new Error(body.error || `No se pudo completar la operación (${r.status}).`);
    error.status = r.status;
    throw error;
  }
  return body;
}

async function tarea(fn, boton) {
  if (boton?.disabled) return;
  const texto = boton?.textContent;
  if (boton) { boton.disabled = true; boton.textContent = "Un momento…"; }
  try { await fn(); } catch (e) { console.error(e); mensaje(e.message, true); }
  finally { if (boton) { boton.disabled = false; if (boton.textContent === "Un momento…") boton.textContent = texto; } }
}

function confirmar(texto) {
  const dialogo = el("confirmacion");
  el("confirmacion-texto").textContent = texto;
  dialogo.returnValue = "";
  return new Promise(resolve => {
    dialogo.addEventListener("close", () => resolve(dialogo.returnValue === "confirmar"), {once:true});
    dialogo.showModal();
  });
}

function limpiarSesion() {
  versionSesion++;
  usuario = null; csrf = null; mascotas = []; solicitudes = []; disponibilidades = []; tienePerfil = false;
  ["lista-mascotas", "lista-solicitudes", "mis-disponibilidades", "select-mascotas", "detalle-cuidador"].forEach(id => el(id).replaceChildren());
  el("detalle-cuidador").hidden = true;
  ["form-perfil", "form-solicitud", "form-agenda", "form-mascota", "form-login", "form-register"].forEach(id => el(id).reset());
  cancelarEdicionMascota(); cancelarEdicionAgenda();
  el("campos-agenda").disabled = true;
  actualizarModalidades();
}

function actualizarAcceso() {
  todos("[data-role]").forEach(n => { n.hidden = usuario?.rol !== n.dataset.role; });
  todos("[data-auth]").forEach(n => { n.hidden = !usuario; });
  todos("[data-guest]").forEach(n => { n.hidden = Boolean(usuario); });
  el("usuario-actual").hidden = !usuario;
  el("usuario-actual").textContent = usuario ? `${usuario.nombre} · ${usuario.rol === "DUENO" ? "Dueño" : "Cuidador"}` : "";
  el("salir").hidden = !usuario; el("acceso").hidden = Boolean(usuario);
  el("cuenta-activa").hidden = !usuario; el("formularios-cuenta").hidden = Boolean(usuario);
  el("datos-cuenta").textContent = usuario ? `${usuario.nombre} ${usuario.apellido} · ${usuario.email}` : "";
}

async function refrescarSesion() {
  const r = await api("/api/auth/me");
  usuario = r.autenticado ? r.usuario : null;
  actualizarAcceso();
}

async function navegar(enfocar=true) {
  const ancla = location.hash.slice(1);
  let tab = ["como-funciona", "ayuda"].includes(ancla) ? "inicio" : ancla || "inicio";
  const privados = {mascotas:"DUENO", agenda:"CUIDADOR", solicitudes:"AMBOS"};
  if (!el(`tab-${tab}`)) tab = "inicio";
  if (privados[tab] && (!usuario || (privados[tab] !== "AMBOS" && usuario.rol !== privados[tab]))) {
    tab = usuario ? "inicio" : "cuenta";
    history.replaceState(null, "", `#${tab}`);
  }
  todos(".page-section").forEach(n => { n.hidden = n.id !== `tab-${tab}`; });
  todos("[data-tab]").forEach(n => { if (n.dataset.tab === tab) n.setAttribute("aria-current", "page"); else n.removeAttribute("aria-current"); });
  el("mensaje").classList.add("d-none");
  if (["como-funciona", "ayuda"].includes(ancla)) {
    el(ancla).scrollIntoView({behavior:"smooth", block:"start"});
    (el(ancla).querySelector("h2") || el("titulo-como"))?.focus({preventScroll:true});
  } else if (enfocar) el(`titulo-${tab}`)?.focus({preventScroll:true});
  if (tab === "mascotas") await cargarMascotas();
  if (tab === "cuidadores") await cargarCuidadores(datosForm("form-buscar"));
  if (tab === "agenda") await cargarAgenda();
  if (tab === "solicitudes") {
    await cargarCuidadores();
    if (usuario?.rol === "DUENO") await cargarMascotas();
    await cargarSolicitudes();
    estimar();
  }
}

async function cargarMascotas() {
  const version = versionSesion;
  const r = await api("/api/mascotas");
  if (version !== versionSesion) return;
  mascotas = r.mascotas;
  el("lista-mascotas").innerHTML = mascotas.length ? mascotas.map(m => `<article class="pet-card"><span class="pet-avatar" aria-hidden="true">${m.especie === "GATO" ? "🐱" : "🐶"}</span><div class="flex-grow-1"><h3 class="h5">${html(m.nombre)}</h3><p class="field-note mb-1">${m.especie === "GATO" ? "Gato" : "Perro"} · ${html(m.tamano.toLowerCase())}${m.raza ? ` · ${html(m.raza)}` : ""}</p><p class="small mb-1">${html(m.cuidados_especiales || "Sin cuidados especiales registrados.")}</p><div class="entry-actions"><button class="btn btn-outline-primary btn-sm" data-editar-mascota="${m.id}">Editar</button><button class="btn btn-outline-danger btn-sm" data-eliminar-mascota="${m.id}">Desactivar</button></div></div></article>`).join("") : vacio("Tu familia peluda empieza acá", "Agregá una mascota para poder solicitar su cuidado.");
  const seleccionados = todos('[name="mascota_id"]:checked').map(n => n.value);
  el("select-mascotas").innerHTML = mascotas.length ? mascotas.map(m => `<label class="pet-option"><input type="checkbox" name="mascota_id" value="${m.id}" ${seleccionados.includes(String(m.id)) ? "checked" : ""}>${html(m.nombre)} · ${m.especie === "GATO" ? "Gato" : "Perro"}</label>`).join("") : vacio("Primero, tu mascota", "Necesitás registrar al menos una.", "#mascotas", "Agregar mascota");
}

function cancelarEdicionMascota() {
  mascotaEditada = null; el("form-mascota").reset();
  el("titulo-form-mascota").textContent = "Agregar mascota";
  el("cancelar-mascota").hidden = true; el("guardar-mascota").textContent = "Guardar mascota";
}

async function cargarCuidadores(filtros={}) {
  const query = new URLSearchParams(Object.entries(filtros).filter(([,v]) => v.trim()));
  let resultados = (await api(`/api/cuidadores?${query}`)).cuidadores;
  if (filtrosInicio) {
    const f = filtrosInicio;
    resultados = resultados.filter(c => (!f.especie || (f.especie === "PERRO" ? c.admite_perros : c.admite_gatos)) && (f.modalidad !== "VISITA" || c.tarifa_visita != null));
    if (f.fecha_desde) {
      const compatibles = await Promise.all(resultados.map(async c => {
        const r = await api(`/api/cuidadores/${c.id}/disponibilidades`);
        return r.disponibilidades.some(d => d.modalidad === f.modalidad && d.fecha_desde <= f.fecha_desde && d.fecha_hasta >= (f.modalidad === "VISITA" ? f.fecha_desde : f.fecha_hasta));
      }));
      resultados = resultados.filter((c, i) => compatibles[i]);
    }
  }
  cuidadores = resultados;
  const resumen = filtrosInicio ? ` · ${filtrosInicio.modalidad === "VISITA" ? "Visitas a domicilio" : "Alojamiento"}${filtrosInicio.especie ? ` · ${filtrosInicio.especie === "PERRO" ? "Perro" : "Gato"}` : ""}${filtrosInicio.fecha_desde ? ` · ${fecha(filtrosInicio.fecha_desde)}${filtrosInicio.modalidad === "ALOJAMIENTO" ? ` al ${fecha(filtrosInicio.fecha_hasta)}` : ""}` : ""}. Cupo sujeto a confirmación.` : "";
  el("cantidad-cuidadores").textContent = `${cuidadores.length} ${cuidadores.length === 1 ? "cuidador encontrado" : "cuidadores encontrados"}${resumen}`;
  el("lista-cuidadores").innerHTML = cuidadores.length ? cuidadores.map(c => `<div class="col-md-6 col-xl-4"><article class="panel caregiver-card"><div class="d-flex align-items-center gap-3"><span class="caregiver-avatar" aria-hidden="true">${html(c.nombre.slice(0,1))}${html(c.apellido.slice(0,1))}</span><div><h2 class="mb-1">${html(c.nombre)} ${html(c.apellido)}</h2><p>${html(c.localidad)}, ${html(c.provincia)}</p></div></div><p>${html(c.descripcion || "Un espacio para cuidar con cariño.")}</p><div class="tags">${c.admite_perros ? '<span class="tag">Perros</span>' : ""}${c.admite_gatos ? '<span class="tag">Gatos</span>' : ""}<span class="tag">Hasta ${c.capacidad_maxima} mascotas</span></div><div class="price-grid"><p>Alojamiento<strong>${dinero(c.tarifa_diaria)}</strong><small>por mascota / noche</small></p><p>Visita<strong>${dinero(c.tarifa_visita)}</strong><small>por turno</small></p></div><button class="btn btn-outline-primary" data-detalle="${c.id}">Conocer y ver disponibilidad</button></article></div>`).join("") : `<div class="col-12">${vacio("No encontramos cuidadores", "Probá con otra localidad o limpiá los filtros.")}</div>`;
  const previo = el("select-cuidador").value;
  el("select-cuidador").innerHTML = '<option value="">Elegí un cuidador</option>' + cuidadores.map(c => `<option value="${c.id}">${html(c.nombre)} ${html(c.apellido)} · ${html(c.localidad)}</option>`).join("");
  if (cuidadores.some(c => String(c.id) === previo)) el("select-cuidador").value = previo;
}

async function detalleCuidador(id) {
  const c = (await api(`/api/cuidadores/${id}`)).cuidador;
  const ds = (await api(`/api/cuidadores/${id}/disponibilidades`)).disponibilidades;
  const nodo = el("detalle-cuidador"); nodo.hidden = false;
  nodo.innerHTML = `<h2 class="h4">${html(c.nombre)} ${html(c.apellido)}</h2><p>${html(c.condiciones_convivencia || "Sin condiciones de convivencia adicionales.")}</p><h3 class="h6">Disponibilidad publicada</h3>${ds.length ? ds.map(d => `<div class="list-entry d-flex flex-wrap gap-3 justify-content-between align-items-center"><div><strong>${d.modalidad === "VISITA" ? "Visita a domicilio" : "Alojamiento"}</strong><div class="field-note">${fecha(d.fecha_desde)} al ${fecha(d.fecha_hasta)}${d.hora_desde ? ` · ${html(d.hora_desde)}–${html(d.hora_hasta)}` : ""}</div></div>${!usuario || usuario.rol === "DUENO" ? `<button class="btn btn-primary btn-sm" data-reservar="${c.id}" data-modalidad="${d.modalidad}" data-desde="${d.fecha_desde}" data-hasta="${d.fecha_hasta}" data-hora-desde="${d.hora_desde || ""}" data-hora-hasta="${d.hora_hasta || ""}">Solicitar cuidado</button>` : ""}</div>`).join("") : vacio("Aún no hay fechas publicadas", "Volvé a consultar más adelante.")}<p class="field-note mt-3 mb-0">La disponibilidad publicada está sujeta a las reservas aceptadas. El sistema comprueba el cupo al procesar tu solicitud.</p>`;
  nodo.focus(); nodo.scrollIntoView({behavior:"smooth", block:"start"});
}

function cancelarEdicionAgenda() {
  agendaEditada = null; el("form-agenda").reset();
  el("titulo-form-agenda").textContent = "Publicar disponibilidad";
  el("guardar-agenda").textContent = "Publicar"; el("cancelar-agenda").hidden = true;
  actualizarModalidades();
}

async function cargarAgenda() {
  const version = versionSesion;
  let perfil;
  try { perfil = (await api("/api/cuidadores/mi-perfil")).cuidador; }
  catch (e) { if (e.status !== 404) throw e; }
  if (version !== versionSesion) return;
  tienePerfil = Boolean(perfil); el("campos-agenda").disabled = !tienePerfil;
  el("aviso-perfil").textContent = tienePerfil ? "Publicá fechas para que puedan solicitar tus servicios." : "Primero guardá tu perfil para habilitar la agenda.";
  if (!perfil) { el("mis-disponibilidades").innerHTML = vacio("Armá tu perfil", "Después vas a poder publicar tu disponibilidad."); return; }
  const f = el("form-perfil");
  ["descripcion", "condiciones_convivencia", "capacidad_maxima", "tarifa_diaria", "tarifa_visita"].forEach(k => { f.elements[k].value = perfil[k] ?? ""; });
  ["admite_perros", "admite_gatos"].forEach(k => { f.elements[k].checked = perfil[k]; });
  const r = await api("/api/disponibilidades");
  if (version !== versionSesion) return;
  disponibilidades = r.disponibilidades;
  el("mis-disponibilidades").innerHTML = disponibilidades.length ? disponibilidades.map(d => `<div class="list-entry"><strong>${d.modalidad === "VISITA" ? "Visita a domicilio" : "Alojamiento"}</strong><div class="field-note">${fecha(d.fecha_desde)} al ${fecha(d.fecha_hasta)}${d.hora_desde ? ` · ${html(d.hora_desde)}–${html(d.hora_hasta)}` : ""}</div><div class="entry-actions"><button class="btn btn-outline-primary btn-sm" data-editar-agenda="${d.id}">Editar</button><button class="btn btn-outline-danger btn-sm" data-borrar-agenda="${d.id}">Desactivar</button></div></div>`).join("") : vacio("Tu agenda está lista para empezar", "Publicá tu primer período disponible.");
}

function accionesSolicitud(s) {
  const boton = (accion, texto, clase) => `<button class="btn btn-sm ${clase}" data-accion="${accion}" data-id="${s.id}">${texto}</button>`;
  let resultado = "";
  if (usuario?.rol === "CUIDADOR" && s.estado === "PENDIENTE") resultado += boton("aceptar", "Aceptar", "btn-primary") + boton("rechazar", "Rechazar", "btn-outline-danger");
  const inicio = s.modalidad === "VISITA" ? new Date(`${s.fecha_desde}T${s.hora_desde}`) : new Date(`${s.fecha_desde}T00:00:00`);
  const fin = s.modalidad === "VISITA" ? new Date(`${s.fecha_hasta}T${s.hora_hasta}`) : new Date(`${s.fecha_hasta}T00:00:00`);
  if (usuario?.rol === "DUENO" && (s.estado === "PENDIENTE" || (s.estado === "ACEPTADA" && inicio > new Date()))) resultado += boton("cancelar", "Cancelar solicitud", "btn-outline-danger");
  if (usuario?.rol === "CUIDADOR" && s.estado === "ACEPTADA" && fin <= new Date()) resultado += boton("finalizar", "Finalizar servicio", "btn-outline-primary");
  return resultado;
}

function mostrarSolicitudes() {
  const filtro = el("filtro-estado").value;
  const lista = solicitudes.filter(s => !filtro || s.estado === filtro);
  el("lista-solicitudes").innerHTML = lista.length ? lista.map(s => {
    const c = cuidadores.find(c => c.id === s.cuidador_id);
    return `<article class="solicitud-card"><div class="d-flex flex-wrap gap-2 justify-content-between"><strong>${s.modalidad === "VISITA" ? "Visita a domicilio" : "Alojamiento"} · #${s.id}</strong><span class="status status-${html(s.estado.toLowerCase())}">${html(estado(s.estado))}</span></div>${c ? `<p>Cuidador: ${html(c.nombre)} ${html(c.apellido)}</p>` : ""}<p>${fecha(s.fecha_desde)}${s.modalidad === "VISITA" ? ` · ${html(s.hora_desde)}–${html(s.hora_hasta)}` : ` al ${fecha(s.fecha_hasta)} · ${s.noches} noche(s)`}</p><p>${html((s.mascotas || []).map(m => m.nombre).join(", "))} · ${s.total_mascotas} mascota(s)</p><strong>Total: ${dinero(s.monto_total)}</strong><div class="entry-actions">${accionesSolicitud(s)}</div><details><summary>Ver cuidados e historial</summary><dl><dt>Contacto de emergencia</dt><dd>${html(s.contacto_emergencia || "No informado")}</dd><dt>Veterinario</dt><dd>${html(s.veterinario_emergencia || "No informado")}</dd><dt>Atención de urgencia</dt><dd>${s.autorizacion_urgencia ? `Autorizada hasta ${dinero(s.limite_gastos_urgencia)}` : "No autorizada"}</dd>${s.direccion_servicio ? `<dt>Dirección del servicio</dt><dd>${html(s.direccion_servicio)}</dd>` : ""}</dl>${(s.mascotas || []).map(m => `<p><strong>${html(m.nombre)}:</strong> ${html(m.cuidados_especiales || "Sin cuidados especiales registrados.")}</p>`).join("")}<h3 class="h6">Historial</h3><ol>${(s.historial || []).map(h => `<li>${html(estado(h.estado_nuevo))} · ${html(new Date(h.fecha_cambio).toLocaleString("es-AR"))}${h.motivo ? ` · ${html(h.motivo)}` : ""}</li>`).join("")}</ol></details></article>`;
  }).join("") : vacio(filtro ? "No hay solicitudes con ese estado" : "Todavía no hay solicitudes", usuario?.rol === "DUENO" ? "Elegí un cuidador para organizar tu primer servicio." : "Tus solicitudes recibidas van a aparecer acá.", usuario?.rol === "DUENO" ? "#cuidadores" : "", "Buscar cuidadores");
  actualizarP1Solicitudes();
}

async function cargarSolicitudes() {
  const version = versionSesion;
  const r = await api("/api/solicitudes");
  if (version !== versionSesion) return;
  solicitudes = r.solicitudes; mostrarSolicitudes();
}

function actualizarModalidades() {
  const solicitud = el("form-solicitud");
  const visita = solicitud.elements.modalidad.value === "VISITA";
  const grupos = [["[data-solicitud-visita]", visita], ["[data-solicitud-alojamiento]", !visita]];
  grupos.forEach(([selector, mostrar]) => todos(selector).forEach(n => {
    n.hidden = !mostrar; n.querySelectorAll("input").forEach(input => { input.disabled = !mostrar; input.required = mostrar; });
  }));
  el("etiqueta-fecha").firstChild.textContent = visita ? "Fecha de visita" : "Fecha de ingreso";
  const urgencia = solicitud.elements.autorizacion_urgencia.checked;
  todos("[data-urgencia]").forEach(n => { n.hidden = !urgencia; });
  solicitud.elements.limite_gastos_urgencia.disabled = !urgencia;
  solicitud.elements.limite_gastos_urgencia.required = urgencia;
  solicitud.elements.veterinario_emergencia.required = urgencia;
  const agendaVisita = el("form-agenda").elements.modalidad.value === "VISITA";
  todos("[data-agenda-visita]").forEach(n => { n.hidden = !agendaVisita; n.querySelectorAll("input").forEach(input => { input.disabled = !agendaVisita; input.required = agendaVisita; }); });
  estimar();
}

function estimar() {
  const f = el("form-solicitud");
  const c = cuidadores.find(c => String(c.id) === f.elements.cuidador_id.value);
  const cantidad = todos('[name="mascota_id"]:checked').length;
  const visita = f.elements.modalidad.value === "VISITA";
  const noches = Math.round((new Date(`${f.elements.fecha_hasta.value}T12:00:00`) - new Date(`${f.elements.fecha_desde.value}T12:00:00`))/86400000);
  let texto = "Elegí cuidador, fechas y mascotas para estimar el total.";
  if (c && cantidad && f.elements.fecha_desde.value) {
    if (visita) texto = c.tarifa_visita == null ? "Este cuidador no ofrece visitas." : `Total estimado: ${dinero(c.tarifa_visita)} por turno.`;
    else if (noches > 0) texto = `Total estimado: ${dinero(Number(c.tarifa_diaria) * cantidad * noches)} · ${cantidad} mascota(s) × ${noches} noche(s).`;
  }
  el("estimacion").textContent = `${texto} El importe definitivo lo confirma el sistema al enviar.`;
}

function enviar(id, callback) {
  el(id).addEventListener("submit", e => { e.preventDefault(); tarea(() => callback(e.target), e.submitter); });
}

enviar("form-register", async f => {
  await api("/api/auth/register", "POST", datosForm(f.id));
  el("form-login").elements.email.value = f.elements.email.value;
  f.reset(); mensaje("Tu cuenta está creada. Ahora ingresá con tu email y contraseña.");
});
enviar("form-login", async f => {
  await api("/api/auth/login", "POST", datosForm(f.id));
  versionSesion++; await refrescarSesion(); await token(); f.reset();
  location.hash = usuario.rol === "CUIDADOR" ? "agenda" : "mascotas";
});
el("salir").addEventListener("click", e => tarea(async () => {
  await api("/api/auth/logout", "POST"); limpiarSesion(); actualizarAcceso();
  location.hash = "inicio"; await navegar(false); mensaje("Cerraste sesión correctamente.");
}, e.currentTarget));

enviar("form-mascota", async f => {
  const editando = mascotaEditada;
  await api(`/api/mascotas${editando ? `/${editando}` : ""}`, editando ? "PUT" : "POST", datosForm(f.id));
  cancelarEdicionMascota(); await cargarMascotas(); mensaje(editando ? "Datos de tu mascota actualizados." : "Tu mascota ya está registrada.");
});
el("cancelar-mascota").addEventListener("click", cancelarEdicionMascota);
el("recargar-mascotas").addEventListener("click", e => tarea(cargarMascotas, e.currentTarget));
el("lista-mascotas").addEventListener("click", e => {
  const b = e.target.closest("button"); if (!b) return;
  if (b.dataset.editarMascota) {
    const m = mascotas.find(m => m.id === Number(b.dataset.editarMascota));
    mascotaEditada = m.id;
    Object.entries(m).forEach(([k,v]) => { if (el("form-mascota").elements[k]) el("form-mascota").elements[k].value = v ?? ""; });
    el("titulo-form-mascota").textContent = `Editar a ${m.nombre}`;
    el("guardar-mascota").textContent = "Guardar cambios"; el("cancelar-mascota").hidden = false;
    el("form-mascota").elements.nombre.focus();
  }
  if (b.dataset.eliminarMascota) tarea(async () => {
    if (!await confirmar("¿Desactivar esta mascota? Dejará de aparecer para nuevas solicitudes; los servicios anteriores conservarán sus datos.")) return;
    await api(`/api/mascotas/${b.dataset.eliminarMascota}`, "DELETE");
    if (mascotaEditada === Number(b.dataset.eliminarMascota)) cancelarEdicionMascota();
    await cargarMascotas(); mensaje("Mascota desactivada.");
  }, b);
});

enviar("form-buscar", async f => { filtrosInicio = null; el("detalle-cuidador").hidden = true; await cargarCuidadores(datosForm(f.id)); });
el("limpiar-busqueda").addEventListener("click", e => tarea(async () => { el("form-buscar").reset(); filtrosInicio = null; el("detalle-cuidador").hidden = true; await cargarCuidadores(); }, e.currentTarget));
el("lista-cuidadores").addEventListener("click", e => { const b = e.target.closest("[data-detalle]"); if (b) tarea(() => detalleCuidador(b.dataset.detalle), b); });
el("detalle-cuidador").addEventListener("click", e => {
  const b = e.target.closest("[data-reservar]"); if (!b) return;
  if (!usuario) { location.hash = "cuenta"; return; }
  tarea(async () => {
    const d = b.dataset;
    // Cargar las opciones antes de seleccionar y navegar, para conservar el cuidador.
    await cargarCuidadores(); await cargarMascotas();
    const f = el("form-solicitud");
    f.elements.cuidador_id.value = d.reservar; f.elements.modalidad.value = d.modalidad;
    f.elements.fecha_desde.value = d.desde; f.elements.fecha_hasta.value = d.hasta;
    f.elements.hora_desde.value = d.horaDesde; f.elements.hora_hasta.value = d.horaHasta;
    actualizarModalidades(); location.hash = "solicitudes";
  }, b);
});

enviar("form-perfil", async f => {
  const d = datosForm(f.id);
  d.capacidad_maxima = Number(d.capacidad_maxima); d.admite_perros = f.elements.admite_perros.checked; d.admite_gatos = f.elements.admite_gatos.checked;
  d.tarifa_visita = d.tarifa_visita || null;
  await api("/api/cuidadores/mi-perfil", tienePerfil ? "PUT" : "POST", d);
  await cargarAgenda(); mensaje("Tu perfil está actualizado.");
});
enviar("form-agenda", async f => {
  const d = datosForm(f.id), editando = agendaEditada;
  if (d.modalidad === "ALOJAMIENTO") { d.hora_desde = null; d.hora_hasta = null; }
  await api(`/api/disponibilidades${editando ? `/${editando}` : ""}`, editando ? "PUT" : "POST", d);
  cancelarEdicionAgenda(); await cargarAgenda(); mensaje(editando ? "Disponibilidad actualizada." : "Tu disponibilidad está publicada.");
});
el("cancelar-agenda").addEventListener("click", cancelarEdicionAgenda);
el("mis-disponibilidades").addEventListener("click", e => {
  const b = e.target.closest("button"); if (!b) return;
  if (b.dataset.editarAgenda) {
    const d = disponibilidades.find(d => d.id === Number(b.dataset.editarAgenda)); agendaEditada = d.id;
    ["modalidad", "fecha_desde", "fecha_hasta", "hora_desde", "hora_hasta"].forEach(k => { el("form-agenda").elements[k].value = d[k] ?? ""; });
    actualizarModalidades(); el("titulo-form-agenda").textContent = "Editar disponibilidad";
    el("guardar-agenda").textContent = "Guardar cambios"; el("cancelar-agenda").hidden = false; el("form-agenda").elements.modalidad.focus();
  }
  if (b.dataset.borrarAgenda) tarea(async () => {
    if (!await confirmar("¿Desactivar este período de disponibilidad? El sistema impedirá hacerlo si respalda reservas aceptadas.")) return;
    await api(`/api/disponibilidades/${b.dataset.borrarAgenda}`, "DELETE");
    if (agendaEditada === Number(b.dataset.borrarAgenda)) cancelarEdicionAgenda();
    await cargarAgenda(); mensaje("Disponibilidad desactivada.");
  }, b);
});

enviar("form-solicitud", async f => {
  const d = datosForm(f.id), ids = todos('[name="mascota_id"]:checked').map(n => Number(n.value));
  if (!ids.length) throw new Error("Elegí al menos una mascota para el servicio.");
  const base = {cuidador_id:Number(d.cuidador_id), mascotas_ids:ids, contacto_emergencia:d.contacto_emergencia, autorizacion_urgencia:f.elements.autorizacion_urgencia.checked};
  if (d.veterinario_emergencia) base.veterinario_emergencia = d.veterinario_emergencia;
  if (base.autorizacion_urgencia) base.limite_gastos_urgencia = d.limite_gastos_urgencia;
  const visita = d.modalidad === "VISITA";
  const datos = visita ? {...base, fecha:d.fecha_desde, hora_desde:d.hora_desde, hora_hasta:d.hora_hasta, direccion_servicio:d.direccion_servicio} : {...base, modalidad:"ALOJAMIENTO", fecha_desde:d.fecha_desde, fecha_hasta:d.fecha_hasta};
  const r = await api(visita ? "/api/visitas" : "/api/solicitudes", "POST", datos);
  f.reset(); actualizarModalidades(); await cargarSolicitudes();
  mensaje(`Solicitud enviada. Total: ${dinero(r.solicitud.monto_total)}. Podés seguir la respuesta en Mis servicios.`);
});
el("recargar-solicitudes").addEventListener("click", e => tarea(cargarSolicitudes, e.currentTarget));
el("filtro-estado").addEventListener("change", mostrarSolicitudes);
el("lista-solicitudes").addEventListener("click", e => {
  const b = e.target.closest("[data-accion]"); if (!b) return;
  tarea(async () => {
    const textos = {aceptar:"¿Aceptar esta solicitud? Se comprobará la disponibilidad y se reservará el cupo.", rechazar:"¿Rechazar esta solicitud?", cancelar:"¿Cancelar esta solicitud? Se liberará el cupo si ya estaba aceptada.", finalizar:"¿Confirmar que el servicio terminó?"};
    if (!await confirmar(textos[b.dataset.accion])) return;
    await api(`/api/solicitudes/${b.dataset.id}/${b.dataset.accion}`, "POST");
    await cargarSolicitudes(); mensaje("El estado de la solicitud se actualizó correctamente.");
  }, b);
});
el("form-solicitud").addEventListener("change", actualizarModalidades);
el("form-solicitud").addEventListener("input", estimar);
el("form-agenda").elements.modalidad.addEventListener("change", actualizarModalidades);
window.addEventListener("hashchange", () => tarea(navegar));

// La fecha local evita adelantar el mínimo por diferencias con UTC.
todos('input[type="date"]').forEach(n => { if (n.name === "fecha_nacimiento") n.max = hoy(); else n.min = hoy(); });
actualizarModalidades();
tarea(async () => { await token(); await refrescarSesion(); await navegar(false); });

// Buscador de portada: conserva los filtros y consulta la disponibilidad publicada.
function actualizarBuscadorInicio() {
  const f = el("form-inicio"), visita = f.elements.modalidad.value === "VISITA";
  el("inicio-hasta-label").hidden = visita;
  f.elements.fecha_hasta.disabled = visita;
  el("inicio-desde-texto").textContent = visita ? "Día de visita" : "Desde";
  el("inicio-error-fechas").hidden = true;
}
enviar("form-inicio", async f => {
  const d = datosForm(f.id), error = el("inicio-error-fechas");
  let texto = "";
  if (d.fecha_desde && d.fecha_desde < hoy()) texto = "Elegí una fecha a partir de hoy.";
  if (d.modalidad === "ALOJAMIENTO" && Boolean(d.fecha_desde) !== Boolean(d.fecha_hasta)) texto = "Completá el ingreso y la salida, o dejá ambas fechas vacías.";
  if (d.modalidad === "ALOJAMIENTO" && d.fecha_desde && d.fecha_hasta <= d.fecha_desde) texto = "La salida debe ser posterior al ingreso: al menos una noche.";
  if (texto) { error.textContent = texto; error.hidden = false; return; }
  filtrosInicio = d;
  el("form-buscar").elements.provincia.value = d.provincia.trim();
  el("form-buscar").elements.localidad.value = d.localidad.trim();
  el("detalle-cuidador").hidden = true;
  location.hash = "cuidadores";
});
el("form-inicio").addEventListener("change", actualizarBuscadorInicio);
actualizarBuscadorInicio();
