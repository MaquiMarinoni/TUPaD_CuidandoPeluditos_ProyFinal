# Pruebas manuales P1 y navegación — 12/11/2026

## Entorno y preparación

Ejecución manual: Marianela. Windows, navegador Edge, Flask en `http://127.0.0.1:5001`, MariaDB 11.4.13 y base `cuidandopeluditos_pruebas`. Rama `integration/tpi-final`, sobre la integración `df6ef50`, con el ajuste de menú descrito abajo.

Se prepararon directamente mediante los modelos dos solicitudes sintéticas para las cuentas locales de prueba y la mascota `Demo P1 (ficticia)`: #12, aceptada del 12 al 13/11, y #13, aceptada del 8 al 10/11. Esta preparación permite comprobar fechas vigentes y pasadas sin cambiar el reloj. No constituye una prueba de creación y aceptación de reservas desde la interfaz. La solicitud original #1 de Luna se conservó. Los datos sintéticos de este recorrido permanecen en la base local; no se ejecutó limpieza automática.

## Resultados

| Caso | Resultado observado | Evidencia |
| --- | --- | --- |
| Formulario de incidencia | Visible para el cuidador en #12, dentro de sus fechas. Oculto en la reserva futura #1. | [Formulario](evidencias/visual-p1-2026-11-12/01-formulario-incidencia.png) |
| Registrar incidencia | Conducta, descripción y medidas guardadas; estado ABIERTA conservado después de F5. | [Incidencia abierta](evidencias/visual-p1-2026-11-12/02-incidencia-abierta.png) |
| Resolver incidencia | Estado RESUELTA y medidas actualizadas. Persistencia tras F5 confirmada; desapareció el control de resolución. | [Resolución](evidencias/visual-p1-2026-11-12/03-incidencia-resuelta.png) |
| Consulta de la dueña | Puede leer la incidencia resuelta y sus medidas; no aparecen controles de creación o resolución. | [Consulta](evidencias/visual-p1-2026-11-12/04-consulta-duena.png) |
| Finalizar servicio | El cuidador confirmó la finalización de #13. Estado FINALIZADA conservado después de F5; historial PENDIENTE, ACEPTADA y FINALIZADA. Los dos primeros estados fueron preparados por el script. | [Historial](evidencias/visual-p1-2026-11-12/05-finalizacion-historial.png) |
| Publicar valoración | La dueña publicó 5/5 y un comentario identificado como ficticio. Persisten después de F5 y el formulario se reemplaza por la valoración registrada. No se intentó un segundo envío HTTP en este recorrido manual. | [Valoración](evidencias/visual-p1-2026-11-12/06-valoracion.png) |
| Tarjeta en ventana angosta | Estado, importe y comentario legibles; el comentario ocupa varias líneas. | [Tarjeta](evidencias/visual-p1-2026-11-12/07-tarjeta-angosta.png) |
| Menú en ventana angosta | Se detectó desplazamiento horizontal. Se modificó la regla móvil de CSS para permitir varias filas; después de Ctrl+F5 todos los enlaces quedan visibles. | [Antes](evidencias/visual-p1-2026-11-12/08-menu-antes.png), [después](evidencias/visual-p1-2026-11-12/09-menu-despues.png) |
| Menú en escritorio | Tras maximizar, el menú conserva una fila y el contenido dos columnas. | [Escritorio](evidencias/visual-p1-2026-11-12/10-escritorio.png) |
| Teclado | En el recorrido de Mis servicios se confirmó foco visible y avance y retroceso con Tab y Shift+Tab. | Comprobación manual |

## Alcance y límites

Se verificaron los recorridos indicados en Edge sobre MariaDB local. La revisión en ventana reducida no sustituye una prueba en teléfono físico ni una auditoría completa de accesibilidad. No se probaron todas las pantallas, anchos, navegadores ni acciones con teclado. Los permisos observados en la interfaz no sustituyen los casos automatizados de autorización del backend.

Se utilizó IA como apoyo para organizar y redactar la documentación de pruebas.
