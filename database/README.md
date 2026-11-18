# Base de datos de Cuidando Peluditos

## Estructura vigente

La base de la aplicación se crea y actualiza mediante las migraciones de `backend/migrations/`. Este es el procedimiento vigente para reconstruir el esquema.

Con la base de datos y el usuario local creados, y la variable `DATABASE_URL` configurada para apuntar a esa base local, ejecutar desde la raíz del repositorio:

```powershell
python -m flask --app backend.run:app db upgrade --directory backend/migrations
python -m flask --app backend.run:app db current --directory backend/migrations
python -m flask --app backend.run:app db check --directory backend/migrations
```

La revisión vigente es `e72a91c4b603`, que incorpora el historial de cambios administrativos de cuentas. Su revisión anterior es `d18a6c2f904b`, correspondiente al comentario de cierre de incidencias.

El esquema actual contiene once tablas de dominio y `alembic_version`, utilizada para registrar la revisión aplicada.

Cuando los modelos y el esquema coinciden, `db check` debe informar:

`No new upgrade operations detected.`

La creación de la base, la cuenta de desarrollo y la configuración se explican en la [guía local con MariaDB](../docs/ejecucion-local-mariadb.md).

El [ejemplo de variables](../.env.example) no contiene credenciales reales.

La instalación completa sobre una base vacía no fue revalidada durante el cierre final de noviembre de 2026.

## Roles iniciales

Después de aplicar las migraciones, cargar los roles iniciales.

Dentro del cliente MariaDB, con la base correspondiente seleccionada:

```sql
INSERT IGNORE INTO roles (nombre)
VALUES ('DUENO'), ('CUIDADOR'), ('ADMIN');

SELECT id, nombre FROM roles;
```

`seeds.sql` conserva la carga original con identificadores fijos para una base inicial.

Para una base ya utilizada, el comando anterior permite cargar los roles por nombre sin reasignar identificadores existentes.

El panel ADMIN permite consultar cuentas, activar y desactivar cuentas no administrativas y conservar un historial de estas operaciones.

Cada cambio de estado registra el motivo, la fecha y el administrador responsable.

Las cuentas ADMIN se aprovisionan mediante un procedimiento privado, no desde el registro público.

## SQL histórico de Entrega 2

`schema.sql` se conserva como antecedente del diseño presentado en la Entrega 2.

**No representa el esquema actual y no debe ejecutarse para instalar o actualizar la aplicación.** Contiene instrucciones que pueden eliminar tablas y datos.

Las migraciones incorporan las modificaciones realizadas durante el desarrollo, entre ellas:

- Horarios y condiciones de las visitas.
- Tarifas por modalidad de servicio.
- Control de disponibilidad y cupos.
- Dirección del servicio y protección de información privada.
- Información histórica de veterinarios.
- Historial de estados de solicitudes.
- Gestión de incidencias y comentario de cierre.
- Auditoría de cambios administrativos de cuentas.

Las restricciones de asociación de mascotas también evolucionaron durante la implementación. En la versión vigente se admiten visitas para hasta tres mascotas del mismo dueño, conforme a las reglas implementadas.

Las decisiones de diseño anteriores se conservan como antecedentes históricos y no deben interpretarse como restricciones vigentes cuando fueron reemplazadas por migraciones posteriores.

No combinar la carga del SQL histórico con el procedimiento de migraciones.

## Entidades de la versión actual

El esquema contiene las siguientes tablas de dominio:

1. `roles`: roles disponibles en el sistema.
2. `usuarios`: cuentas de usuarios y datos de autenticación.
3. `perfiles_cuidadores`: información de los cuidadores y condiciones del servicio.
4. `mascotas`: mascotas registradas por los dueños.
5. `disponibilidades`: fechas, horarios y capacidad de atención.
6. `solicitudes`: solicitudes de alojamiento y visitas.
7. `solicitudes_mascotas`: asociación entre solicitudes y mascotas.
8. `valoraciones`: calificaciones y comentarios de servicios finalizados.
9. `incidencias`: registro y seguimiento de incidencias.
10. `historial_estados`: cambios de estado de las solicitudes.
11. `auditoria_cuentas`: historial de activaciones y desactivaciones administrativas.

Adicionalmente, `alembic_version` registra la revisión de migraciones aplicada.

## Base de datos en producción

La aplicación publicada en Render utiliza TiDB Cloud como base de datos SQL persistente, mediante conexión cifrada TLS.

El 17/11/2026 se confirmó en producción la revisión `e72a91c4b603` y la existencia de la tabla `auditoria_cuentas`.

Las credenciales se administran mediante variables de entorno privadas y no se incorporan al repositorio.

Las comprobaciones de producción se documentan en [Validación de producción del 17/11/2026](../docs/validacion-produccion-2026-11-17.md).
