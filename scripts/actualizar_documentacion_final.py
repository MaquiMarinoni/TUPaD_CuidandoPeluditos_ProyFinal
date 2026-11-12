"""Actualiza documentación del cierre sin sobrescribir informes originales.

Ejecutar DESPUÉS de la prueba P1: python -m scripts.actualizar_documentacion_final
"""
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidencias/p1-mariadb-2026-11-12.txt'
if not EVIDENCE.is_file() or 'TODAS LAS PRUEBAS P1 PASARON' not in EVIDENCE.read_text(encoding='utf-8'):
    raise SystemExit('ERROR: falta evidencia exitosa de la prueba P1. Ejecutar primero python -m scripts.prueba_p1_mariadb')


def insert_once(path, marker, addition, anchor=None):
    text = path.read_text(encoding='utf-8')
    if marker in text:
        print(f'[OK] Ya actualizado: {path.relative_to(ROOT)}')
        return
    if anchor is not None:
        if anchor not in text:
            raise SystemExit(f'ERROR: no se encontró el ancla en {path}. No se modificó el archivo.')
        text = text.replace(anchor, addition + '\n\n' + anchor, 1)
    else:
        text += '\n\n' + addition + '\n'
    path.write_text(text, encoding='utf-8')
    print(f'[OK] Actualizado: {path.relative_to(ROOT)}')


readme = ROOT / 'README.md'
readme_text = readme.read_text(encoding='utf-8')
if '**Estado Actual:** Entrega 02 — Diseño y Módulos' in readme_text:
    readme.write_text(readme_text.replace(
        '**Estado Actual:** Entrega 02 — Diseño y Módulos',
        '**Estado Actual:** Integración y validación funcional P0/P1 — noviembre de 2026', 1), encoding='utf-8')

intro = '''## Validación final de implementación — 12/11/2026

La versión conjunta integra la interfaz de Maru con el backend de los módulos P0 y P1. Las pruebas automatizadas de incidencias, valoraciones, privacidad y finalización terminaron con **14 pruebas aprobadas**. También se comprobó la finalización positiva e historial en MariaDB con un servicio ficticio y limpieza posterior.

La prueba P1 en la base aislada `cuidandopeluditos_pruebas` verificó por HTTP autenticado la creación, consulta, resolución y persistencia de incidencias; la creación, listado, promedio y persistencia de valoraciones; y controles de permisos, duplicados y estados. La salida se conserva en [evidencias de P1 en MariaDB](docs/evidencias/p1-mariadb-2026-11-12.txt).

- [Instrucciones de ejecución actualizadas](docs/ejecucion-local-mariadb.md)
- [Registro de validación final y pendientes](docs/validacion-final-2026-11-12.md)
- [Antecedentes de pruebas de MariaDB](docs/pruebas-mariadb.md)

**Alcance:** se validó el código y la persistencia para los casos indicados, sin afirmar despliegue público ni auditoría de seguridad completa.
'''
insert_once(readme, '## Validación final de implementación — 12/11/2026', intro, '## 1. Descripción del proyecto')

guide = ROOT / 'docs/ejecucion-local-mariadb.md'
addition = '''## Actualización de cierre: XAMPP y módulos P1 (12/11/2026)

La guía original describe el entorno MariaDB 11.4 utilizado por Marianela. El proyecto también se ejecutó con **MariaDB 10.4.32 instalado mediante XAMPP** en Windows. No es necesario instalar otra instancia si el servicio `mysql_xampp` ya está iniciado.

Desde la raíz del repositorio, activar el entorno virtual que ya se creó. Configurar `DATABASE_URL` para que apunte a **`cuidandopeluditos_pruebas`**, nunca a la base principal para ejecutar pruebas con datos ficticios. Si la terminal está recién abierta, volver a configurar la variable: no se conserva entre terminales. Utilizar las credenciales que correspondan al servidor local; no guardarlas en Git ni en evidencias.

```powershell
# Revisar SOLO el nombre de la base, sin imprimir contraseñas:
python -c "from backend.app import create_app; a=create_app(); print(a.config['SQLALCHEMY_DATABASE_URI'].rsplit('@',1)[-1].split('?')[0])"

# Verificar migraciones (con DATABASE_URL ya configurada):
python -m flask --app backend.run:app db current --directory backend/migrations
python -m flask --app backend.run:app db check --directory backend/migrations

# Aplicación completa:
python -m flask --app backend.run:app run --host 127.0.0.1 --port 5001 --no-debugger --no-reload
```

Abrir `http://127.0.0.1:5001/`. Para comprobar la funcionalidad P1 no hace falta un servidor Flask aparte: el script usa el cliente HTTP de pruebas de Flask con MariaDB real.

```powershell
# Desde la raíz y con DATABASE_URL apuntando a la base _pruebas:
python -m scripts.prueba_finalizacion_mariadb
python -m scripts.prueba_p1_mariadb
python -m pytest tests/test_incidencias.py tests/test_valoraciones.py tests/test_privacidad_solicitudes.py tests/test_finalizacion.py -q
```

La prueba P1 elimina las entidades ficticias que genera y escribe su evidencia en `docs/evidencias/p1-mariadb-2026-11-12.txt`. Si falla, no debe declararse aprobada. Los scripts originales de regresión pueden generar otras reservas de prueba y deben ejecutarse únicamente sobre una base aislada.
'''
insert_once(guide, '## Actualización de cierre: XAMPP y módulos P1 (12/11/2026)', addition, '## 1. Dependencias')

old = ROOT / 'docs/pruebas-mariadb.md'
notice = '''> **Actualización posterior — 12/11/2026:** este informe conserva íntegramente los resultados históricos del 11/11. Los pendientes registrados entonces se verificaron posteriormente: finalización positiva en MariaDB (script `prueba_finalizacion_mariadb.py`), 14 pruebas automatizadas de cierre y prueba real de incidencias y valoraciones en MariaDB (evidencia [P1](evidencias/p1-mariadb-2026-11-12.txt)). Véase [validación final](validacion-final-2026-11-12.md). Las notas de “pendiente” que siguen describen el estado al **11/11**, no el estado actualizado.''' 
insert_once(old, '> **Actualización posterior — 12/11/2026:**', notice, '## Entorno')

report = ROOT / 'docs/validacion-final-2026-11-12.md'
if not report.exists():
    report.write_text('''# Validación funcional final — 12/11/2026

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
''', encoding='utf-8')
    print('[OK] Creado: docs/validacion-final-2026-11-12.md')
else:
    print('[OK] Informe de validación ya existe; no se sobrescribió')
print('DOCUMENTACION ACTUALIZADA. Revisar git diff antes del commit.')
