# Validación de producción — 17/11/2026

## Versión y entorno

- URL: https://cuidando-peluditos.onrender.com/.
- Rama de despliegue: `deploy/render`; commit `dce4785`.
- Render confirmó Deploy succeeded / Live en el despliegue manual del 17/11/2026, iniciado a las 15:49:18 GMT-3: [captura](evidencias/validacion-produccion-2026-11-17/01-despliegue-dce4785-live.png).
- Consulta de solo lectura a TiDB mediante PyMySQL con verificación TLS: base `cuidandopeluditos`, revisión `e72a91c4b603`, existencia de `auditoria_cuentas` confirmada. Antes del despliegue la revisión era `d18a6c2f904b` y la tabla no existía.
- Build Command configurado: `pip install -r backend/requirements.txt && FLASK_ENV=prod python -m flask --app backend.run:app db upgrade --directory backend/migrations`.
- Start Command conservado: `gunicorn --bind 0.0.0.0:$PORT backend.run:app`.
- Auto-Deploy se dejó temporalmente en Off durante la revisión. Su restauración a On Commit está pendiente al cerrar las pruebas.

## ADMIN: cambios de estado de cuenta

Se abrió el panel ADMIN y el detalle de la cuenta ficticia Tomás Aguirre (`demo-cp-2026-dueno-20@example.com`), inicialmente activa y sin solicitudes. El historial administrativo estaba vacío: [captura](evidencias/validacion-produccion-2026-11-17/02-cuenta-ficticia-sin-auditoria.png).

1. Se desactivó con motivo «Prueba de auditoría en producción con cuenta ficticia». Se mostró estado Inactivo y el registro Activa → Inactiva, responsable Administrador Sistema (ID 90001), con fecha y hora: [captura](evidencias/validacion-produccion-2026-11-17/03-desactivacion-auditada.png).
2. Se reactivó con motivo «Reactivación al finalizar la prueba de auditoría». Se mostró Inactiva → Activa, conservando el registro anterior y el responsable: [captura](evidencias/validacion-produccion-2026-11-17/04-reactivacion-historial-conservado.png).
3. Tras F5 y volver a abrir el detalle, ambos registros permanecieron. Se confirmó que la cuenta terminó activa.

Resultado: recorrido de desactivación y reactivación con auditoría aprobado en producción. Las horas visualizadas en los registros no se utilizaron para validar sincronización de reloj ni zona horaria en esta prueba.

Observación de navegación: F5 vuelve al listado del panel; el detalle abierto no se conserva. No se perdieron los registros. Mantener el detalle al recargar queda anotado como mejora pendiente, no como una corrección realizada.

## Recorridos pendientes

Contactos por participante y estado, dirección privada de alojamiento, franjas de visita, precios, cupos, incidencias, finalización y valoración sobre esta versión publicada. La suite de 104 pruebas aisladas y las evidencias locales no sustituyen estos recorridos de producción.

## Alojamiento, contactos y liberación de cupo

Se registró la cuenta ficticia Camila Prueba (`cuidador.validacion.1711@example.com`) y se guardó su perfil con capacidad de 3, tarifa de alojamiento de $12.000 por mascota/noche y dirección privada «Domicilio ficticio de prueba 123». Se confirmó la publicación de disponibilidad del 25/11/2026 al 28/11/2026.

La solicitud #120001 incluyó a Otis, una mascota, del 25/11/2026 al 26/11/2026. La creación confirmó un total de $12.000 y se observó el contador de un pendiente. El recorrido se realizó en la versión publicada `dce4785`, conectada a TiDB.

| Comprobación | Resultado |
|---|---|
| Solicitud pendiente | Contactos de coordinación ocultos para dueño y cuidador. [Captura del dueño](evidencias/validacion-produccion-2026-11-17/05-alojamiento-pendiente-sin-contactos.png). |
| Aceptación por Camila | Estado ACEPTADA. El cuidador pudo consultar los contactos del dueño y la dirección acordada. No se incorpora la captura de esos contactos personales al repositorio. |
| Consulta del dueño tras aceptar | Nombre, teléfono ficticio y email de Camila visibles, junto con la misma dirección acordada. [Captura](evidencias/validacion-produccion-2026-11-17/06-contactos-cuidador-tras-aceptar.png). |
| Ocupación por noche | 25 al 26/11: 2 plazas libres; 26 al 28/11: 3 plazas libres. La reserva de una noche no ocupa el resto del período. [Captura](evidencias/validacion-produccion-2026-11-17/07-cupos-por-noche-aceptada.png). |
| Cancelación por el dueño | Estado CANCELADA y contactos de coordinación ocultos en su pantalla. [Captura](evidencias/validacion-produccion-2026-11-17/08-cancelada-sin-contactos.png). |
| Consulta pública posterior | Un tramo del 25 al 28/11 con 3 plazas libres. [Captura](evidencias/validacion-produccion-2026-11-17/09-cupo-restablecido.png). |

Resultado: recorrido de contactos por aceptación, precio de una mascota/noche, ocupación parcial del período, cancelación y liberación de cupo aprobado en producción. La solicitud de prueba terminó CANCELADA y el período recuperó su capacidad. No se afirma que el cupo se actualice sin volver a consultar la disponibilidad, ni se verificó todavía el ocultamiento tras cancelar desde la pantalla del cuidador.

Continúan pendientes los recorridos de franjas y precios de visitas, incidencias, finalización y valoración de esta versión publicada.

## Visitas nuevas e identificación de un registro histórico de 5 minutos

- Publicar una franja VISITA del 29/11/2026 de 15:00 a 15:05 se rechazó con el mensaje de mínimo 60 minutos: [captura](evidencias/validacion-produccion-2026-11-17/10-visita-cinco-minutos-rechazada.png).
- Tras cambiar el final a 16:00, la interfaz confirmó la publicación: [captura](evidencias/validacion-produccion-2026-11-17/11-disponibilidad-visita-publicada.png).
- El formulario de solicitud mostró 29/11, inicio 15:00, fin automático 16:00 y estimado $16.000 para Monna y Tita, con tarifa de $8.000 por mascota: [captura](evidencias/validacion-produccion-2026-11-17/12-estimado-visita-dos-mascotas.png).
- La creación de la solicitud #120002 confirmó esos horarios, las dos mascotas y $16.000. Estado PENDIENTE, sin contactos de coordinación: [captura](evidencias/validacion-produccion-2026-11-17/13-visita-120002-creada.png). Aceptación y cancelación de esta visita todavía pendientes.
- En el historial del dueño se identificó la visita #8, FINALIZADA, del 13/11/2026 de 11:55 a 12:00, para tres mascotas y $10.000: [captura](evidencias/validacion-produccion-2026-11-17/14-visita-historica-8-cinco-minutos.png). Su fecha es anterior a la formalización de la regla del 15/11. Corresponde conservar sus horarios e importe históricos, sin recalcularlos con la política actual. No se modificó ese registro. Esta captura identifica un caso concreto de cinco minutos; no permite asegurar que fuera exactamente la pantalla del reporte inicial.

Resultados confirmados en producción: rechazo de publicación de franja insuficiente y creación de visita nueva de 60 minutos con precio por dos mascotas. No se afirma una prueba nueva de máximos, concurrencia o finalización de esta visita futura.

### Aceptación y cancelación de la visita #120002

Camila Prueba aceptó la visita del 29/11/2026 de 15:00 a 16:00 para Tita y Monna. Se conservaron el intervalo de 60 minutos, las dos mascotas y el total de $16.000: [captura](evidencias/validacion-produccion-2026-11-17/15-visita-aceptada.png).

Desde la cuenta del cuidador se desplegaron los contactos y se observó la dirección «Domicilio ficticio de visita 456», junto con los datos del dueño. La captura con datos de contacto personales no se incorpora al repositorio.

Luego el cuidador canceló la solicitud. La interfaz mostró CANCELADA y ocultó los contactos de coordinación, conservando los horarios e importe históricos: [captura](evidencias/validacion-produccion-2026-11-17/16-visita-cancelada-cuidador.png).

Resultado: aceptación, dirección de visita y cancelación por el cuidador aprobadas en producción. Estado final de la #120002: CANCELADA. No se intentó finalizar anticipadamente esta visita futura ni se comprobó en este recorrido una segunda reserva del turno liberado.

### Historial visible de la visita #120002

Se desplegó Ver cuidados e historial desde el cuidador tras cancelar. Se observaron las entradas Pendiente, Aceptada y Cancelada, cada una con fecha y hora: [captura](evidencias/validacion-produccion-2026-11-17/17-historial-visita-cancelada.png). La pantalla no muestra el responsable de cada transición; su visualización no se considera verificada y queda como observación de presentación. No se validó la zona horaria de estas marcas.

Los contactos de emergencia y veterinario se mostraron como No informado desde el cuidador con la solicitud cancelada. Esta pantalla no demuestra que esos datos falten en el registro: el serializador restringe los datos privados por participante y estado. No se modificaron datos para esta comprobación.

## Consulta histórica: incidencia y valoración de la visita #8

Desde el dueño se abrió la visita FINALIZADA #8. Se observó su historial Pendiente → Aceptada → Finalizada y los datos históricos del servicio.

En Seguimiento del servicio se consultó una incidencia CONDUCTA, RESUELTA. La pantalla mostró la descripción y las medidas registradas, con «Comentario de cierre: No registrado en esta incidencia»: [captura](evidencias/validacion-produccion-2026-11-17/18-incidencia-historica-resuelta.png). No se atribuye un comentario nuevo a esta incidencia histórica ni se afirma que se hayan podido recuperar medidas anteriores sobrescritas por el flujo previo.

Se desplegó Valoración del servicio: apareció una valoración registrada de 5/5 y su comentario: [captura](evidencias/validacion-produccion-2026-11-17/19-valoracion-historica.png). No se envió ni modificó una valoración.

Resultado: consulta de incidencia resuelta y valoración histórica aprobada en producción. La creación y resolución de una incidencia nueva, la transición a FINALIZADA y la creación o rechazo de valoración duplicada no se ejecutaron en esta revisión de producción; cuentan con pruebas locales anteriores y automatizadas, que no se presentan como comprobaciones de TiDB.

## Consulta pública sin sesión

En el recorrido indicado en ventana de incógnito se abrió el detalle de Camila Prueba: [captura](evidencias/validacion-produccion-2026-11-17/20-disponibilidad-publica-sin-contactos.png). Se observaron sus condiciones y disponibilidades de alojamiento y visita, sin teléfono, email ni dirección exacta en esa vista. El alojamiento del 25 al 28/11 mostró 3 plazas libres y la visita del 29/11, 15:00–16:00.

Resultado: presentación pública del perfil sin contactos privados aprobada. Esta comprobación visual no sustituye las pruebas de autorización de los endpoints privados. El recorrido del botón Solicitar cuidado sin sesión todavía no se verificó.

Al pulsar Solicitar cuidado sin sesión, se confirmó que la navegación llevó a iniciar sesión o registrarse. No se creó otra cuenta ni se envió una solicitud en esa comprobación. Resultado informado durante el recorrido; sin captura adicional. Queda comprobado el acceso al formulario de autenticación desde la acción pública, sin atribuirle una prueba adicional de seguridad de API.
