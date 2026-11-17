# Contactos para coordinar el cuidado

Los participantes activos de una solicitud ACEPTADA o FINALIZADA pueden consultar nombre, teléfono y email de dueño y cuidador. Los contactos de coordinación no están disponibles en PENDIENTE, RECHAZADA o CANCELADA, ni en búsquedas públicas ni para terceros. El contacto de emergencia tiene una función distinta y conserva su política de privacidad previa.

La pantalla muestra los datos de la contraparte como texto, sin enviar mensajes ni abrir conversaciones automáticamente. Son contactos actuales del perfil, no un snapshot histórico de teléfonos o correos. La dirección de visita conserva el snapshot original.

El cuidador puede informar una dirección de alojamiento privada y opcional en Mi perfil y agenda. Solo se devuelve al titular en los métodos de mi-perfil. Al aceptar un alojamiento se copia a la dirección del servicio, si aún no estaba informada; cambios posteriores del perfil no alteran esa dirección acordada. Para reservas anteriores no se rellena retroactivamente con un domicilio nuevo. Cuando no se informó, la interfaz indica coordinar la entrega directamente por teléfono o email.

Se reutilizan `usuarios.direccion` y `solicitudes.direccion_servicio`: este ajuste no requiere otra migración. La actualización conjunta sí necesita la migración de auditoría `e72a91c4b603` incorporada en la rama anterior.

## Verificación

`tests/test_contactos_servicio.py` comprueba estados y roles, acceso anónimo y ajeno, exclusión de la dirección de las consultas públicas, validación y conservación del domicilio al cambiar el perfil. Pruebas aisladas SQLite; la validación manual en MariaDB y navegador se agrega una vez ejecutada.

## Prueba manual local — 17/11/2026

Entorno: navegador local y MariaDB `cuidandopeluditos_pruebas` (11.4.13). No corresponde a una validación en producción.

Solicitud de alojamiento #31: Demo P1 (ficticia), Cuidador Prueba, del 20/11/2026 al 21/11/2026; una mascota y una noche, total $12.000.

- Se guardó una dirección ficticia privada en el perfil del cuidador.
- En estado PENDIENTE, el dueño no vio los contactos del cuidador: [captura](evidencias/contactos-servicio-2026-11-17/01-pendiente-sin-contactos.png).
- Tras aceptar, el cuidador vio nombre, teléfono y email del dueño y la dirección de alojamiento acordada: [captura](evidencias/contactos-servicio-2026-11-17/02-cuidador-contactos-aceptada.png).
- El dueño vio los contactos del cuidador y la misma dirección: [captura](evidencias/contactos-servicio-2026-11-17/03-duena-contactos-aceptada.png).
- Tras cancelar, los contactos volvieron a ocultarse. La solicitud quedó CANCELADA: [captura](evidencias/contactos-servicio-2026-11-17/04-cancelada-sin-contactos.png).

Suite automatizada completa: **98 pruebas aprobadas**, con advertencias de deprecación de SQLAlchemy y datetime. La comprobación de sintaxis de JavaScript también pasó. La conservación de la dirección al modificar el perfil y las restricciones para terceros se verificaron en pruebas automatizadas.
