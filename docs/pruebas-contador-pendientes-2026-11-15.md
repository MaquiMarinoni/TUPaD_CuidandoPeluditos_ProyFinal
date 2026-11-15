# Contador de solicitudes pendientes — 15/11/2026

## Funcionamiento

El número junto a Mis solicitudes cuenta únicamente solicitudes en estado PENDIENTE del usuario autenticado. Para el cuidador indica pedidos que esperan su respuesta; para el dueño, pedidos que esperan respuesta del cuidador. No es un contador de avisos no leídos. Si no hay pendientes, el círculo se oculta.

Se consulta al iniciar sesión, al cargar o gestionar solicitudes, al volver a la pestaña y cada 60 segundos mientras la página está visible. Las consultas del contador no reemplazan formularios ni tarjetas en uso. El texto accesible indica el significado del número según el rol.

## Recorrido manual

Ejecución: Marianela, Edge, Flask local en el puerto 5001, MariaDB 11.4.13 y base cuidandopeluditos_pruebas. Rama feature/ajustes-ux-maru sobre el commit 64689b9, con el cambio de contador pendiente de commit. Cuentas ficticias locales de dueña y cuidador.

Se publicó disponibilidad del 20 al 22/11/2026 y se creó desde la web la solicitud #23 para Luna, una mascota, dos noches y total $24.000.

| Caso | Resultado observado | Evidencia |
| --- | --- | --- |
| Dueña envía solicitud #23 | Aparece 1 junto a Mis solicitudes. | [Dueña](evidencias/contador-pendientes-2026-11-15/01-duena-un-pendiente.png) |
| Cuidador inicia sesión | Aparece 1 estando en Mi perfil y agenda, antes de entrar en Mis solicitudes. | [Cuidador](evidencias/contador-pendientes-2026-11-15/02-cuidador-contador-al-ingresar.png) |
| Cuidador acepta | Se informa actualización correcta y el círculo desaparece. | [Aceptación](evidencias/contador-pendientes-2026-11-15/03-cuidador-sin-contador-tras-aceptar.png) |
| Dueña vuelve a ingresar | Ya no aparece el contador, estando en Mis mascotas. | [Sin pendientes](evidencias/contador-pendientes-2026-11-15/04-duena-sin-pendientes.png) |
| Dueña consulta la reserva | #23 ACEPTADA, Luna, 20 al 22/11/2026 y total $24.000. | [Reserva](evidencias/contador-pendientes-2026-11-15/05-solicitud-23-aceptada.png) |

La solicitud #23 permanece aceptada en la base local de pruebas. No se modificaron datos del despliegue. Este recorrido valida los casos de cero y un pendiente y la actualización al gestionar e iniciar sesión. No se ensayaron aquí múltiples pendientes, errores de conexión, actualización entre dos sesiones abiertas simultáneamente ni el intervalo automático de 60 segundos.

Se utilizó IA como apoyo para organizar y redactar la documentación de pruebas.
