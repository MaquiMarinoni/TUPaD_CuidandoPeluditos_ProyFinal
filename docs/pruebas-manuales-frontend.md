# Pruebas manuales del frontend — 11/11/2026

## Alcance y entorno

- Ejecución manual: Marianela, desde el navegador.
- Aplicación: Flask y frontend de `feature/frontend-maru`, commit `129042f`.
- Entorno: demo local iniciada con `python -m scripts.ejecutar_frontend_local`.
- Persistencia: SQLite, archivo local `backend/instance/frontend_demo.db`.
- Datos ficticios: cuenta de dueña Prueba, cuidador Maca Demo Prueba y mascotas Luna, Toby, Milo y Nina.
- Evidencias: capturas de pantalla y resultados observados durante las pruebas manuales. Las capturas guardadas se enlazan en la tabla. No se realizaron consultas directas a la base de datos para comprobar cada resultado.
- El script de demo todavía no está incluido en un commit. Las cuentas y la base local contienen únicamente datos de prueba.

**Las pruebas se realizaron en SQLite. Quedan pendientes las pruebas en MariaDB, las operaciones simultáneas y las verificaciones de seguridad indicadas al final.**

## Resultados

Los 18 casos dieron el resultado esperado. En cada fila se indica lo observado; cuando se comprobó la conservación de datos al recargar, también se registra.

| ID | Caso y pasos | Resultado esperado | Resultado observado / evidencia |
| --- | --- | --- | --- |
| F01 | Registrar una cuenta ficticia con rol DUENO y campos requeridos completos. | Crear la cuenta y permitir el ingreso posterior. | Mensaje «Tu cuenta está creada. Ahora ingresá con tu email y contraseña». Ingreso posterior correcto. |
| F02 | Ingresar con credenciales correctas y recargar con F5. | Mostrar nombre, rol y navegación de dueño; conservar sesión. | Se abrió Mis mascotas. El nombre y la sesión se conservaron al recargar. |
| F03 | Crear Luna: PERRO, MEDIANO, Mestiza; instrucciones de alimentación y paseos. | Una ficha con datos correctos y acciones Editar/Desactivar. | Luna apareció con los datos enviados. [Captura 01](evidencias/frontend-2026-11-11/01-mascota-creada.png). |
| F04 | Editar Luna y agregar «No darle golosinas.»; guardar y recargar. | Actualizar la ficha sin duplicarla y conservar el cambio. | El cambio se conservó después de recargar. Al cerrar e iniciar sesión, apareció una sola ficha de Luna con la indicación actualizada. |
| F05 | Cerrar sesión y recargar. | Ocultar navegación privada y mantener sesión cerrada. | La página permaneció sin sesión después de recargar. Al volver a ingresar, Luna conservó sus datos. |
| F06 | Intentar ingresar con contraseña incorrecta; después usar la correcta. | Rechazar el primer acceso con mensaje genérico y permitir el segundo. | Se mostró «Correo o contraseña incorrectos». El ingreso con la contraseña correcta funcionó. |
| F07 | Ingresar como cuidador, editar descripción, guardar y recargar. | Mostrar navegación de cuidador y conservar la edición del perfil. | El perfil conservó la descripción editada después de F5. El cambio también apareció al consultar el catálogo desde la cuenta de dueña. |
| F08 | Publicar VISITA el 13/11/2026, 10:00–12:00. | Agregar el turno y mantener el alojamiento existente. | «Tu disponibilidad está publicada». Aparecen visita y alojamiento. [Captura 02](evidencias/frontend-2026-11-11/02-agenda-publicada.png). |
| F09 | Intentar publicar VISITA el mismo día, 11:00–13:00. | Rechazar la superposición. | Se rechazó la publicación con el mensaje «Ya existe disponibilidad superpuesta para esa modalidad». Sin captura guardada. |
| F10 | Como dueña, consultar Maca Demo y elegir Solicitar cuidado en la visita publicada. | Trasladar cuidador, modalidad, fecha y horario al formulario. | El formulario mostró el cuidador, la modalidad, la fecha y el horario seleccionados. Permitió elegir a Luna y completar los datos de emergencia. |
| F11 | Enviar visita para Luna el 13/11, 10:00–12:00, dirección y contacto ficticios; urgencias sin autorizar. | Confirmar total de $8.000 y crear PENDIENTE. | Solicitud #1, PENDIENTE, una mascota, total $8.000. [Captura 03](evidencias/frontend-2026-11-11/03-visita-pendiente.png). |
| F12 | Como cuidador, consultar cuidados e historial y aceptar #1 mediante confirmación; recargar. | Mostrar instrucciones de Luna y guardar ACEPTADA. | Se mostraron los cuidados de Luna, el contacto, la dirección y la atención de urgencia no autorizada. La solicitud pasó a ACEPTADA y conservó el estado después de F5. El mismo estado apareció en la cuenta de dueña. |
| F13 | Como dueña, cancelar #1 aceptada antes del servicio. | Guardar CANCELADA y conservar los eventos anteriores. | Historial PENDIENTE → ACEPTADA → CANCELADA. [Captura 04](evidencias/frontend-2026-11-11/04-cancelacion-historial.png). |
| F14 | Crear otra visita en el mismo horario y aceptarla como cuidador. | Permitir reutilizar el turno cancelado sin borrar la solicitud anterior. | #2 ACEPTADA y #1 CANCELADA para el mismo horario. [Captura 05](evidencias/frontend-2026-11-11/05-horario-reutilizado.png). |
| F15 | Intentar desactivar disponibilidad que respalda #2 aceptada. | Impedir dejar la reserva sin disponibilidad. | Se impidió la desactivación con el mensaje «No podes desactivar esta disponibilidad porque existen reservas aceptadas». Sin captura guardada. |
| F16 | Crear alojamiento para Luna, ingreso 14/11 y salida 16/11, tarifa $12.000 por mascota/noche; aceptar como cuidador. | Dos noches, total $24.000 y estado ACEPTADA. | La estimación y el total del servidor coincidieron en $24.000. La solicitud #3 pasó a ACEPTADA y conservó el estado después de F5. |
| F17 | Crear Toby y Milo; seleccionarlos sin Luna para alojamiento del 14 al 16/11. Enviar y aceptar. | Dos mascotas × dos noches × $12.000 = $48.000. Junto con #3, completar capacidad de 3. | #4 creada PENDIENTE y luego ACEPTADA con Toby y Milo por $48.000. [Captura 06](evidencias/frontend-2026-11-11/06-alojamiento-dos-mascotas.png). |
| F18 | Crear Nina y solicitar alojamiento del 14 al 16/11 con las tres plazas ocupadas. | Rechazar por falta de cupo y conservar datos del formulario. | Se mostró «No hay cupos para todas las noches». Nina, las fechas y el contacto permanecieron cargados en el formulario. [Captura 07](evidencias/frontend-2026-11-11/07-rechazo-sobrecupo.png). |

## Estado de las solicitudes al terminar las pruebas

| Solicitud | Servicio | Mascotas | Fechas / horario | Estado observado | Total |
| --- | --- | --- | --- | --- | --- |
| #1 | Visita | Luna | 13/11, 10:00–12:00 | CANCELADA | $8.000 |
| #2 | Visita | Luna | 13/11, 10:00–12:00 | ACEPTADA | $8.000 |
| #3 | Alojamiento | Luna | 14/11–16/11, 2 noches | ACEPTADA | $24.000 |
| #4 | Alojamiento | Toby y Milo | 14/11–16/11, 2 noches | ACEPTADA | $48.000 |

La solicitud de Nina fue rechazada durante la creación; no se observó un identificador nuevo. Las pruebas de capacidad se realizaron una después de otra, con un único cuidador y capacidad máxima de 3.

## Pruebas pendientes

- **Validación en MariaDB:** las primeras pruebas se realizaron con SQLite, en una base local separada, para avanzar con la interfaz mientras la otra desarrolladora trabajaba en paralelo en el backend. Queda pendiente repetir el recorrido principal en MariaDB, el motor elegido para la entrega, aplicando las migraciones del proyecto para comprobar su funcionamiento con el esquema previsto.
- Ejecutar aceptaciones simultáneas y comprobar bloqueos y capacidad en MariaDB/InnoDB.
- Validar aislamiento entre usuarios mediante consultas y modificaciones no autorizadas, más allá de la navegación por rol observada.
- Intentar modificar datos sin token CSRF y comprobar que el servidor rechace la operación.
- Probar formularios de alta de cuidador desde una cuenta nueva, edición de disponibilidad, bajas lógicas y restricciones de especies.
- Probar fechas inválidas, urgencias autorizadas con veterinario y límite, y conservación histórica de datos después de editar una mascota ya reservada.
- Probar rechazo de solicitudes, finalización del servicio y, cuando estén integradas, incidencias y valoraciones.
- Verificar uso completo en celular, navegación por teclado y mensajes de error de los formularios.

## Uso de IA

Se utilizó IA como apoyo para organizar y redactar la documentación de pruebas. Marianela ejecutó las pruebas manuales y revisó los resultados registrados.
