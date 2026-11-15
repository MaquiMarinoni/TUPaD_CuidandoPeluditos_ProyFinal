# Conservación de fechas al solicitar cuidado — 15/11/2026

## Problema reproducido

En la búsqueda desde Inicio se eligió alojamiento del 20 al 21/11/2026. El perfil Cuidador Prueba tenía disponibilidad publicada del 20 al 22/11. Al pulsar Solicitar cuidado en ese período, el formulario reemplazaba la salida elegida por el 22/11. El cambio añadía una noche no seleccionada y podía aumentar el total estimado.

## Corrección

El formulario conserva las fechas de la búsqueda cuando la modalidad coincide y el rango está cubierto por la disponibilidad seleccionada. Para visitas conserva el día buscado si está dentro del rango publicado; las horas siguen tomándose de la franja elegida. Sin fechas de búsqueda, con modalidad diferente o rango no cubierto, se utiliza el período publicado de la fila seleccionada.

La selección de fechas se obtiene antes de recargar las opciones del formulario. No se modificó el cálculo de cupos ni la fórmula de precios del backend. Tampoco se implementó en este cambio una presentación de plazas libres por noche ni la conservación de una reserva a través de un login intermedio.

## Recorrido manual

Edge, aplicación local en puerto 5001, MariaDB 11.4.13 y base cuidandopeluditos_pruebas; sesión de dueña en rama fix/conservar-fechas-reserva.

| Caso | Resultado observado | Evidencia |
| --- | --- | --- |
| Búsqueda desde Inicio | Resumen de alojamiento para perro, 20 al 21/11, con Cuidador Prueba como resultado. | [Búsqueda](evidencias/fechas-reserva-2026-11-15/01-busqueda-una-noche.png) |
| Disponibilidad elegida | Período publicado del 20 al 22/11. | [Agenda](evidencias/fechas-reserva-2026-11-15/02-periodo-publicado.png) |
| Antes de corregir | Formulario con ingreso 20/11 y salida 22/11, sustituyendo el rango buscado. | [Antes](evidencias/fechas-reserva-2026-11-15/03-antes-fechas-reemplazadas.png) |
| Después de corregir | Mismo recorrido; ingreso 20/11 y salida 21/11 conservados. | [Después](evidencias/fechas-reserva-2026-11-15/04-despues-fechas-conservadas.png) |
| Estimación | Solo Demo P1 (ficticia) seleccionada: $12.000 por una mascota y una noche, con tarifa de $12.000 por mascota/noche. | [Estimado](evidencias/fechas-reserva-2026-11-15/05-estimado-una-noche.png) |

No se envió una nueva solicitud ni se modificaron reservas existentes durante este recorrido. El importe observado es la estimación del frontend, no un nuevo monto persistido por el servidor.

## Comprobación complementaria

Se verificó la sintaxis de app.js con Node y se ejecutaron seis comprobaciones de la función de selección de fechas: rango buscado cubierto, ausencia de búsqueda, rango fuera de cobertura, modalidad distinta, día de visita dentro de cobertura y rango invertido. Las seis pasaron sin acceso a base de datos. El recorrido manual anterior corresponde a alojamiento; no se declara aquí una prueba completa del formulario de visitas.

Se utilizó IA como apoyo para organizar y redactar la documentación de pruebas.
