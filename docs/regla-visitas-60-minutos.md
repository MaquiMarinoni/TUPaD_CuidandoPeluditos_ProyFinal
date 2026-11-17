# Regla de nuevas visitas — 15/11/2026

- Cada visita dura exactamente 60 minutos y termina el mismo día.
- Incluye entre 1 y 3 mascotas activas del mismo dueño.
- Total = tarifa por mascota del cuidador × cantidad de mascotas.
- El servidor calcula el horario final y el importe. La hora completa debe estar cubierta por la disponibilidad publicada.
- Una visita ocupa una franja del cuidador, independientemente de cuántas mascotas incluya. El cupo de alojamiento sigue siendo una regla separada.
- Las visitas anteriores conservan sus horarios e importes. No se modifica la base mediante una migración para este cambio.

Ejemplo: tarifa de $8.000; una mascota, $8.000; dos, $16.000; tres, $24.000. Siempre por 60 minutos.

La tarifa de visita ya configurada se interpreta como tarifa por mascota para las nuevas solicitudes. Antes de publicar esta versión corresponde revisar los valores con los cuidadores de la demostración.

## Verificación

Pruebas aisladas: `python -m pytest tests/test_visitas_60_minutos.py -q`.

Resultados del 15/11/2026 en la rama `feat/visitas-60-minutos`, a partir del commit `292f51d`:

| Entorno | Comprobación | Resultado |
|---|---|---|
| SQLite en memoria | Suite completa `python -m pytest tests -q` | 38 aprobadas; incluye 10 casos nuevos de visitas. |
| JavaScript | Sintaxis de `app.js` y cálculo del horario final | Correctos; incluye 10:30 → 11:30 y rechazo de inicio 23:00 por cambio de día. |
| API local en 5001, conectada a MariaDB de pruebas | `python -m scripts.prueba_visitas` | Todas aprobadas. Cuidador #10; solicitudes #26 y #27. |
| API local en 5001, conectada a MariaDB de pruebas | `python -m scripts.prueba_concurrencia_visitas` | Todas aprobadas. Cuidador #11; solicitudes #28 y #29. |
| Navegador local | Inicio 15:00 y final automático 16:00 | Correcto; campo final de solo lectura. |
| Navegador local | Tarifa de $8.000: seleccionar una mascota, agregar otra y quitarla | El estimado pasó de $8.000 a $16.000 y volvió a $8.000. No se envió esta solicitud. |

La prueba de visitas confirmó el total de $160 para dos mascotas con tarifa de $80, permisos, protección CSRF, bloqueo de horarios superpuestos y liberación del turno al cancelar. En la prueba simultánea, Beto obtuvo HTTP 200 y Ana HTTP 409; quedaron una solicitud ACEPTADA y otra PENDIENTE. También se verificaron privacidad, conflicto con alojamiento y desactivación de disponibilidad después de cancelar.

Los casos aislados verificaron el importe con una, dos y tres mascotas, el rechazo de una cuarta, la duración alterada, el horario fuera de disponibilidad y la conservación del horario e importe de una visita anterior. Estas comprobaciones aisladas se ejecutaron con SQLite; no se presentan como pruebas de esos mismos casos en MariaDB.

Los informes anteriores conservan las reglas y resultados correspondientes a su fecha. Estas pruebas locales no equivalen a una validación del despliegue en Render/TiDB.


## Evidencia visual

![Visita con fin automático de 60 minutos](evidencias/visitas-60-minutos-2026-11-15/01-fin-automatico.png)

La captura muestra la duración y el límite indicados en el formulario. La variación del estimado se confirmó durante el recorrido; no se adjuntó una captura de ese importe.

## Observación en producción: horarios de 5 minutos — 17/11/2026

Durante el recorrido de la aplicación publicada en Render se informó la presencia de turnos de visita de 5 minutos. Estado: **pendiente de identificar y reproducir**. No se cuenta todavía con una captura, identificadores ni horarios exactos de esos registros.

No está confirmado si corresponden a solicitudes históricas anteriores a la regla de 60 minutos o a franjas de disponibilidad publicadas. La antigüedad de los datos es una hipótesis, no una causa comprobada. Las pruebas locales de la regla no demuestran por sí solas el comportamiento de esos registros en Render/TiDB.

Para cerrar esta observación se debe:

- Identificar la pantalla, el registro y los horarios mostrados en producción.
- Distinguir entre una visita histórica y una disponibilidad que se ofrece para crear una visita nueva.
- Conservar los horarios e importes de las solicitudes históricas, aunque duren menos de 60 minutos.
- Comprobar que las nuevas solicitudes duren exactamente 60 minutos y queden cubiertas por una disponibilidad válida.
- Si una franja publicada dura menos de 60 minutos, revisar su presentación y selección para no ofrecerla como un turno reservable de 60 minutos.
- Registrar la evidencia y el resultado de la verificación antes de marcar la observación como resuelta.

Esta anotación no implica cambios ni eliminación de datos de producción y no presenta el caso como corregido.

### Resultado de la verificación — 17/11/2026

Se consultaron sin autenticación y sin modificar datos `/api/cuidadores` y las disponibilidades públicas de los 16 perfiles devueltos por el listado de Render. En esa consulta no se encontraron franjas de visita menores de 60 minutos. No se inspeccionaron solicitudes privadas ni cuentas inactivas; no se identificó el registro observado anteriormente y su origen continúa sin confirmar.

En el código local se reprodujo una inconsistencia: `validar_datos` de disponibilidades aceptó una franja futura VISITA de 15:00 a 15:05, devolviendo datos válidos y sin error. Se invocó solo la función de validación; no se creó ni guardó una disponibilidad. La consulta pública del código local devuelve las disponibilidades activas sin filtrar su duración. Por su parte, la validación de nuevas solicitudes de visita calcula 60 minutos y rechaza un final distinto; no se intentó crear una reserva en producción.

[Evidencia de la comprobación](evidencias/visitas-cortas-2026-11-17/resultado-verificacion.json).

Conclusión: no se reprodujo el caso concreto en la consulta pública actual de Render, pero sí se confirmó localmente que se pueden validar disponibilidades demasiado cortas. Queda pendiente corregir esa validación y la presentación de franjas antiguas insuficientes, con pruebas, sin alterar solicitudes históricas. El caso original no se marca como resuelto.

### Corrección local de franjas insuficientes

- Crear o editar una disponibilidad de visitas exige una franja de al menos 60 minutos; puede ser más amplia para ofrecer diferentes horarios de inicio.
- La consulta pública excluye franjas de visitas menores de 60 minutos, sin horarios completos o cuyo rango de fechas ya terminó. La búsqueda de cuidadores utiliza esa consulta.
- Las franjas anteriores se conservan en la base y en la agenda privada del cuidador. Se pueden corregir si no respaldan reservas aceptadas, manteniendo las restricciones existentes.
- No se alteran horarios ni importes de solicitudes históricas. No se requiere una migración nueva.
- La ayuda del formulario de agenda explica el mínimo de 60 minutos.

La cobertura automatizada adicional está en `tests/test_disponibilidades_visitas.py`: creación de franjas de 5, 59, 60 y 120 minutos; exclusión pública y conservación privada de franjas antiguas; corrección de una franja de 5 a 60 minutos. La comprobación manual de este ajuste en navegador y su validación posterior al despliegue continúan pendientes.

Resultado de la suite aislada completa tras el ajuste: **104 pruebas aprobadas** (51,24 segundos), con 799 advertencias de deprecación. No equivale a una prueba de esta corrección en Render/TiDB.

### Prueba manual local de publicación — 17/11/2026

En el navegador local, conectado a MariaDB de pruebas, Cuidador Prueba intentó publicar una disponibilidad VISITA para el 25/11/2026, de 15:00 a 15:05. El sistema rechazó la operación con el mensaje «La franja de visitas debe cubrir al menos 60 minutos».

Luego se cambió únicamente la hora final a 16:00. La publicación se aceptó y apareció en Mis disponibilidades como 25/11/2026 al 25/11/2026, 15:00–16:00.

- [Rechazo de la franja de 5 minutos](evidencias/visitas-cortas-2026-11-17/01-rechazo-franja-cinco-minutos.png).
- [Franja de 60 minutos publicada](evidencias/visitas-cortas-2026-11-17/02-franja-sesenta-minutos-publicada.png).

Estas capturas verifican la publicación en el entorno local; la exclusión pública de franjas antiguas se cubrió con pruebas automatizadas. La comprobación de la corrección después del despliegue en Render continúa pendiente.

### Identificación posterior en el historial de producción

Durante el recorrido final se identificó la visita #8, FINALIZADA, del 13/11/2026, de 11:55 a 12:00, tres mascotas y monto histórico de $10.000. Es anterior a la regla del 15/11 y se conserva sin recalcular. La nueva #120002, del 29/11 de 15:00 a 16:00 para dos mascotas, confirmó $16.000. La publicación de una franja de cinco minutos fue rechazada. Evidencias en [validación de producción](validacion-produccion-2026-11-17.md). No se puede asegurar que la #8 sea el mismo registro del reporte inicial.
