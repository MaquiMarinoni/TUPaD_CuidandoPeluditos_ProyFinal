# Auditoría de cambios administrativos de cuentas

Las activaciones y desactivaciones realizadas desde ADMIN requieren un motivo de 1 a 1000 caracteres. Se guardan usuario afectado, administrador autenticado, estado anterior, estado nuevo, motivo y fecha UTC. El actor y la fecha los determina el servidor.

El cambio de cuenta y el registro se confirman en la misma transacción. Se bloquea la cuenta al modificarla; repetir el estado actual devuelve conflicto y no agrega un registro. Se conserva la restricción de no modificar cuentas ADMIN. No se borran cuentas ni solicitudes históricas.

El historial se consulta solo con rol ADMIN activo, desde el detalle de dueño o cuidador, paginado de a 20. La interfaz convierte las fechas a horario de Argentina y trata el motivo como texto. No hay operaciones públicas para editar o eliminar registros de auditoría.

Los cambios anteriores a esta funcionalidad no tienen una auditoría reconstruida. Un historial vacío no demuestra que nunca haya habido cambios previos.

## Migración y actualización

Nueva revisión: `e72a91c4b603`, posterior a `d18a6c2f904b`. Crea `auditoria_cuentas`; no cambia datos anteriores. No ejecutar downgrade en producción: elimina esta tabla y su historial.

Con conexión a la base local de pruebas y respaldo disponible:

```powershell
python -m flask --app backend.run:app db upgrade --directory backend/migrations
python -m flask --app backend.run:app db check --directory backend/migrations
```

Producción debe recibir la migración antes de activar el código que utiliza la tabla. Coordinarlo junto con el resto del cierre para una única actualización.

## Verificación

Pruebas aisladas en `tests/test_auditoria_admin.py`: actor y estados, motivo obligatorio, intento de inyectar actor, repetición, privacidad, protección ADMIN, paginación y reversión de la operación ante un fallo al guardar. 

## Resultados del 17/11/2026

- Suite aislada SQLite: 74 pruebas aprobadas, incluidas 12 nuevas de auditoría. La comprobación de sintaxis de JavaScript no informó errores.
- MariaDB local 11.4.13, base `cuidandopeluditos_pruebas`: aplicada la migración `d18a6c2f904b → e72a91c4b603`. `db check` informó `No new upgrade operations detected.`
- Navegador local: cuenta ficticia Beto Auditoria desactivada con motivo **Usuario repetido**, por Admin Prueba, ID 34. El detalle mostró Activa → Inactiva, motivo y fecha en horario de Argentina.
- La misma cuenta fue reactivada con motivo **Reactivación después de prueba local**. Se agregó Inactiva → Activa, conservando el registro anterior. La cuenta terminó activa.
- Después de F5 y de volver a abrir el detalle, los dos registros permanecieron visibles.
- Durante el recorrido se corrigió el listado ADMIN en ventanas pequeñas: cada cuenta se presenta como ficha con etiquetas, datos y acciones; se conserva la tabla en escritorio. La visualización fue confirmada durante la prueba.

La ejecución manual corresponde a MariaDB local. No acredita aplicación de la migración ni funcionamiento de la auditoría en Render/TiDB.

### Evidencias

- [Desactivación con motivo y responsable](evidencias/auditoria-admin-2026-11-17/01-desactivacion-con-motivo.png).
- [Reactivación e historial conservado](evidencias/auditoria-admin-2026-11-17/02-reactivacion-e-historial.png).

Las capturas se tomaron antes de recargar; la permanencia después de F5 se confirmó durante el recorrido, sin una captura adicional.

