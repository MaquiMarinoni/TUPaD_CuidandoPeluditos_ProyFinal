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

Los scripts `prueba_visitas` y `prueba_concurrencia_visitas` utilizan intervalos de 60 minutos y el cálculo por mascota. Su ejecución en MariaDB y la comprobación visual se registrarán cuando se realicen; los informes anteriores conservan las reglas y resultados de su fecha.
