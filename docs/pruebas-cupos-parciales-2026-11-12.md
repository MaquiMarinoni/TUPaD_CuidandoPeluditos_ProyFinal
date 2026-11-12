# Ocupación por noche con reservas parcialmente solapadas — 12/11/2026

## Entorno y preparación

Ejecución: Marianela, mediante `python -m scripts.prueba_cupos_parciales`. Se verificó motor MariaDB/MySQL y base `cuidandopeluditos_pruebas`. El script utiliza Flask.test_client con sesiones autenticadas y tokens CSRF, conectado a MariaDB real; no utiliza SQLite ni controla formularios del navegador.

Se creó un cuidador ficticio con capacidad máxima 2 y cuatro mascotas distintas. Cada solicitud contiene una mascota. Todas se crearon PENDIENTES antes de intentar las aceptaciones.

## Resultados

| Caso | Solicitud | Período de diciembre de 2026 | Resultado |
| --- | --- | --- | --- |
| A | #19 | 12 al 14, dos noches | Aceptación HTTP 200. |
| B | #20 | 14 al 16, dos noches | Aceptación HTTP 200; no coincide con A porque el retiro no consume noche. |
| C | #21 | 12 al 16, cuatro noches | Aceptación HTTP 200; coincide con A en el primer tramo y con B en el segundo, sin superar dos plazas por noche. |
| D | #22 | 13 al 15, dos noches | Intento de aceptación HTTP 409 por sobrecupo real; mantiene PENDIENTE. |

Con tarifa de $100 por mascota y noche, el script comprobó importes de $200, $200, $400 y $200 respectivamente. Las consultas posteriores confirmaron los estados ACEPTADA, ACEPTADA, ACEPTADA y PENDIENTE antes de cancelar los casos.

**Resultado: todas las comprobaciones pasaron.** La ocupación se evalúa por noche; no se suman indiscriminadamente todas las reservas que intersectan algún tramo de la nueva solicitud. Este caso responde a la observación del tutor sobre reservas que coinciden con la nueva pero no entre sí.

## Estado posterior y reproducción

Las solicitudes #19, #20, #21 y #22 se cancelaron por API, con HTTP 200 en los cuatro casos. Permanecen los usuarios, perfil, disponibilidad y mascotas ficticios propios de esta ejecución. No se modificaron reservas manuales anteriores.

Con DATABASE_URL configurada contra MariaDB y una base terminada en `_pruebas`, ejecutar desde la raíz:

```powershell
python -m scripts.prueba_cupos_parciales
```

El script genera fechas relativas e identificadores propios en cada ejecución. No requiere un servidor HTTP adicional. La concurrencia se valida en sus pruebas independientes; este recorrido comprueba la distribución temporal de la ocupación.
