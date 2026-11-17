
"use strict";

const $ = id => document.getElementById(id);

let seccion = "usuarios";
let pagina = 1;
let paginas = 1;
let csrf = "";

let detalleActual = null;
let paginaHistorial = 1;
let paginasHistorial = 1;

const columnas = {
  usuarios: [
    "ID", "Nombre", "Correo", "Ubicación",
    "Estado", "Acciones"
  ],
  cuidadores: [
    "ID", "Cuidador", "Correo", "Ubicación",
    "Capacidad", "Estado", "Acciones"
  ]
};

function mensaje(texto, error = false) {
  $("mensaje").textContent = texto;
  $("mensaje").className = error ? "error" : "";
}

async function api(ruta, opciones = {}) {
  const respuesta = await fetch(ruta, {
    credentials: "same-origin",
    ...opciones
  });

  const datos = await respuesta.json().catch(() => ({}));

  if (!respuesta.ok) {
    throw new Error(
      datos.error || `Error HTTP ${respuesta.status}`
    );
  }

  return datos;
}

function crearElemento(etiqueta, texto = "", clase = "") {
  const elemento = document.createElement(etiqueta);
  elemento.textContent = texto;

  if (clase) {
    elemento.className = clase;
  }

  return elemento;
}

function celda(fila, contenido) {
  const td = crearElemento(
    "td",
    contenido == null ? "-" : String(contenido)
  );

  fila.appendChild(td);
  return td;
}

function boton(texto, accion, clase = "") {
  const elemento = crearElemento("button", texto, clase);
  elemento.type = "button";
  elemento.addEventListener("click", accion);
  return elemento;
}

function valor(contenido) {
  if (
    contenido === null ||
    contenido === undefined ||
    contenido === ""
  ) {
    return "-";
  }

  if (typeof contenido === "boolean") {
    return contenido ? "Sí" : "No";
  }

  return String(contenido);
}

function fecha(texto) {
  if (!texto) {
    return "-";
  }

  return texto.replace("T", " ").slice(0, 19);
}

function estadoVisual(activo) {
  return crearElemento(
    "span",
    activo ? "Activo" : "Inactivo",
    activo ? "estado activo" : "estado inactivo"
  );
}

function dato(contenedor, etiqueta, contenido) {
  const div = crearElemento("div", "", "dato");

  div.appendChild(
    crearElemento("span", etiqueta, "dato-etiqueta")
  );

  div.appendChild(
    crearElemento("strong", valor(contenido))
  );

  contenedor.appendChild(div);
}

function metrica(nombre, cantidad) {
  const nombres = {
    usuarios: "Usuarios registrados",
    usuarios_activos: "Usuarios activos",
    cuidadores: "Cuidadores",
    mascotas: "Mascotas",
    solicitudes: "Solicitudes",
    solicitudes_pendientes: "Solicitudes pendientes",
    incidencias: "Incidencias",
    incidencias_abiertas: "Incidencias abiertas",
    valoraciones: "Valoraciones"
  };

  const div = crearElemento("div", "", "metrica");

  div.appendChild(
    crearElemento("strong", String(cantidad))
  );

  div.appendChild(
    crearElemento("span", nombres[nombre] || nombre)
  );

  $("metricas").appendChild(div);
}

async function cargarResumen() {
  const datos = await api("/admin/api/resumen");

  $("metricas").replaceChildren();

  Object.entries(datos).forEach(([nombre, cantidad]) => {
    metrica(nombre, cantidad);
  });
}

async function cambiarEstado(usuarioId, email, activo) {
  const accion = activo ? "desactivar" : "activar";

  const motivo = await pedirMotivoCuenta(accion, email);
  if (motivo === null) return;

  try {
    await api(
      `/admin/api/usuarios/${usuarioId}/estado`,
      {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrf
        },
        body: JSON.stringify({
          activo: !activo,
          motivo
        })
      }
    );

    mensaje("Estado de la cuenta actualizado correctamente.");

    await cargarResumen();

    if (detalleActual) {
      await abrirDetalle(
        detalleActual.tipo,
        detalleActual.id,
        false
      );
    } else {
      await cargarListado();
    }
  } catch (error) {
    mensaje(error.message, true);
  }
}

function agregarAcciones(fila, item) {
  const td = document.createElement("td");

  const tipo = seccion === "usuarios"
    ? "dueno"
    : "cuidador";

  td.appendChild(
    boton(
      "Ver detalle",
      () => abrirDetalle(tipo, item.id),
      "boton-secundario"
    )
  );

  const usuarioId = seccion === "usuarios"
    ? item.id
    : item.usuario_id;

  td.appendChild(
    boton(
      item.activo ? "Desactivar" : "Activar",
      () => cambiarEstado(
        usuarioId,
        item.email,
        item.activo
      ),
      item.activo ? "boton-peligro" : "boton-exito"
    )
  );

  fila.appendChild(td);
}

async function cargarListado() {
  const seccionSolicitada = seccion;

  try {
    const parametros = new URLSearchParams({
      pagina: String(pagina)
    });

    if (seccionSolicitada === "usuarios") {
      // El backend filtra ANTES de paginar.
      parametros.set("rol", "DUENO");

      const busqueda = $("buscar").value.trim();

      if (busqueda) {
        parametros.set("buscar", busqueda);
      }
    }

    const datos = await api(
      `/admin/api/${seccionSolicitada}?${parametros}`
    );

    if (seccionSolicitada !== seccion) {
      return;
    }

    paginas = datos.paginas;

    $("encabezados").replaceChildren();

    const encabezado = document.createElement("tr");

    columnas[seccion].forEach(titulo => {
      encabezado.appendChild(
        crearElemento("th", titulo)
      );
    });

    $("encabezados").appendChild(encabezado);
    $("filas").replaceChildren();

    // Los registros ya llegan filtrados desde el backend.
    for (const item of datos.items) {
      const fila = document.createElement("tr");

      if (seccion === "usuarios") {
        celda(fila, item.id);
        celda(fila, `${item.nombre} ${item.apellido}`);
        celda(fila, item.email);
        celda(
          fila,
          `${item.localidad}, ${item.provincia}`
        );
      } else {
        celda(fila, item.id);
        celda(fila, item.nombre);
        celda(fila, item.email);
        celda(
          fila,
          `${item.localidad}, ${item.provincia}`
        );
        celda(fila, item.capacidad);
      }

      const tdEstado = document.createElement("td");
      tdEstado.appendChild(estadoVisual(item.activo));
      fila.appendChild(tdEstado);

      agregarAcciones(fila, item);
      [...fila.cells].forEach((celda, indice) => {
        celda.dataset.label = columnas[seccion][indice];
      });
      $("filas").appendChild(fila);
    }

    if (!datos.items.length) {
      const fila = document.createElement("tr");

      const td = crearElemento(
        "td",
        "No se encontraron registros."
      );

      td.colSpan = columnas[seccion].length;
      fila.appendChild(td);
      $("filas").appendChild(fila);
    }

    $("pagina").textContent =
      `Página ${datos.pagina} de ${paginas || 1} · ` +
      `${datos.total} registros`;

    $("anterior").disabled = pagina <= 1;
    $("siguiente").disabled = pagina >= paginas;

  } catch (error) {
    mensaje(error.message, true);
  }
}

function seleccionar(nombre) {
  seccion = nombre;
  pagina = 1;
  detalleActual = null;

  $("panel-listado").hidden = false;
  $("panel-detalle").hidden = true;

  $("titulo").textContent = nombre === "usuarios"
    ? "Dueños registrados"
    : "Cuidadores registrados";

  $("descripcion-seccion").textContent =
    nombre === "usuarios"
      ? "Gestión de cuentas, mascotas y solicitudes."
      : "Gestión de cuidadores, servicios e incidencias.";

  $("buscar").hidden = nombre !== "usuarios";
  $("filtrar").hidden = nombre !== "usuarios";

  document.querySelectorAll("[data-seccion]").forEach(elemento => {
    if (elemento.dataset.seccion === nombre) {
      elemento.setAttribute("aria-current", "page");
    } else {
      elemento.removeAttribute("aria-current");
    }
  });

  mensaje("");
  cargarListado();
}

function mostrarCuenta(datos) {
  const contenedor = $("datos-cuenta");
  contenedor.replaceChildren();

  dato(
    contenedor,
    "Nombre",
    `${datos.nombre} ${datos.apellido}`
  );
  dato(contenedor, "Correo", datos.email);
  dato(contenedor, "Teléfono", datos.telefono);
  dato(contenedor, "Provincia", datos.provincia);
  dato(contenedor, "Localidad", datos.localidad);
  dato(
    contenedor,
    "Fecha de registro",
    fecha(datos.fecha_registro)
  );
  dato(
    contenedor,
    "Estado",
    datos.activo ? "Activo" : "Inactivo"
  );
}

function mostrarPerfil(datos) {
  const contenedor = $("datos-perfil");
  contenedor.replaceChildren();

  dato(contenedor, "Descripción", datos.descripcion);
  dato(
    contenedor,
    "Capacidad máxima",
    datos.capacidad_maxima
  );
  dato(contenedor, "Admite perros", datos.admite_perros);
  dato(contenedor, "Admite gatos", datos.admite_gatos);
  dato(
    contenedor,
    "Condiciones",
    datos.condiciones_convivencia
  );
  dato(
    contenedor,
    "Tarifa diaria",
    datos.tarifa_diaria
  );
  dato(
    contenedor,
    "Tarifa por visita",
    datos.tarifa_visita
  );
}

function mostrarMascotas(mascotas) {
  const contenedor = $("lista-mascotas");
  contenedor.replaceChildren();

  if (!mascotas.length) {
    contenedor.appendChild(
      crearElemento("p", "No hay mascotas registradas.")
    );
    return;
  }

  mascotas.forEach(mascota => {
    const tarjeta = crearElemento(
      "article",
      "",
      "tarjeta"
    );

    tarjeta.appendChild(
      crearElemento("h4", mascota.nombre)
    );

    const datos = crearElemento("div", "", "datos-grid");

    dato(datos, "Especie", mascota.especie);
    dato(datos, "Raza", mascota.raza);
    dato(datos, "Tamaño", mascota.tamano);
    dato(
      datos,
      "Nacimiento",
      mascota.fecha_nacimiento
    );
    dato(
      datos,
      "Cuidados especiales",
      mascota.cuidados_especiales
    );
    dato(
      datos,
      "Veterinario",
      mascota.contacto_veterinario
    );
    dato(
      datos,
      "Estado",
      mascota.activo ? "Activa" : "Inactiva"
    );

    tarjeta.appendChild(datos);
    contenedor.appendChild(tarjeta);
  });
}

function mostrarCambios(historial, contenedor) {
  if (!historial || !historial.length) {
    return;
  }

  const bloque = crearElemento(
    "div",
    "",
    "subbloque"
  );

  bloque.appendChild(
    crearElemento("h5", "Historial de estados")
  );

  historial.forEach(cambio => {
    const texto =
      `${fecha(cambio.fecha_cambio)} · ` +
      `${valor(cambio.estado_anterior)} → ` +
      `${cambio.estado_nuevo}` +
      (cambio.motivo ? ` · ${cambio.motivo}` : "");

    bloque.appendChild(
      crearElemento("p", texto)
    );
  });

  contenedor.appendChild(bloque);
}

function mostrarIncidencias(incidencias, contenedor) {
  if (!incidencias || !incidencias.length) {
    contenedor.appendChild(
      crearElemento(
        "p",
        "Sin incidencias registradas."
      )
    );
    return;
  }

  const bloque = crearElemento(
    "div",
    "",
    "subbloque"
  );

  bloque.appendChild(
    crearElemento("h5", "Incidencias")
  );

  incidencias.forEach(incidencia => {
    const tarjeta = crearElemento(
      "article",
      "",
      "incidencia"
    );

    tarjeta.appendChild(
      crearElemento(
        "strong",
        `${incidencia.tipo} · ${incidencia.estado}`
      )
    );

    const datos = crearElemento(
      "div",
      "",
      "datos-grid"
    );

    dato(
      datos,
      "Fecha",
      fecha(incidencia.fecha)
    );
    dato(
      datos,
      "Descripción",
      incidencia.descripcion
    );
    dato(
      datos,
      "Medidas tomadas",
      incidencia.medidas_tomadas
    );
    dato(
      datos,
      "Comentario de cierre",
      incidencia.comentario_cierre
    );

    tarjeta.appendChild(datos);
    bloque.appendChild(tarjeta);
  });

  contenedor.appendChild(bloque);
}

function mostrarHistorial(items) {
  const contenedor = $("lista-historial");
  contenedor.replaceChildren();

  if (!items.length) {
    contenedor.appendChild(
      crearElemento(
        "p",
        "No hay registros en el historial."
      )
    );
    return;
  }

  items.forEach(item => {
    const tarjeta = crearElemento(
      "article",
      "",
      "tarjeta"
    );

    tarjeta.appendChild(
      crearElemento(
        "h4",
        `Solicitud #${item.id} · ${item.estado}`
      )
    );

    const datos = crearElemento(
      "div",
      "",
      "datos-grid"
    );

    dato(datos, "Modalidad", item.modalidad);
    dato(datos, "Desde", item.fecha_desde);
    dato(datos, "Hasta", item.fecha_hasta);
    dato(datos, "Hora desde", item.hora_desde);
    dato(datos, "Hora hasta", item.hora_hasta);
    dato(
      datos,
      "Cantidad de mascotas",
      item.total_mascotas
    );
    dato(
      datos,
      "Importe total",
      item.monto_total
    );

    if (detalleActual.tipo === "dueno") {
      dato(
        datos,
        "Cuidador",
        item.cuidador ? item.cuidador.nombre : "-"
      );

      dato(
        datos,
        "Mascotas",
        (item.mascotas || [])
          .map(mascota => mascota.nombre)
          .join(", ")
      );
    } else {
      dato(
        datos,
        "Dueño",
        item.dueno ? item.dueno.nombre : "-"
      );
    }

    tarjeta.appendChild(datos);

    mostrarCambios(
      item.historial_estados,
      tarjeta
    );

    if (detalleActual.tipo === "cuidador") {
      mostrarIncidencias(
        item.incidencias,
        tarjeta
      );
    }

    contenedor.appendChild(tarjeta);
  });
}

async function cargarHistorial() {
  if (!detalleActual) {
    return;
  }

  const ruta = detalleActual.tipo === "dueno"
    ? `/admin/api/duenos/${detalleActual.id}/solicitudes`
    : `/admin/api/cuidadores/${detalleActual.id}/servicios`;

  try {
    const datos = await api(
      `${ruta}?pagina=${paginaHistorial}`
    );

    paginasHistorial = datos.paginas;

    mostrarHistorial(datos.items);

    $("historial-pagina").textContent =
      `Página ${datos.pagina} de ${paginasHistorial || 1} · ` +
      `${datos.total} registros`;

    $("historial-anterior").disabled =
      paginaHistorial <= 1;

    $("historial-siguiente").disabled =
      paginaHistorial >= paginasHistorial;

  } catch (error) {
    mensaje(error.message, true);
  }
}

async function abrirDetalle(tipo, id, reiniciarPagina = true) {
  try {
    const ruta = tipo === "dueno"
      ? `/admin/api/duenos/${id}`
      : `/admin/api/cuidadores/${id}`;

    const datos = await api(ruta);

    detalleActual = { tipo, id };

    if (reiniciarPagina) {
      paginaHistorial = 1;
    }

    $("panel-listado").hidden = true;
    $("panel-detalle").hidden = false;

    $("titulo-detalle").textContent =
      `${datos.nombre} ${datos.apellido}`;

    $("subtitulo-detalle").textContent =
      tipo === "dueno"
        ? "Detalle del dueño registrado"
        : "Detalle del cuidador registrado";

    mostrarCuenta(datos);
    await cargarAuditoriaCuenta(tipo === "dueno" ? datos.id : datos.usuario_id);

    $("bloque-perfil").hidden =
      tipo !== "cuidador";

    $("bloque-mascotas").hidden =
      tipo !== "dueno";

    if (tipo === "dueno") {
      mostrarMascotas(datos.mascotas);
    } else {
      mostrarPerfil(datos);
    }

    $("titulo-historial").textContent =
      tipo === "dueno"
        ? "Historial de solicitudes"
        : "Historial de servicios e incidencias";

    const acciones = $("acciones-detalle");
    acciones.replaceChildren();

    acciones.appendChild(
      boton(
        datos.activo
          ? "Desactivar cuenta"
          : "Activar cuenta",
        () => cambiarEstado(
          tipo === "dueno"
            ? datos.id
            : datos.usuario_id,
          datos.email,
          datos.activo
        ),
        datos.activo
          ? "boton-peligro"
          : "boton-exito"
      )
    );

    await cargarHistorial();

  } catch (error) {
    mensaje(error.message, true);
  }
}

function volverListado() {
  detalleActual = null;

  $("panel-detalle").hidden = true;
  $("panel-listado").hidden = false;

  cargarListado();
}

document.addEventListener("DOMContentLoaded", async () => {
  document.querySelectorAll("[data-seccion]").forEach(elemento => {
    elemento.addEventListener(
      "click",
      () => seleccionar(elemento.dataset.seccion)
    );
  });

  $("filtrar").addEventListener("click", () => {
    pagina = 1;
    cargarListado();
  });

  $("buscar").addEventListener("keydown", evento => {
    if (evento.key === "Enter") {
      pagina = 1;
      cargarListado();
    }
  });

  $("anterior").addEventListener("click", () => {
    if (pagina > 1) {
      pagina--;
      cargarListado();
    }
  });

  $("siguiente").addEventListener("click", () => {
    if (pagina < paginas) {
      pagina++;
      cargarListado();
    }
  });

  $("volver-listado").addEventListener(
    "click",
    volverListado
  );

  $("historial-anterior").addEventListener("click", () => {
    if (paginaHistorial > 1) {
      paginaHistorial--;
      cargarHistorial();
    }
  });

  $("historial-siguiente").addEventListener("click", () => {
    if (paginaHistorial < paginasHistorial) {
      paginaHistorial++;
      cargarHistorial();
    }
  });

  try {
    const token = await api("/api/auth/csrf-token");
    csrf = token.csrf_token;

    await cargarResumen();
    seleccionar("usuarios");

  } catch (error) {
    mensaje(error.message, true);
  }
});

// El atajo conserva la pestaña, la página y los filtros administrativos.
function actualizarVolverArriba() {
  $("volver-arriba").hidden = window.scrollY < 400;
}
window.addEventListener("scroll", actualizarVolverArriba, {passive: true});
window.addEventListener("pageshow", actualizarVolverArriba);
$("volver-arriba").addEventListener("click", () => {
  document.querySelector(".marca a").focus({preventScroll: true});
  const reducirMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.scrollTo({top: 0, behavior: reducirMovimiento ? "instant" : "smooth"});
});
actualizarVolverArriba();

function pedirMotivoCuenta(accion, email) {
  const dialogo = $("cambio-cuenta");
  if (dialogo.open) return Promise.resolve(null);
  const origen = document.activeElement;
  $("form-cambio-cuenta").reset();
  $("motivo-cuenta").setCustomValidity("");
  $("cambio-cuenta-texto").textContent = `Vas a ${accion} la cuenta ${email}. El motivo y tu identidad quedarán registrados.`;
  dialogo.returnValue = "";
  return new Promise(resolve => {
    dialogo.addEventListener("close", () => {
      origen?.focus({preventScroll: true});
      resolve(dialogo.returnValue === "confirmar" ? $("motivo-cuenta").value.trim() : null);
    }, {once: true});
    dialogo.showModal();
    $("motivo-cuenta").focus();
  });
}
$("form-cambio-cuenta").addEventListener("submit", event => {
  event.preventDefault();
  const campo = $("motivo-cuenta");
  campo.setCustomValidity(campo.value.trim() ? "" : "Indicá el motivo del cambio.");
  if (campo.reportValidity()) $("cambio-cuenta").close("confirmar");
});
$("motivo-cuenta").addEventListener("input", () => $("motivo-cuenta").setCustomValidity(""));
$("cancelar-cambio-cuenta").addEventListener("click", () => $("cambio-cuenta").close("cancelar"));

async function cargarAuditoriaCuenta(usuarioId, pagina = 1) {
  const contenedor = $("auditoria-cuenta");
  contenedor.textContent = "Consultando cambios de estado…";
  const datos = await api(`/admin/api/usuarios/${usuarioId}/auditoria?pagina=${pagina}`);
  contenedor.replaceChildren();
  if (!datos.items.length) {
    contenedor.appendChild(crearElemento("p", "No hay cambios registrados desde la incorporación de este historial."));
    return;
  }
  for (const cambio of datos.items) {
    const tarjeta = crearElemento("article", "", "tarjeta");
    tarjeta.appendChild(crearElemento("h4", `${cambio.activo_anterior ? "Activa" : "Inactiva"} → ${cambio.activo_nuevo ? "Activa" : "Inactiva"}`));
    tarjeta.appendChild(crearElemento("p", cambio.motivo));
    const fechaLocal = new Date(cambio.fecha_cambio).toLocaleString("es-AR", {timeZone: "America/Argentina/Buenos_Aires"});
    tarjeta.appendChild(crearElemento("p", `${cambio.administrador} · ID ${cambio.administrador_id} · ${fechaLocal} (Argentina)`));
    contenedor.appendChild(tarjeta);
  }
  if (datos.paginas > 1) {
    const controles = crearElemento("div", "", "paginacion");
    const anterior = boton("Anterior", () => cargarAuditoriaCuenta(usuarioId, pagina - 1).catch(e => mensaje(e.message, true)));
    anterior.disabled = pagina <= 1;
    const siguiente = boton("Siguiente", () => cargarAuditoriaCuenta(usuarioId, pagina + 1).catch(e => mensaje(e.message, true)));
    siguiente.disabled = pagina >= datos.paginas;
    controles.append(anterior, crearElemento("span", `Página ${pagina} de ${datos.paginas}`), siguiente);
    contenedor.appendChild(controles);
  }
}
