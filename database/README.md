# Base de datos de Cuidando Peluditos

## Estructura vigente

La base de la aplicación se crea y actualiza con las migraciones de `backend/migrations/`. Este es el único procedimiento vigente para reconstruir el esquema.

Con la base y el usuario local creados y `DATABASE_URL` configurada en la misma terminal, ejecutar desde la raíz del repositorio:

```powershell
python -m flask --app backend.run:app db upgrade --directory backend/migrations
python -m flask --app backend.run:app db current --directory backend/migrations
python -m flask --app backend.run:app db check --directory backend/migrations
```

La revisión vigente es `c0af3fd5552a`. La estructura contiene diez tablas de dominio y `alembic_version`, que registra la revisión aplicada. `db check` debe informar `No new upgrade operations detected.` cuando modelos y esquema coinciden.

La creación de la base, la cuenta de desarrollo y la configuración se explican en la [guía local con MariaDB](../docs/ejecucion-local-mariadb.md). El [ejemplo de variables](../.env.example) no contiene credenciales reales.

## Roles iniciales

Después de aplicar las migraciones, cargar los roles. Dentro del cliente MariaDB, con la base correspondiente seleccionada:

```sql
INSERT IGNORE INTO roles (nombre) VALUES ('DUENO'), ('CUIDADOR'), ('ADMIN');
SELECT id, nombre FROM roles;
```

`seeds.sql` conserva la carga original con identificadores fijos para una base inicial. Para una base ya utilizada, el comando anterior carga por nombre sin reasignar identificadores. ADMIN se reserva para una extensión posterior; su existencia no implica un panel administrativo implementado.

## SQL histórico de Entrega 2

`schema.sql` se conserva como antecedente del diseño presentado en Entrega 2. No representa el esquema actual ni debe ejecutarse para instalar o actualizar la aplicación. Contiene instrucciones que eliminan tablas y datos.

Las migraciones incorporan las correcciones posteriores: horarios de visitas, tarifa por visita, límite de urgencias, dirección del servicio, veterinario histórico, restricción de mascota única por solicitud, historial de estados y autorización de urgencias desactivada por defecto. No combinar la carga del SQL histórico con el procedimiento de migraciones.

## Entidades de la versión actual

Roles, usuarios, perfiles de cuidadores, mascotas, disponibilidades, solicitudes, mascotas asociadas a solicitudes, valoraciones, incidencias e historial de estados. La tabla adicional alembic_version registra la revisión aplicada.
