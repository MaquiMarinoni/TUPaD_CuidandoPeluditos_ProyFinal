# Incidencias con medidas iniciales y cierre separado — 15/11/2026

## Cambio

La incidencia conserva medidas_tomadas al crearla y guarda comentario_cierre al resolverla. El cierre requiere texto no vacío de hasta 2000 caracteres y solo lo puede realizar el cuidador asignado en una incidencia ABIERTA. La API de resolución recibe comentario_cierre y no admite modificar medidas_tomadas.

La interfaz distingue Medidas iniciales y Comentario de cierre. Después de resolver muestra ambos textos sin un nuevo control de resolución. Los registros históricos conservan el contenido existente de medidas_tomadas; no se intenta reconstruir información que pudo sobrescribirse con la implementación anterior. Si una incidencia antigua está resuelta sin comentario_cierre, la interfaz muestra Medidas registradas y señala que no hay comentario de cierre registrado.

## Migración

Nueva revisión: d18a6c2f904b, posterior a c0af3fd5552a. Agrega la columna nullable incidencias.comentario_cierre sin cambiar los textos existentes. La migración se aplicó en cuidandopeluditos_pruebas, MariaDB 11.4.13. db check finalizó sin nuevas operaciones detectadas.

Para integrar al despliegue, aplicar esta migración en la base correspondiente antes de arrancar el código que consulta la nueva columna. Publicar frontend y backend compatibles juntos: el cuerpo de resolución ahora utiliza comentario_cierre. La aplicación local fue verificada con MariaDB; esta revisión no declara aplicada la migración en TiDB ni actualizado Render. El downgrade elimina la nueva columna y su contenido; no se utilizó en esta validación.

## Pruebas automatizadas aisladas

Se ejecutaron incidencias, valoraciones, privacidad, finalización y cancelación: **28 pruebas aprobadas en SQLite de pruebas**. Incluyen conservación de medidas iniciales al resolver, lectura posterior de ambos textos, comentario ausente, vacío, inválido o demasiado largo, rechazo de intentos de sobrescribir medidas durante el cierre y lectura de registros históricos sin comentario nuevo.

## Prueba de integración con MariaDB

El comando python -m scripts.prueba_p1_mariadb comprobó sesiones autenticadas y CSRF, conectado a la base MariaDB de pruebas. Pasaron creación y resolución, conservación de medidas, comentario separado, persistencia de ambos campos, permisos y bloqueo de segunda resolución, además de los casos de valoraciones. El script eliminó sus propios datos ficticios al terminar.

Evidencia generada: [Salida P1 con cierre separado](evidencias/p1-cierre-mariadb.txt).

## Recorrido manual del navegador

Edge, localhost:5001 y MariaDB 11.4.13, rama fix/incidencias-cierre. Se agregó un caso ficticio a la solicitud local #1 de Luna, aceptada del 14 al 16/11/2026. Se eligió SALUD, con descripción de prueba de cierre separado.

| Caso | Resultado observado | Evidencia |
| --- | --- | --- |
| Formulario de creación | Aparece Medidas iniciales (opcional). | [Formulario](evidencias/incidencias-cierre-2026-11-15/01-formulario-medidas-iniciales.png) |
| Creación | Incidencia ABIERTA con medidas guardadas y un campo distinto Comentario de cierre. | [Abierta](evidencias/incidencias-cierre-2026-11-15/02-abierta-comentario-cierre.png) |
| Resolución y F5 | Estado RESUELTA. Se conserva Se avisó al dueño y se preparó un espacio tranquilo. El cierre aparece aparte: Luna se adaptó al espacio y permaneció tranquila. Se informó al dueño. | [Persistencia](evidencias/incidencias-cierre-2026-11-15/03-resuelta-despues-f5.png) |
| Consulta de la dueña | Puede leer ambos textos, sin formularios de modificación o resolución. | [Dueña](evidencias/incidencias-cierre-2026-11-15/04-consulta-duena.png) |

La incidencia manual permanece en la base local. No se modificaron reservas ni datos del despliegue.

Se utilizó IA como apoyo para organizar y redactar la documentación de pruebas.
