# Cancelación de reservas por el cuidador — 12/11/2026

## Regla implementada

El dueño y el cuidador asignado pueden cancelar una reserva ACEPTADA antes del inicio del servicio. Para alojamiento, el inicio se considera al comenzar la fecha de ingreso; para visitas, se utiliza la fecha y hora inicial. Una reserva iniciada no puede cancelarse por esta acción.

El dueño conserva la cancelación de solicitudes PENDIENTES. El cuidador puede rechazarlas, pero no cancelarlas mientras están pendientes. La interfaz solicita confirmación y el backend valida participante, estado y fechas dentro del bloqueo existente. La transición a CANCELADA registra el usuario responsable en el historial; la reserva deja de contarse entre las aceptadas al calcular ocupación.

## Recorrido manual con MariaDB

Ejecución manual: Marianela. Edge, Flask en el puerto 5001, MariaDB 11.4.13 y base `cuidandopeluditos_pruebas`, rama `integration/tpi-final` con el cambio de cancelación.

Las solicitudes de este recorrido se crearon y aceptaron desde la web. Se utilizó la mascota ficticia Demo P1, el perfil Cuidador Prueba y el período 14 al 16/11/2026. La reserva original #1 de Luna se conservó.

| Caso | Resultado observado | Evidencia |
| --- | --- | --- |
| Crear solicitud #14 | PENDIENTE; una mascota, dos noches y total $24.000. | [Solicitud](evidencias/cancelacion-cuidador-2026-11-12/01-solicitud-pendiente.png) |
| Aceptar #14 como cuidador | ACEPTADA y botón Cancelar solicitud visible. | [Aceptación](evidencias/cancelacion-cuidador-2026-11-12/02-aceptada-cuidador.png) |
| Cancelar #14 como cuidador | Se mostró la confirmación y luego pasó a CANCELADA. | [Confirmación](evidencias/cancelacion-cuidador-2026-11-12/03-confirmacion-cancelacion.png) |
| Persistencia e historial | CANCELADA después de F5; historial PENDIENTE → ACEPTADA → CANCELADA. | [Historial](evidencias/cancelacion-cuidador-2026-11-12/04-historial-cuidador.png) |
| Consulta de la dueña | La misma solicitud aparece CANCELADA, con el mismo historial. | [Consulta](evidencias/cancelacion-cuidador-2026-11-12/05-consulta-duena.png) |
| Nueva reserva #15 | La misma mascota y fechas pudieron solicitarse nuevamente y aceptarse por $24.000. El estado ACEPTADA se conservó tras F5. | [Nueva aceptación](evidencias/cancelacion-cuidador-2026-11-12/06-nueva-reserva-aceptada.png) |

La nueva aceptación comprueba que la cancelación anterior no bloquea la mascota para esas fechas. Este recorrido no agotó la capacidad del cuidador y no se registra como prueba de reutilización de la última plaza. Al terminar, #14 permanece CANCELADA y #15 ACEPTADA en la base de pruebas.

## Pruebas automatizadas aisladas con SQLite

Se ejecutaron siete casos nuevos: cancelación futura por ambos participantes en alojamiento y visitas, persistencia y autor del historial, bloqueo de repetición, bloqueo de cancelación del cuidador una vez iniciado el período y conservación del rechazo de solicitudes pendientes. Archivo: `tests/test_cancelacion_cuidador.py`.

También se ejecutaron los catorce casos existentes de incidencias, valoraciones, privacidad y finalización. Resultado conjunto: **21 pruebas aprobadas**. Estos tests utilizan SQLite aislado y se registran separados del recorrido manual en MariaDB.

```powershell
python -m pytest tests/test_cancelacion_cuidador.py tests/test_incidencias.py tests/test_valoraciones.py tests/test_privacidad_solicitudes.py tests/test_finalizacion.py -q
```

Se utilizó IA como apoyo para organizar y redactar la documentación de pruebas.
