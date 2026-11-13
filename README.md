 
# Cuidando Peluditos 🐾

### Plataforma web de cuidado y alojamiento de mascotas

**Universidad Tecnológica Nacional (UTN)**  
**Trabajo Integrador Final de Carrera — Tecnicatura Universitaria en Programación**  
**Grupo:** 176  
**Docente:** Oscar Londero  
**Fecha:** noviembre de 2026

**Integrantes:**
- Macarena Marinoni — [GitHub](https://github.com/MaquiMarinoni)
- Marianela Valletto — [GitHub](https://github.com/maruvalletto)

**Estado del proyecto:** aplicación desplegada y circuito funcional principal validado.

---

## 1. Accesos principales

| Recurso | Enlace |
|---|---|
| Aplicación web publicada | [Cuidando Peluditos — Render](https://cuidando-peluditos.onrender.com) |
| Informe final | [Informe Final — Grupo 176](docs/Informe_Final_Cuidando_Peluditos_G176.md) |
| Entrega 01 | [Propuesta y relevamiento UX](docs/Marinoni-Valletto_G176_Entrega01.md) |
| Entrega 02 | [Diseño y modelo de datos](docs/Marinoni-Valletto_G176_Entrega02.md) |
| Video de presentación | Pendiente de incorporar |
| Guía de ejecución local | [Ejecución con MariaDB](docs/ejecucion-local-mariadb.md) |
| Evidencias de pruebas | [Validación final](docs/validacion-final-2026-11-12.md) |

**Repositorio:**  
https://github.com/MaquiMarinoni/TUPaD_CuidandoPeluditos_ProyFinal

**Rama utilizada para el despliegue:** `deploy/render`.

> El video y la versión PDF del informe deben incorporarse antes de cerrar la entrega académica, si son exigidos por la consigna.

---

## 2. Descripción del proyecto

Cuidando Peluditos es una aplicación web desarrollada para facilitar la búsqueda y coordinación de servicios de cuidado temporal de perros y gatos.

Permite que los dueños registren sus mascotas, consulten cuidadores disponibles y gestionen solicitudes de cuidado. A su vez, los cuidadores pueden configurar su perfil, publicar disponibilidades y administrar las solicitudes recibidas.

Se contemplan dos modalidades:

- **Visitas a domicilio:** el cuidador asiste al domicilio del dueño en las fechas y horarios acordados.
- **Alojamiento:** la mascota permanece temporalmente en el hogar del cuidador.

La plataforma centraliza información sobre mascotas, disponibilidad, condiciones del servicio, solicitudes, incidencias y valoraciones.

### Objetivo general

Desarrollar una plataforma web que permita coordinar servicios de cuidado de mascotas mediante un sistema de gestión con autenticación, persistencia de datos, control de disponibilidad y seguimiento de solicitudes.

### Objetivos específicos

- Registrar usuarios con roles diferenciados.
- Gestionar mascotas y sus indicaciones de cuidado.
- Publicar perfiles y disponibilidades de cuidadores.
- Buscar cuidadores mediante filtros.
- Crear y administrar solicitudes de cuidado.
- Controlar cupos y evitar reservas incompatibles.
- Registrar incidencias durante los servicios.
- Permitir valoraciones posteriores a la finalización.

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
                     | HTTPS
                     v
            APLICACIÓN WEB
                 Render
                     |
                     | Gunicorn
                     v
              BACKEND FLASK
                     |
                     | SQLAlchemy / PyMySQL
                     | Conexión TLS
                     v
                TiDB CLOUD
             Base de datos SQL
                persistente
```

El backend se ejecuta en Render y se conecta a TiDB Cloud mediante variables de entorno privadas.

La base de datos se encuentra separada del servicio web, por lo que los registros no dependen del almacenamiento temporal del servidor de Render.

---

## 4. Funcionalidades implementadas

### Autenticación y usuarios

- Registro de usuarios.
- Inicio y cierre de sesión.
- Roles Dueño y Cuidador.
- Control de acceso según usuario y permisos.
- Persistencia de información entre sesiones.

### Gestión de mascotas

- Registro de perros y gatos.
- Consulta y actualización de información.
- Asociación de mascotas con su dueño.
- Registro de indicaciones relevantes para el cuidado.

### Gestión de cuidadores

- Creación y actualización del perfil.
- Configuración de servicios y disponibilidad.
- Búsqueda de cuidadores.
- Filtros por ubicación, especie y fechas.

### Gestión de solicitudes

- Creación de solicitudes de cuidado.
- Selección de cuidador y mascotas.
- Gestión de fechas y horarios.
- Aceptación y rechazo.
- Cancelación y liberación de cupos.
- Finalización del servicio.
- Historial de estados.

### Incidencias

- Registro de incidencias relacionadas con servicios.
- Consulta según permisos.
- Resolución de incidencias.

### Valoraciones

- Valoración de servicios finalizados.
- Calificación y comentario.
- Persistencia de las valoraciones registradas.

### Funcionalidades fuera del alcance implementado

El modelo de datos contempla el rol `ADMIN`, pero el panel administrativo de moderación y métricas, clasificado como P2, no forma parte de las funcionalidades operativas validadas en esta entrega.

Tampoco se incluyen pagos reales, geolocalización en tiempo real ni aplicaciones móviles nativas.

---

## 5. Estructura del repositorio

```text
TUPaD_CuidandoPeluditos_ProyFinal/
|
|-- backend/
|   |-- app/
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
|   |-- ejecucion-local-mariadb.md
|   `-- validacion-final-2026-11-12.md
|
|-- scripts/
|-- tests/
|-- .env.example
|-- .gitignore
`-- README.md
```

La carpeta `docs/` contiene también documentación complementaria y evidencias de pruebas.

---

## 6. Ejecución de la aplicación

### Opción A — Utilizar la aplicación publicada

Para utilizar el sistema no es necesario instalar dependencias ni configurar una base de datos local.

Abrir:

https://cuidando-peluditos.onrender.com

Desde allí es posible registrar usuarios de prueba, crear perfiles, gestionar mascotas y utilizar las funcionalidades disponibles.

**Importante:** debido a las características del plan gratuito de Render, la primera carga después de un período de inactividad puede demorar.

### Opción B — Ejecución local en Windows

#### Requisitos

- Python instalado.
- Git.
- Visual Studio Code.
- MariaDB o MySQL.
- Base de datos configurada.
- Variables de entorno locales.

#### Paso 1. Clonar el repositorio

```powershell
git clone https://github.com/MaquiMarinoni/TUPaD_CuidandoPeluditos_ProyFinal.git

cd TUPaD_CuidandoPeluditos_ProyFinal
```

Para trabajar con la versión utilizada en el despliegue:

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

Preparar una base de datos local y configurar el archivo `.env` tomando como referencia `.env.example`.

No publicar contraseñas ni credenciales en GitHub.

Para la configuración detallada de MariaDB, consultar:

[Guía de ejecución local](docs/ejecucion-local-mariadb.md).

#### Paso 6. Ejecutar las migraciones

```powershell
python -m flask --app backend.run:app db upgrade --directory backend/migrations
```

Las migraciones deben ejecutarse sobre una base de datos local preparada para el proyecto.

No ejecutar `database/schema.sql` sobre una base con datos existentes: se conserva como antecedente histórico y no es el mecanismo vigente de migración.

#### Paso 7. Iniciar el servidor

```powershell
python -m flask --app backend.run:app run --debug
```

#### Paso 8. Abrir la aplicación

Ingresar desde el navegador a:

http://127.0.0.1:5000

La configuración local debe mantenerse separada de las credenciales utilizadas en producción.

---

## 7. Base de datos

El proyecto utiliza un modelo relacional administrado mediante SQLAlchemy y migraciones Alembic.

La versión de migraciones aplicada en producción es:

```text
c0af3fd5552a
```

Se verificó la creación de 11 tablas:

1. `alembic_version`
2. `roles`
3. `usuarios`
4. `mascotas`
5. `perfiles_cuidadores`
6. `disponibilidades`
7. `solicitudes`
8. `solicitudes_mascotas`
9. `incidencias`
10. `valoraciones`
11. `historial_estados`

Los roles iniciales son `DUENO`, `CUIDADOR` y `ADMIN`.

En desarrollo se utilizó MariaDB. Para producción se configuró TiDB Cloud, con conexión cifrada mediante TLS.

**La existencia del rol ADMIN en la base de datos no implica que exista un panel administrativo implementado.**

La documentación técnica se encuentra en [database/README.md](database/README.md).

---

## 8. Pruebas y validación

### Pruebas automatizadas

Se ejecutó la suite de Pytest:

```powershell
python -m pytest -q
```

**Resultado registrado: 21 pruebas aprobadas.**

Las advertencias de dependencias obsoletas no impidieron la ejecución satisfactoria de las pruebas.

### Pruebas funcionales en producción

Se realizaron 12 comprobaciones funcionales sobre la aplicación publicada, con resultado satisfactorio en los escenarios informados.

| Área | Casos aprobados |
|---|---:|
| Seguridad y permisos | 3/3 |
| Disponibilidades y cupos | 3/3 |
| Ciclo completo del servicio | 3/3 |
| Incidencias, filtros y navegación | 3/3 |
| **Total** | **12/12** |

Los recorridos incluyeron:

- Acceso restringido sin autenticación.
- Protección de información y operaciones entre usuarios.
- Validación de disponibilidad y cupos.
- Creación y aceptación de solicitudes.
- Cancelación y liberación de cupos.
- Finalización de servicios.
- Registro y persistencia de valoraciones.
- Registro y resolución de incidencias.
- Búsqueda mediante filtros.
- Visualización en pantallas estrechas.

### Persistencia en producción

Se verificó que:

- Los usuarios permanecen registrados después de cerrar sesión.
- Las mascotas permanecen almacenadas.
- Los registros continúan disponibles después de reiniciar el servicio web de Render.

Estas pruebas permiten validar los escenarios ejecutados, pero no equivalen a una auditoría integral de seguridad ni a una prueba de carga masiva.

### Evidencias complementarias

- [Validación final](docs/validacion-final-2026-11-12.md).
- [Pruebas en MariaDB](docs/pruebas-mariadb.md).
- [Pruebas manuales del frontend](docs/pruebas-manuales-frontend.md).

---

## 9. Consideraciones de seguridad

La aplicación incorpora autenticación, sesiones, protección CSRF y validaciones de permisos para las operaciones implementadas.

Las contraseñas de usuarios se almacenan mediante mecanismos de hashing y las credenciales de infraestructura se administran mediante variables de entorno.

La implementación contempla criterios de minimización de datos personales relacionados con la Ley N.º 25.326 de Protección de Datos Personales de Argentina.

El proyecto es de carácter académico. Las pruebas realizadas no constituyen una certificación de seguridad ni de cumplimiento normativo integral.

---

## 10. Limitaciones conocidas

- El panel administrativo P2 no se encuentra implementado como módulo operativo.
- No se procesan pagos reales.
- No existe verificación automática de identidad de los cuidadores.
- No se realizaron pruebas de carga masiva en producción.
- El servicio gratuito de Render puede presentar demoras de inicio después de períodos de inactividad.
- Durante la validación se identificó una diferencia entre la hora del servidor y los horarios de Argentina. Se propuso configurar la zona horaria de Render; corresponde conservar evidencia de la revalidación posterior.

---

## 11. Documentación del proyecto

La documentación se organiza en los siguientes archivos:

| Documento | Contenido |
|---|---|
| [Entrega 01](docs/Marinoni-Valletto_G176_Entrega01.md) | Propuesta, problema, objetivos e investigación UX |
| [Entrega 02](docs/Marinoni-Valletto_G176_Entrega02.md) | Diseño, reglas de negocio, DER y planificación |
| [Informe Final](docs/Informe_Final_Cuidando_Peluditos_G176.md) | Implementación, resultados y conclusiones |
| [Ejecución local](docs/ejecucion-local-mariadb.md) | Configuración y puesta en marcha |
| [Base de datos](database/README.md) | Esquema, migraciones y roles |
| [Validación final](docs/validacion-final-2026-11-12.md) | Evidencias y pruebas ejecutadas |

---

## 12. Estado de la entrega

La aplicación se encuentra publicada y el circuito principal de Dueño y Cuidador fue validado mediante pruebas automatizadas y manuales.

Para el cierre académico deben verificarse:

- La incorporación del Informe Final en formato PDF.
- La publicación y vinculación del video de presentación.
- La accesibilidad de todos los enlaces desde una sesión externa.
- La identificación del commit o etiqueta de la versión definitiva.
- La correspondencia entre el código desplegado, el informe y el video.

**Versión de referencia:** rama `deploy/render`.

---

**Cuidando Peluditos — Grupo 176**  
**Tecnicatura Universitaria en Programación — UTN**  
**Noviembre de 2026**
