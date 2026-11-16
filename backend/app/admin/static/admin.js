"use strict";
const $ = id => document.getElementById(id);
let seccion = "usuarios";
let pagina = 1;
let paginas = 1;
let csrf = "";

const columnas = {
  usuarios: ["ID","Nombre","Correo","Rol","Ubicacion","Estado","Accion"],
  cuidadores: ["ID","Cuidador","Correo","Ubicacion","Capacidad","Tarifa diaria","Estado"],
  solicitudes: ["ID","Due?o ID","Cuidador ID","Modalidad","Desde","Hasta","Estado"],
  incidencias: ["ID","Solicitud ID","Tipo","Descripcion","Fecha","Estado"]
};

function mensaje(texto, error=false) {
  $("mensaje").textContent = texto;
  $("mensaje").className = error ? "error" : "";
}

async function api(ruta, opciones={}) {
  const respuesta = await fetch(ruta, {
    credentials: "same-origin",
    ...opciones
  });
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) throw new Error(datos.error || `Error HTTP ${respuesta.status}`);
  return datos;
}

function celda(fila, valor) {
  const td = document.createElement("td");
  td.textContent = valor == null ? "-" : String(valor);
  fila.appendChild(td);
  return td;
}

function metrica(nombre, valor) {
  const div = document.createElement("div");
  div.className = "metrica";
  const strong = document.createElement("strong");
  strong.textContent = valor;
  const span = document.createElement("span");
  span.textContent = nombre.replaceAll("_", " ");
  div.append(strong, span);
  $("metricas").appendChild(div);
}

async function resumen() {
  const datos = await api("/admin/api/resumen");
  $("metricas").replaceChildren();
  Object.entries(datos).forEach(([nombre, valor]) => metrica(nombre, valor));
}

function valores(item) {
  switch(seccion) {
    case "usuarios": return [
      item.id, `${item.nombre} ${item.apellido}`, item.email,
      item.rol, `${item.localidad}, ${item.provincia}`,
      item.activo ? "Activo" : "Inactivo"
    ];
    case "cuidadores": return [
      item.id,item.nombre,item.email,
      `${item.localidad}, ${item.provincia}`,item.capacidad,
      item.tarifa_diaria,item.activo ? "Activo" : "Inactivo"
    ];
    case "solicitudes": return [
      item.id,item.dueno_id,item.cuidador_id,item.modalidad,
      item.fecha_desde,item.fecha_hasta,item.estado
    ];
    default: return [
      item.id,item.solicitud_id,item.tipo,item.descripcion,
      item.fecha,item.estado
    ];
  }
}

async function cambiarEstado(item) {
  const accion = item.activo ? "desactivar" : "activar";
  if (!confirm(`?Confirmar ${accion} la cuenta ${item.email}?`)) return;
  try {
    await api(`/admin/api/usuarios/${item.id}/estado`, {
      method: "PATCH",
      headers: {"Content-Type":"application/json","X-CSRFToken":csrf},
      body: JSON.stringify({activo: !item.activo})
    });
    mensaje("Cuenta actualizada correctamente.");
    await Promise.all([cargar(), resumen()]);
  } catch(error) {
    mensaje(error.message,true);
  }
}

async function cargar() {
  try {
    const parametros = new URLSearchParams({pagina: String(pagina)});
    if (seccion === "usuarios" && $("buscar").value.trim()) {
      parametros.set("buscar", $("buscar").value.trim());
    }
    if (["solicitudes","incidencias"].includes(seccion) && $("estado").value) {
      parametros.set("estado", $("estado").value);
    }
    const datos = await api(`/admin/api/${seccion}?${parametros}`);
    paginas = datos.paginas;
    $("encabezados").replaceChildren();
    const encabezado = document.createElement("tr");
    columnas[seccion].forEach(titulo => {
      const th = document.createElement("th");
      th.textContent = titulo;
      encabezado.appendChild(th);
    });
    $("encabezados").appendChild(encabezado);
    $("filas").replaceChildren();

    for (const item of datos.items) {
      const fila = document.createElement("tr");
      valores(item).forEach(valor => celda(fila,valor));
      if (seccion === "usuarios") {
        const td = document.createElement("td");
        if (item.rol !== "ADMIN") {
          const boton = document.createElement("button");
          boton.textContent = item.activo ? "Desactivar" : "Activar";
          boton.addEventListener("click", () => cambiarEstado(item));
          td.appendChild(boton);
        }
        fila.appendChild(td);
      }
      $("filas").appendChild(fila);
    }
    if (!datos.items.length) {
      const fila = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = columnas[seccion].length;
      td.textContent = "No se encontraron registros.";
      fila.appendChild(td);
      $("filas").appendChild(fila);
    }
    $("pagina").textContent = `Pagina ${datos.pagina} de ${paginas || 1} ? ${datos.total} registros`;
    $("anterior").disabled = pagina <= 1;
    $("siguiente").disabled = pagina >= paginas;
  } catch(error) {
    mensaje(error.message,true);
  }
}

function seleccionar(nombre) {
  seccion = nombre;
  pagina = 1;
  $("titulo").textContent = nombre[0].toUpperCase()+nombre.slice(1);
  $("buscar").hidden = nombre !== "usuarios";
  $("estado").hidden = !["solicitudes","incidencias"].includes(nombre);
  $("estado").replaceChildren();
  const opciones = nombre === "solicitudes"
    ? ["","PENDIENTE","ACEPTADA","RECHAZADA","CANCELADA","FINALIZADA"]
    : nombre === "incidencias" ? ["","ABIERTA","RESUELTA"] : [""];
  opciones.forEach(valor => {
    const opcion = document.createElement("option");
    opcion.value = valor;
    opcion.textContent = valor || "Todos los estados";
    $("estado").appendChild(opcion);
  });
  document.querySelectorAll("[data-seccion]").forEach(boton => {
    if (boton.dataset.seccion === nombre) boton.setAttribute("aria-current","page");
    else boton.removeAttribute("aria-current");
  });
  mensaje("");
  cargar();
}

document.addEventListener("DOMContentLoaded", async () => {
  document.querySelectorAll("[data-seccion]").forEach(boton => {
    boton.addEventListener("click", () => seleccionar(boton.dataset.seccion));
  });
  $("filtrar").addEventListener("click", () => {pagina=1;cargar();});
  $("buscar").addEventListener("keydown", evento => {
    if (evento.key === "Enter") {pagina=1;cargar();}
  });
  $("anterior").addEventListener("click", () => {pagina--;cargar();});
  $("siguiente").addEventListener("click", () => {pagina++;cargar();});
  try {
    const token = await api("/api/auth/csrf-token");
    csrf = token.csrf_token;
    await resumen();
    seleccionar("usuarios");
  } catch(error) {
    mensaje(error.message,true);
  }
});
