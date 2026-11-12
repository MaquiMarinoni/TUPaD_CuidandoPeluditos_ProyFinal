# Validación funcional final — 12/11/2026

## Alcance

Proyecto Cuidando Peluditos, versión conjunta en `integration/tpi-final`. Este registro reúne tres verificaciones diferentes: el recorrido manual del navegador sobre MariaDB, los scripts de integración sobre MariaDB y las pruebas automatizadas aisladas con SQLite. Los resultados de un entorno no se atribuyen al otro.

## 1. Recorrido manual del navegador con MariaDB

Ejecución manual: Marianela, el 12/11/2026. Windows, Edge, Flask en el puerto 5001 y **MariaDB 11.4.13**, instalada como servicio independiente, con la base `cuidandopeluditos_pruebas`.

La conexión se comprobó mediante `SELECT DATABASE(), VERSION()`. Las migraciones se aplicaron sin errores y `db check` no detectó diferencias entre los modelos y el esquema.

| Caso | Resultado observado |
| --- | --- |
| Incidencias | El cuidador registró y resolvió una incidencia en la solicitud sintética #12. La dueña pudo consultarla sin controles para crearla o resolverla. |
| Finalización | El cuidador finalizó la solicitud histórica sintética #13 desde la web. Se conservó el historial PENDIENTE → ACEPTADA → FINALIZADA. |
| Valoración | La dueña publicó 5/5 y un comentario ficticio en #13. La valoración registrada reemplazó el formulario. |
| Persistencia | La incidencia abierta, su posterior resolución, la finalización y la valoración se conservaron después de F5. |
| Ventana reducida | Tarjetas y comentarios legibles. Se corrigió el menú para distribuir los enlaces en varias filas y se revisó nuevamente en escritorio. |
| Teclado | Foco visible y avance y retroceso con Tab y Shift+Tab en el recorrido revisado de Mis servicios. |

Detalle y capturas: [Pruebas manuales P1 y navegación](pruebas-visuales-p1-2026-11-12.md).

Los servicios #12 y #13 se prepararon directamente mediante los modelos con fechas adecuadas para estos casos. No corresponden a servicios reales ni prueban su creación desde el navegador. Estos datos ficticios permanecen en la base local y la reserva original de Luna se conservó.

## 2. Scripts de integración con MariaDB

La validación de backend incorporada a la integración el 12/11 se realizó con MariaDB 10.4.32 mediante XAMPP, en una base separada de pruebas. Los scripts usan `Flask.test_client()` con sesiones autenticadas, tokens CSRF y persistencia en MariaDB. Es una ejecución diferente del recorrido manual anterior.

| Caso | Resultado registrado | Evidencia |
| --- | --- | --- |
| Finalización histórica | HTTP 200, historial y persistencia; segunda finalización HTTP 409; limpieza correcta | `scripts/prueba_finalizacion_mariadb.py`, ejecución informada el 12/11 |
| Incidencias | Creación, consulta, resolución, persistencia y restricciones de acceso | [Salida P1 MariaDB](evidencias/p1-mariadb-2026-11-12.txt) |
| Valoraciones | Registro, promedio, persistencia y bloqueos por duplicación, rol y estado | [Salida P1 MariaDB](evidencias/p1-mariadb-2026-11-12.txt) |

Estos scripts crean y eliminan sus propias entidades ficticias. Esta limpieza no se aplica a los datos del recorrido manual.

Para repetirlos, configurar `DATABASE_URL` contra una base MariaDB terminada en `_pruebas` y ejecutar:

```powershell
python -m scripts.prueba_finalizacion_mariadb
python -m scripts.prueba_p1_mariadb
```

## 3. Pruebas automatizadas aisladas con SQLite

Este bloque corresponde a las pruebas aisladas incorporadas a la integración. Usa SQLite de pruebas; no es el motor utilizado en el recorrido manual de Marianela ni en los scripts de integración con MariaDB.

| Caso | Resultado registrado | Archivo |
| --- | --- | --- |
| Incidencias | 4/4 aprobadas | `tests/test_incidencias.py` |
| Valoraciones | 4/4 aprobadas | `tests/test_valoraciones.py` |
| Privacidad de solicitudes | 5/5 aprobadas | `tests/test_privacidad_solicitudes.py` |
| Finalización | 1/1 aprobada | `tests/test_finalizacion.py` |

```powershell
python -m pytest tests/test_incidencias.py tests/test_valoraciones.py tests/test_privacidad_solicitudes.py tests/test_finalizacion.py -q
```

## Observaciones

Los avisos por `datetime.utcnow()` y `Query.get()` corresponden a APIs deprecadas. No impidieron las pruebas automatizadas registradas.

## Cancelación por el cuidador

Se incorporó la cancelación de reservas aceptadas por el cuidador antes del inicio. Recorrido manual confirmado en MariaDB y siete pruebas aisladas adicionales aprobadas: [Registro y evidencias](pruebas-cancelacion-cuidador-2026-11-12.md).

## Retiro e ingreso de alojamiento el mismo día

Prueba ejecutada sobre MariaDB: con capacidad 1 se aceptaron dos reservas consecutivas y se impidió una tercera con superposición real. Estados consultados antes de cancelar las tres solicitudes de prueba: [Registro de recambio de alojamiento](pruebas-recambio-alojamiento-2026-11-12.md).
