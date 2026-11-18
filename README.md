# Cuidando Peluditos 

### Plataforma web de cuidado y alojamiento de mascotas

**Universidad Tecnológica Nacional (UTN)**  
**Trabajo Integrador Final de Carrera — Tecnicatura Universitaria en Programación**  
**Grupo:** 176  
**Docente:** Oscar Londero  
**Fecha:** noviembre de 2026

**Integrantes:**
- Macarena Marinoni — [GitHub](https://github.com/MaquiMarinoni)
- Marianela Valletto — [GitHub](https://github.com/maruvalletto)

**Estado del proyecto:** aplicación desplegada en producción, con el circuito funcional principal implementado y validado mediante pruebas automatizadas y recorridos manuales.

---

## 1. Accesos principales

| Recurso | Enlace |
|---|---|
| Aplicación web publicada | [Cuidando Peluditos — Render](https://cuidando-peluditos.onrender.com) |
| Repositorio | [Cuidando Peluditos — GitHub](https://github.com/MaquiMarinoni/TUPaD_CuidandoPeluditos_ProyFinal) |
| Informe final | [Informe Final — Grupo 176](docs/Informe_Final_Cuidando_Peluditos_G176.md) |
| Entrega 01 | [Propuesta y relevamiento UX](docs/Marinoni-Valletto_G176_Entrega01.md) |
| Entrega 02 | [Diseño y modelo de datos](docs/Marinoni-Valletto_G176_Entrega02.md) |
| Video de presentación | Pendiente de incorporar |
| Guía de ejecución local | [Ejecución con MariaDB](docs/ejecucion-local-mariadb.md) |
| Validación funcional inicial | [Validación del 12/11/2026](docs/validacion-final-2026-11-12.md) |
| Validación de producción | [Validación del 17/11/2026](docs/validacion-produccion-2026-11-17.md) |

**Rama utilizada para el despliegue:** `deploy/render`.

**Versión de referencia para el cierre funcional:** commit `7f8e372`. Las pruebas documentadas del 17/11 corresponden al código funcional desplegado mediante el commit `dce4785`.

---

## 2. Descripción del proyecto

Cuidando Peluditos es una aplicación web desarrollada para facilitar la búsqueda y coordinación de servicios de cuidado temporal de perros y gatos.

Permite que los dueños registren sus mascotas, consulten cuidadores disponibles y gestionen solicitudes de cuidado. A su vez, los cuidadores pueden configurar su perfil, publicar disponibilidades y administrar las solicitudes recibidas.

Se contemplan dos modalidades:

- **Visitas a domicilio:** el cuidador asiste al domicilio del dueño durante una franja horaria acordada.
- **Alojamiento:** las mascotas permanecen temporalmente en el domicilio del cuidador durante las fechas contratadas.

La plataforma centraliza información sobre mascotas, perfiles de cuidadores, disponibilidades, solicitudes, incidencias, valoraciones e historial de estados.

También incorpora funciones administrativas para consultar usuarios, modificar el estado de cuentas no administrativas y registrar la trazabilidad de esas operaciones.

### Objetivo general

Desarrollar una plataforma web que permita coordinar servicios de cuidado de mascotas mediante un sistema de gestión con autenticación, persistencia de datos, control de disponibilidad y seguimiento de solicitudes.

### Objetivos específicos

- Registrar usuarios con roles y permisos diferenciados.
- Gestionar mascotas y sus indicaciones de cuidado.
- Publicar perfiles y disponibilidades de cuidadores.
- Buscar cuidadores mediante filtros.
- Crear y administrar solicitudes de alojamiento y visitas.
- Controlar cupos y evitar reservas incompatibles.
- Calcular los importes de los servicios según sus condiciones.
- Proteger los datos de contacto y las direcciones privadas.
- Registrar incidencias durante los servicios.
- Permitir valoraciones posteriores a la finalización.
- Mantener el historial de estados y las operaciones administrativas relevantes.

---

## 3. Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Frontend | HTML5, CSS3, JavaScript ES6 y Bootstrap 5.3 |
| Backend | Python 3 y Flask 3 |
| Arquitectura | Application Factory y Blueprints |
| ORM | Flask-SQLAlchemy |
| Migraciones | Flask-Migrate y Alembic |
| Autenticación | Flask-Login y Flask-WTF |
| Base de datos local | MariaDB / MySQL |
| Base de datos en producción | TiDB Cloud, compatible con MySQL |
| Conector de base de datos | PyMySQL |
| Servidor de producción | Gunicorn |
| Alojamiento web | Render |
| Pruebas automatizadas | Pytest |
| Control de versiones | Git y GitHub |

### Arquitectura de producción

```text
                   USUARIO
                      |
                    HTTPS
                      |
                      v
               APLICACIÓN WEB
                    Render
                      |
                   Gunicorn
                      |
                      v
                 BACKEND FLASK
                      |
              SQLAlchemy / PyMySQL
                  Conexión TLS
                      |
                      v
                  TiDB CLOUD
               Base de datos SQL
                  persistente
```

El backend se ejecuta en Render y se conecta a TiDB Cloud mediante variables de entorno privadas.

La base de datos está separada del servicio web, por lo que los registros persistentes no dependen del almacenamiento temporal de Render.

---

## 4. Funcionalidades implementadas

### Autenticación y usuarios

- Registro de usuarios.
- Inicio y cierre de sesión.
- Roles `DUENO`, `CUIDADOR` y `ADMIN`.
- Control de acceso según usuario y permisos.
- Persistencia de información entre sesiones.
- Restricción de operaciones a usuarios autorizados.

### Gestión de mascotas

- Registro de perros y gatos.
- Consulta y actualización de información.
- Asociación de mascotas con su dueño.
- Registro de indicaciones relevantes para el cuidado.
- Desactivación lógica de mascotas.

### Gestión de cuidadores

- Creación y actualización del perfil.
- Configuración de servicios ofrecidos.
- Publicación de disponibilidades de alojamiento y visitas.
- Definición de capacidad y tarifas.
- Búsqueda de cuidadores mediante filtros.
- Consulta pública de perfiles y condiciones de servicio.

### Gestión de solicitudes

- Creación de solicitudes de alojamiento y visitas.
- Selección de cuidador y mascotas.
- Gestión de fechas y horarios.
- Aceptación y rechazo de solicitudes.
- Cancelación por los participantes según las reglas del sistema.
- Control y liberación de cupos.
- Finalización del servicio.
- Consulta del historial de estados.

### Reglas de alojamiento

- Configuración de capacidad del cuidador.
- Control de plazas disponibles por noche.
- Cálculo del importe según mascotas y noches.
- Recuperación de capacidad al cancelar una reserva.
- Tratamiento privado de la dirección de alojamiento.

### Reglas de visitas

- Publicación de franjas de disponibilidad.
- Duración mínima de 60 minutos para nuevas franjas.
- Selección de hasta tres mascotas del mismo dueño por visita.
- Cálculo de tarifa por mascota.
- Conservación de los datos históricos de servicios anteriores.

### Privacidad y contactos

- Protección de los datos de contacto de los participantes.
- Visualización de contactos de coordinación al aceptar una solicitud.
- Ocultamiento de dichos contactos al cancelar el servicio.
- Protección de la dirección privada de alojamiento.
- Presentación pública de perfiles sin exponer contactos privados.

### Incidencias

- Registro de incidencias relacionadas con servicios.
- Consulta según los permisos del usuario.
- Seguimiento y resolución de incidencias.
- Conservación de la información registrada.

### Valoraciones

- Valoración de servicios finalizados.
- Registro de calificación y comentario.
- Persistencia de las valoraciones.
- Restricciones para evitar operaciones no autorizadas.

### Administración

El sistema incorpora un panel para el rol `ADMIN`, con funcionalidades de consulta y administración de cuentas.

Permite:

- Consultar usuarios.
- Activar y desactivar cuentas no administrativas.
- Registrar un motivo para el cambio de estado.
- Conservar el historial de operaciones administrativas.
- Identificar el responsable y la fecha de cada cambio.

Las cuentas administrativas no se crean desde el registro público.

### Funcionalidades fuera del alcance implementado

El sistema no incorpora pagos reales, geolocalización en tiempo real ni aplicaciones móviles nativas.

Tampoco incluye verificación automática de identidad de los cuidadores.

---

## 5. Estructura del repositorio

```text
TUPaD_CuidandoPeluditos_ProyFinal/
|
|-- backend/
|   |-- app/
|   |   |-- admin/
|   |   |-- auth/
|   |   |-- cuidadores/
|   |   |-- disponibilidades/
|   |   |-- incidencias/
|   |   |-- mascotas/
|   |   |-- models/
|   |   |-- solicitudes/
|   |   |-- valoraciones/
|   |   `-- visitas/
|   |-- migrations/
|   |-- requirements.txt
|   `-- run.py
|
|-- frontend/
|   |-- statics/
|   `-- templates/
|
|-- database/
|   |-- README.md
|   `-- schema.sql
|
|-- docs/
|   |-- Informe_Final_Cuidando_Peluditos_G176.md
|   |-- Marinoni-Valletto_G176_Entrega01.md
|   |-- Marinoni-Valletto_G176_Entrega02.md
|   |-- auditoria-admin.md
|   |-- contactos-servicio.md
|   |-- ejecucion-local-mariadb.md
|   |-- regla-visitas-60-minutos.md
|   |-- validacion-final-2026-11-12.md
|   |-- validacion-produccion-2026-11-17.md
|   `-- evidencias/
|
|-- scripts/
|-- tests/
|-- .env.example
|-- .gitignore
`-- README.md
```

La carpeta `docs/` contiene documentación complementaria, reglas de negocio y evidencias de las pruebas realizadas.

La estructura presentada resume los directorios principales y no constituye un inventario exhaustivo de todos los archivos.

---

## 6. Ejecución de la aplicación

### Opción A — Utilizar la aplicación publicada

Para utilizar el sistema no es necesario instalar dependencias ni configurar una base de datos local.

Ingresar a:

https://cuidando-peluditos.onrender.com

Desde la aplicación es posible registrar usuarios, crear perfiles, gestionar mascotas y utilizar las funcionalidades disponibles según los permisos de cada rol.

**Importante:** debido a las características del servicio de alojamiento utilizado, la primera carga después de un período de inactividad puede demorar.

### Opción B — Ejecución local en Windows

#### Requisitos

- Python instalado.
- Git.
- Visual Studio Code o un editor equivalente.
- MariaDB o MySQL.
- Base de datos local y usuario con permisos.
- Variables de entorno configuradas.

#### Paso 1. Clonar el repositorio

```powershell
git clone https://github.com/MaquiMarinoni/TUPaD_CuidandoPeluditos_ProyFinal.git
cd TUPaD_CuidandoPeluditos_ProyFinal
```

Seleccionar la rama utilizada para el despliegue:

```powershell
git switch deploy/render
```

#### Paso 2. Crear el entorno virtual

```powershell
python -m venv venv
```

#### Paso 3. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

#### Paso 4. Instalar las dependencias

```powershell
python -m pip install -r backend/requirements.txt
```

#### Paso 5. Configurar la base de datos

Crear una base de datos local y configurar las variables de entorno tomando como referencia `.env.example`.

La guía detallada se encuentra en:

[Ejecución local con MariaDB](docs/ejecucion-local-mariadb.md).

La variable `DATABASE_URL` debe apuntar a la base local preparada para esta instalación.

No utilizar credenciales de producción ni publicar contraseñas en GitHub.

#### Paso 6. Ejecutar las migraciones

Desde la raíz del repositorio:

```powershell
python -m flask --app backend.run:app db upgrade --directory backend/migrations
python -m flask --app backend.run:app db current --directory backend/migrations
python -m flask --app backend.run:app db check --directory backend/migrations
```

La revisión esperada es:

`e72a91c4b603`

Cuando los modelos y el esquema coinciden, `db check` debe indicar que no se detectaron nuevas operaciones de migración.

**Advertencia:** no ejecutar `database/schema.sql` como mecanismo de instalación. Es un archivo histórico que contiene instrucciones capaces de eliminar tablas y datos.

#### Paso 7. Cargar los roles iniciales

Con la base local seleccionada, ejecutar en el cliente MariaDB:

```sql
INSERT IGNORE INTO roles (nombre)
VALUES ('DUENO'), ('CUIDADOR'), ('ADMIN');

SELECT id, nombre FROM roles;
```

La creación de cuentas administrativas se realiza mediante un procedimiento privado y no desde el formulario de registro público.

#### Paso 8. Iniciar el servidor

```powershell
python -m flask --app backend.run:app run --debug
```

#### Paso 9. Abrir la aplicación

Ingresar desde el navegador a:

http://127.0.0.1:5000

Las instrucciones anteriores describen el procedimiento previsto de instalación. La reconstrucción completa sobre una base vacía todavía no fue ejecutada como prueba independiente de cierre.

---

## 7. Base de datos

El proyecto utiliza un modelo relacional administrado mediante SQLAlchemy y migraciones Alembic.

La revisión vigente, verificada en TiDB Cloud el 17/11/2026, es:

```text
e72a91c4b603
```

Esta revisión incorpora el historial de cambios administrativos de cuentas y sucede a `d18a6c2f904b`, relacionada con el comentario de cierre de incidencias.

### Tablas del esquema actual

1. `roles`
2. `usuarios`
3. `mascotas`
4. `perfiles_cuidadores`
5. `disponibilidades`
6. `solicitudes`
7. `solicitudes_mascotas`
8. `incidencias`
9. `valoraciones`
10. `historial_estados`
11. `auditoria_cuentas`
12. `alembic_version` — control de revisiones de migración.

El esquema comprende once tablas de dominio y una tabla técnica de Alembic.

Los roles iniciales son `DUENO`, `CUIDADOR` y `ADMIN`.

En desarrollo se utilizó MariaDB. Para producción se configuró TiDB Cloud con conexión cifrada mediante TLS.

La documentación técnica se encuentra en [database/README.md](database/README.md).

---

## 8. Pruebas y validación

### Pruebas automatizadas

Se ejecutó la suite completa de Pytest desde la raíz del repositorio:

```powershell
python -m pytest -q
```

**Resultado local del 17/11/2026:**

```text
104 passed, 799 warnings in 76.48s
```

Las 104 pruebas finalizaron satisfactoriamente, sin fallos.

Las advertencias corresponden principalmente al uso de APIs de fecha y consultas de SQLAlchemy que requieren modernización futura. No impidieron la ejecución de las pruebas.

### Pruebas funcionales iniciales

El 12/11/2026 se documentaron doce comprobaciones manuales:

| Área | Casos aprobados |
|---|---:|
| Seguridad y permisos | 3/3 |
| Disponibilidades y cupos | 3/3 |
| Ciclo completo del servicio | 3/3 |
| Incidencias, filtros y navegación | 3/3 |
| **Total** | **12/12** |

Estas comprobaciones corresponden a una etapa anterior del proyecto y se conservan como evidencia histórica.

### Validación de producción del 17/11/2026

Se realizaron recorridos funcionales sobre la aplicación publicada en Render, conectada a TiDB Cloud.

Se verificaron los siguientes escenarios:

- Desactivación y reactivación de una cuenta desde ADMIN.
- Persistencia del historial de auditoría administrativa.
- Creación y aceptación de solicitudes de alojamiento.
- Cálculo de importe por mascota y noche.
- Control de capacidad por noche.
- Cancelación y recuperación de cupos.
- Visualización condicional de contactos.
- Rechazo de una franja de visita inferior a 60 minutos.
- Publicación de una franja válida de 60 minutos.
- Creación de una visita para dos mascotas con cálculo de tarifa.
- Aceptación y cancelación de una visita por el cuidador.
- Consulta del historial de estados.
- Consulta de una incidencia histórica resuelta.
- Consulta de una valoración histórica.
- Visualización pública de un perfil sin contactos privados.
- Redirección a autenticación al intentar solicitar cuidado sin sesión.

Las solicitudes de prueba `#120001` y `#120002` finalizaron en estado `CANCELADA`.

No se ejecutó en esta revisión un nuevo recorrido integral de creación de incidencia, resolución, finalización y valoración en producción. Las consultas de incidencias y valoraciones se realizaron sobre registros históricos.

Tampoco se efectuó una prueba nueva de carga masiva ni de concurrencia en producción.

### Persistencia y despliegue

El 17/11/2026 se confirmó:

- Despliegue satisfactorio de la aplicación en Render.
- Conexión a TiDB Cloud.
- Revisión de migración `e72a91c4b603`.
- Existencia de la tabla `auditoria_cuentas`.
- Persistencia de los registros de auditoría después de actualizar la interfaz.

### Evidencias complementarias

- [Validación funcional inicial](docs/validacion-final-2026-11-12.md).
- [Validación de producción del 17/11](docs/validacion-produccion-2026-11-17.md).
- [Auditoría administrativa](docs/auditoria-admin.md).
- [Privacidad de contactos](docs/contactos-servicio.md).
- [Regla de visitas de 60 minutos](docs/regla-visitas-60-minutos.md).
- [Pruebas en MariaDB](docs/pruebas-mariadb.md).
- [Pruebas manuales del frontend](docs/pruebas-manuales-frontend.md).

Los resultados documentan los escenarios efectivamente ejecutados y no constituyen una auditoría integral de seguridad.

---

## 9. Consideraciones de seguridad

La aplicación incorpora autenticación, sesiones, protección CSRF y controles de permisos para las operaciones implementadas.

Las contraseñas se almacenan mediante mecanismos de hashing y las credenciales de infraestructura se administran mediante variables de entorno privadas.

El acceso a información de coordinación se encuentra condicionado por el participante y el estado de la solicitud.

La presentación pública de los cuidadores no expone teléfonos, correos electrónicos ni direcciones privadas en los escenarios validados.

La implementación contempla criterios de minimización y protección de datos personales relacionados con la Ley N.º 25.326 de Protección de Datos Personales de Argentina.

El proyecto tiene carácter académico. Las pruebas realizadas no constituyen una certificación de seguridad ni de cumplimiento normativo integral.

---

## 10. Limitaciones conocidas y mejoras futuras

La versión de entrega presenta las siguientes limitaciones:

- No procesa pagos reales.
- No incorpora verificación automática de identidad de cuidadores.
- No ofrece geolocalización en tiempo real.
- No incluye aplicaciones móviles nativas.
- No se realizaron pruebas de carga masiva en producción.
- La instalación completa desde una base vacía no fue revalidada durante el cierre final.
- No se comprobó integralmente la sincronización de las marcas de tiempo con la zona horaria de Argentina.
- El servicio de alojamiento puede presentar demoras de inicio después de períodos de inactividad.

Se identificaron además oportunidades de mejora para versiones posteriores:

- Conservar el detalle abierto del panel ADMIN al actualizar la página.
- Mostrar el responsable de cada transición en el historial visual de solicitudes.
- Mejorar la actualización visual de disponibilidad y cupos.
- Modernizar las llamadas a APIs antiguas de SQLAlchemy.
- Ampliar las pruebas integrales de los recorridos funcionales en producción.
- Revisar y perfeccionar aspectos de navegación y presentación visual.

Estas observaciones no se presentan como funcionalidades implementadas ni como defectos críticos confirmados.

---

## 11. Documentación del proyecto

| Documento | Contenido |
|---|---|
| [Entrega 01](docs/Marinoni-Valletto_G176_Entrega01.md) | Propuesta, problema, objetivos e investigación UX |
| [Entrega 02](docs/Marinoni-Valletto_G176_Entrega02.md) | Diseño, reglas de negocio, DER y planificación |
| [Informe Final](docs/Informe_Final_Cuidando_Peluditos_G176.md) | Implementación, resultados y conclusiones |
| [Ejecución local](docs/ejecucion-local-mariadb.md) | Configuración y puesta en marcha |
| [Base de datos](database/README.md) | Esquema, migraciones y roles |
| [Auditoría administrativa](docs/auditoria-admin.md) | Cambios de estado y trazabilidad |
| [Contactos de servicio](docs/contactos-servicio.md) | Privacidad según estado y participante |
| [Reglas de visitas](docs/regla-visitas-60-minutos.md) | Duración mínima y validaciones |
| [Validación del 12/11](docs/validacion-final-2026-11-12.md) | Pruebas funcionales anteriores |
| [Validación del 17/11](docs/validacion-produccion-2026-11-17.md) | Recorridos en producción y capturas |

Los documentos correspondientes a entregas anteriores se conservan como antecedentes del desarrollo y pueden reflejar decisiones de diseño que evolucionaron durante la implementación.

---

## 12. Estado de la entrega

La aplicación se encuentra publicada en Render y utiliza TiDB Cloud como base de datos persistente.

El circuito funcional principal fue implementado y validado mediante pruebas automatizadas y recorridos manuales.

**Estado de referencia al 17/11/2026:**

- Rama: `deploy/render`.
- Commit de referencia: `7f8e372`.
- Código funcional desplegado y validado: `dce4785`.
- Migración vigente: `e72a91c4b603`.
- Pruebas automatizadas locales: 104 aprobadas.
- Evidencias de producción: documentadas.

Las mejoras funcionales no indispensables se reservan para una versión posterior.

---

**Cuidando Peluditos — Grupo 176**  
**Tecnicatura Universitaria en Programación — UTN**  
**Noviembre de 2026**
