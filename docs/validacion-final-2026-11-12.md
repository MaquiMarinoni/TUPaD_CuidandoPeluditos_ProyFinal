# Validación funcional final — 12/11/2026

## Alcance y entorno

Proyecto Cuidando Peluditos. Integración de `feature/frontend-maru` y `back` en `integration/tpi-final`. Aplicación Flask, Jinja2/Bootstrap/JS y base de pruebas `cuidandopeluditos_pruebas`, instalada con MariaDB mediante XAMPP en Windows.

Los datos de prueba P1 son ficticios y se eliminan tras cada ejecución. La prueba usa `Flask.test_client()` con sesiones reales, tokens CSRF y transacciones confirmadas en MariaDB; no equivale a una prueba de navegador de esos formularios.

## Resultados confirmados

| Caso | Resultado | Evidencia |
| --- | --- | --- |
| Incidencias (SQLite de pruebas) | 4/4 aprobadas | `tests/test_incidencias.py` |
| Valoraciones (SQLite de pruebas) | 4/4 aprobadas | `tests/test_valoraciones.py` |
| Privacidad de solicitudes (SQLite de pruebas) | 5/5 aprobadas | `tests/test_privacidad_solicitudes.py` |
| Finalización (SQLite de pruebas) | 1/1 aprobada | `tests/test_finalizacion.py` |
| Finalización histórica real en MariaDB | HTTP 200, historial y persistencia; doble finalización HTTP 409; limpieza correcta | `scripts/prueba_finalizacion_mariadb.py`, ejecución local informada el 12/11 |
| P1: incidencias en MariaDB | Creación, consulta, resolución, persistencia y restricciones de acceso confirmadas | [Salida P1 MariaDB](evidencias/p1-mariadb-2026-11-12.txt) |
| P1: valoraciones en MariaDB | Registro, promedio, persistencia y bloqueos por duplicación/rol/estado confirmados | [Salida P1 MariaDB](evidencias/p1-mariadb-2026-11-12.txt) |
| Navegación del frontend integrado | Registro, mascotas, cuidadores y solicitudes comprobados manualmente | Comprobación local comunicada el 12/11 |

## Reproducción

```powershell
# Activar venv, configurar DATABASE_URL contra una base terminada en _pruebas
python -m flask --app backend.run:app db current --directory backend/migrations
python -m scripts.prueba_finalizacion_mariadb
python -m scripts.prueba_p1_mariadb
python -m pytest tests/test_incidencias.py tests/test_valoraciones.py tests/test_privacidad_solicitudes.py tests/test_finalizacion.py -q
```

No ejecutar los scripts de prueba contra la base principal. No guardar claves ni URLs con credenciales en los informes.

## Límites y pendientes

- Las pruebas P1 de MariaDB validan los endpoints mediante un cliente HTTP de Flask, no la interacción manual completa de los formularios en navegador.
- La carga y uso de los nuevos formularios P1 debe verificarse visualmente antes de declarar completada la experiencia de usuario.
- Esta validación no representa pruebas de rendimiento ni una auditoría integral de seguridad.
- La publicación final en `main`, el ZIP y la defensa se documentan cuando efectivamente se completen.

## Observaciones

Los avisos por `datetime.utcnow()` y `Query.get()` corresponden a APIs deprecadas. No impidieron las pruebas registradas.
