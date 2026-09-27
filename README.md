<div>

UNIVERSIDAD TECNOLOGICA NACIONAL

# CUIDANDO PELUDITOS
### Plataforma de cuidado y alojamiento de mascotas

**TRABAJO INTEGRADOR FINAL DE CARRERA**  
**Grupo:** 176  

**Integrantes:**  
**Macarena Marinoni** — [@MaquiMarinoni](https://github.com/MaquiMarinoni) ([marinonimacarena@gmail.com](mailto:marinonimacarena@gmail.com))  
**Marianela Valletto** — [@maruvalletto](https://github.com/maruvalletto) ([maruvalletto@gmail.com](mailto:maruvalletto@gmail.com))  

**Docente:** Oscar Londero  
**Estado Actual:** Entrega 02 — Diseño y Módulos


---

</div>

<div align="justify">

## 1. Descripción del proyecto

**Cuidando Peluditos** es un proyecto de plataforma web que busca facilitar la búsqueda y coordinación de servicios de cuidado para perros y gatos ante viajes, compromisos laborales o imprevistos. Contempla dos modalidades: alojamiento en el hogar del cuidador y visitas al domicilio del dueño.

La propuesta reúne perfiles de cuidadores, condiciones de convivencia y disponibilidad para que los dueños puedan comparar alternativas y enviar solicitudes para una o varias mascotas. El diseño contempla el control de cupos para evitar reservas incompatibles, la conservación de las indicaciones de cuidado de cada servicio, el registro de incidencias y las valoraciones asociadas a servicios finalizados.

---

## 2. Documentación de entregas

El repositorio reúne los informes de las entregas y la documentación del modelo de datos:

* **[Entrega 01 — Propuesta de Proyecto y relevamiento UX](docs/Marinoni-Valletto_G176_Entrega01.md):** Presenta el problema, la propuesta de valor y los resultados de la investigación con usuarios: cinco entrevistas semiestructuradas, un card sorting con diez participantes y pruebas de usabilidad con una duración promedio del recorrido de 54 segundos.
* **[Entrega 02 — Diseño, DER y módulos a desarrollar](docs/Marinoni-Valletto_G176_Entrega02.md):** Describe las reglas de negocio, el modelo de datos, los estados de las solicitudes, la arquitectura, los módulos priorizados y el escenario de prueba integral.
* **[Directorio de Base de Datos](database/):**  Contiene el script de creación de tablas (`schema.sql`), los roles iniciales (`seeds.sql`) y la documentación del diagrama entidad-relación (DER) en Mermaid.

---

## 3. Stack tecnológico

| Capa | Tecnologías | Justificación Técnica y Curricular |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript ES6, Bootstrap 5.3 | Interfaz responsiva tradicional basada en componentes y prototipos UX previamente validados con usuarios del público objetivo. |
| **Backend** | Python 3.10+, Flask 3.x | Arquitectura modular desacoplada mediante el patrón *Application Factory* y *Blueprints* organizados por dominio. |
| **Persistencia / ORM** | Flask-SQLAlchemy 3.x, Flask-Migrate (Alembic) | Mapeo objeto-relacional de entidades, control de transacciones ACID y evolución versionada del esquema. |
| **Base de Datos** | MySQL 8.x / MariaDB (InnoDB) | Motor relacional con integridad referencial estricta, restricciones de unicidad, índices B-Tree y bloqueo pesimista (`SELECT ... FOR UPDATE`). |
| **Seguridad y Normativa** | Flask-Login, Werkzeug Security, Ley N° 25.326 | Sesiones seguras, hashing irreversible de contraseñas, permisos por rol (`DUENO`, `CUIDADOR`, `ADMIN`) y principio de minimización de datos sensibles y domicilios exactos. |
| **Testing** | Pytest | Suite de pruebas automatizadas para validación de agenda, solapamientos y condiciones de carrera concurrentes. |

---

## 4. Estructura del repositorio

```text
TUPaD_CuidandoPeluditos_ProyFinal/
├── backend/                      # Arquitectura del servidor 
│   ├── auth/                     # Módulo de autenticación y sesiones seguras
│   ├── cuidadores/               # Módulo de perfiles, tarifas y disponibilidad
│   ├── incidencias/              # Módulo de contingencias e imprevistos
│   ├── mascotas/                 # Módulo de CRUD de mascotas
│   ├── solicitudes/              # Módulo central de máquina de estados y cupos
│   ├── valoraciones/             # Módulo de reseñas verificadas post-servicio
│   └── README.md                 # Documentación de la capa backend
├── frontend/                     # Capa de presentación (interfaz de usuario)
│   ├── statics/                  # Hojas de estilo CSS, JS cliente e imágenes
│   ├── templates/                # Plantillas Jinja2 / HTML organizadas por módulo
│   └── README.md                 # Documentación técnica de la capa frontend
├── database/                     # Definición del modelo de datos relacional
│   ├── schema.sql                # Script DDL formal
│   ├── seeds.sql                 # Script DML con roles iniciales del sistema
│   └── README.md                 # Documentación del DER 
├── docs/                         # Informes
│   ├── Marinoni-Valletto_G176_Entrega01.md  # Informe de la entrega 01
│   ├── Marinoni-Valletto_G176_Entrega02.md  # Informe de la entrega 02
│   └── estilos.css                          # Estilos para renderizado y exportación a PDF
├── .github/                      # Pautas de diagramas Mermaid
├── .vscode/                      # Configuración del espacio de trabajo
├── .gitignore                    # Reglas de exclusión de Git
└── README.md                     # Portada del repositorio
```

---

## 5. Módulos funcionales y priorización

Los módulos se organizan en tres niveles de prioridad según su importancia para el alcance del proyecto: P0 (núcleo del MVP), P1 (funcionalidades complementarias obligatorias) y P2 (extensiones posteriores al MVP).

* **P0 — Núcleo del MVP:**
  * `auth`: Registro, login y roles diferenciados (`DUENO`, `CUIDADOR`, `ADMIN`).
  * `mascotas`: ABM de perros y gatos asociados al dueño y sus cuidados especiales.
  * `cuidadores`: Perfil público, tarifas, condiciones declaradas de convivencia y calendario de disponibilidad.
  * `solicitudes`: Gestión del ciclo de las solicitudes de cuidado para una o varias mascotas, conservación de las indicaciones de cuidado al crear la solicitud y control de cupos para evitar reservas incompatibles.
* **P1 — Complementarios Obligatorios:**
  * `valoraciones`: Calificación de 1 a 5 estrellas y comentario del dueño sobre un servicio finalizado, con una única valoración por solicitud.
  * `incidencias`: Protocolo de registro de emergencias veterinarias, conductas anómalas o extravíos durante el servicio.
* **P2 — Extensión y Post-MVP:**
  * `admin`: Panel administrativo de moderación, auditoría de incidencias y métricas operativas.

---

## 6. Cumplimiento normativo (Ley N° 25.326)

En relación con los contenidos de la asignatura *Legislación* y la Ley N.º 25.326, el diseño contempla limitar la exposición de datos personales. Las búsquedas públicas y los perfiles mostrarán únicamente la provincia y la localidad, sin publicar teléfonos ni domicilios exactos. Los datos de contacto y ubicación necesarios para coordinar el cuidado estarán disponibles para el dueño y el cuidador una vez aceptada la solicitud.

</div>