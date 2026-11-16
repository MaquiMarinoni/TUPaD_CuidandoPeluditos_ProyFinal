# Plazas libres de alojamiento

El período publicado por el cuidador se conserva. La consulta pública agrega tramos con plazas libres según las reservas ACEPTADAS y FINALIZADAS, respetando el cálculo por noche. PENDIENTES, RECHAZADAS y CANCELADAS no ocupan plazas. La fecha de salida no consume una noche.

Ejemplo: capacidad 3, período del 20 al 25 y una mascota reservada del 21 al 24. Quedan 3 plazas del 20 al 21, 2 del 21 al 24 y 3 del 24 al 25.

La búsqueda de alojamiento con fechas exige al menos una plaza durante todo el rango. El resumen no conoce todavía cuántas mascotas seleccionará el dueño; el servidor mantiene la comprobación definitiva para todas ellas al aceptar. No se expone información personal de las reservas.

La página muestra los cupos al consultar o volver a abrir el detalle. No representa una reserva ni una actualización en tiempo real. Los períodos de alojamiento terminados no ofrecen el botón de solicitud. Las disponibilidades de visitas no cambian con este ajuste.

No requiere migraciones.

## Validación del 15/11/2026

- Suite aislada con SQLite en memoria: 44 pruebas aprobadas, incluidas 6 del resumen público de cupos. Se comprobaron reservas parciales, recambio el mismo día, estados que no ocupan plazas, cancelación, fechas pasadas y respuesta pública sin datos personales.
- JavaScript: sintaxis correcta y comprobación del filtro con tramos consecutivos, tramo sin cupo y salida coincidente con el comienzo de un tramo ocupado.
- Recorrido manual en navegador local, puerto 5001, con MariaDB de pruebas: cuidador Prueba, capacidad 3, tarifa de alojamiento $12.000 y período publicado del 20 al 22/11/2026. La reserva previa de Luna ocupaba una plaza en ambas noches.

| Paso | Resultado observado |
|---|---|
| Consulta inicial | 2 plazas libres del 20 al 22/11. |
| Seleccionar Demo P1 del 20 al 21/11 | Estimado de $12.000 por una mascota y una noche. |
| Enviar y aceptar solicitud #30 | ACEPTADA, con total de $12.000. |
| Volver a consultar el detalle como dueño | 1 plaza libre del 20 al 21 y 2 del 21 al 22. |
| Cancelar la solicitud #30 y volver a consultar | 2 plazas libres del 20 al 22. |

La prueba confirma que una reserva parcial descuenta plazas únicamente en las noches utilizadas y que la cancelación restablece ese cupo. El período publicado se conserva. Este recorrido corresponde al entorno local; no se presenta como una validación de Render/TiDB.

## Evidencias

1. [Cupo inicial](evidencias/cupos-alojamiento-2026-11-15/01-cupo-inicial.png).
2. [Estimado por una noche](evidencias/cupos-alojamiento-2026-11-15/02-estimado-una-noche.png).
3. [Solicitud #30 aceptada](evidencias/cupos-alojamiento-2026-11-15/03-solicitud-30-aceptada.png).
4. [Plazas libres por tramo](evidencias/cupos-alojamiento-2026-11-15/04-cupos-por-tramo.png).
5. [Cupo restablecido](evidencias/cupos-alojamiento-2026-11-15/05-cupo-restablecido.png).
