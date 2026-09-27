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

**Cuidando Peluditos** es una solución web integral diseñada para resolver la dificultad recurrente que enfrentan los dueños de perros y gatos para coordinar servicios de cuidado confiables (alojamiento en el hogar del cuidador o visitas a domicilio) ante viajes, compromisos laborales o imprevistos familiares.

La plataforma reduce la asimetría informativa centralizando perfiles transparentes, declaraciones explícitas de convivencia, disponibilidad de agenda en tiempo real, gestión de múltiples mascotas por solicitud, control de concurrencia atómico para evitar sobreventas de cupos (*overbooking*), preservación histórica de fichas médicas mediante snapshots inmutables, protocolo de contingencias para imprevistos y valoraciones verificadas únicamente post-servicio finalizado.

---

## 2. Documentación de entregas

El repositorio concentra la totalidad de las instancias formales de evaluación del proyecto de fin de carrera:

* 📑 **[Entrega 01 — Propuesta de Proyecto y relevamiento UX](docs/Marinoni-Valletto_G176_Entrega01.md):** Identificación del problema, propuesta de valor, investigación empírica de campo (5 entrevistas semiestructuradas, card sorting con 10 participantes y pruebas de usabilidad con 54 segundos promedio de recorrido).
* 📐 **[Entrega 02 — Diseño, DER y módulos a desarrollar](docs/Marinoni-Valletto_G176_Entrega02.md):** Marco curricular de TUPaD, reglas del dominio central en P0, máquina de estados, control transaccional de concurrencia (`with_for_update()`), esquema relacional en 3FN con diccionario de datos, listado de módulos priorizados (P0/P1/P2) y modelado del escenario de prueba integral.
* 🗄️ **[Directorio de Base de Datos](database/):** Scripts DDL (`schema.sql`) y DML (`seeds.sql`) en MySQL InnoDB y documentación del DER en Mermaid.

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
│   ├── static/                   # Hojas de estilo CSS, JS cliente e imágenes
│   ├── templates/                # Plantillas Jinja2 / HTML organizadas por módulo
│   └── README.md                 # Documentación técnica de la capa frontend
├── database/                     # Definición y persistencia de datos relacional
│   ├── schema.sql                # Script DDL formal
│   ├── seeds.sql                 # Script DML con roles iniciales del sistema
│   └── README.md                 # Documentación del DER 
├── docs/                         # Informes
│   ├── Marinoni-Valletto_G176_Entrega01.md  # Informe entrega 01
│   ├── Marinoni-Valletto_G176_Entrega02.md  # Informe entrega 02
│   └── estilos.css                         # Estilos para renderizado y exportación a PDF
├── .github/                      # Pautas de diagramas Mermaid
├── .vscode/                      # Configuraciones de workspace
├── .gitignore                    # Reglas de exclusión de Git
└── README.md                     # Portada del repositorio
```

---

## 5. Módulos funcionales y priorización

El sistema estructura sus componentes bajo el estándar ágil de priorización (P0 = MVP Crítico, P1 = Necesario, P2 = Extensión):

* **P0 — Núcleo del MVP:**
  * `auth`: Registro, login y roles diferenciados (`DUENO`, `CUIDADOR`, `ADMIN`).
  * `mascotas`: ABM de perros y gatos asociados al dueño y sus cuidados especiales.
  * `cuidadores`: Perfil público, tarifas, condiciones declaradas de convivencia y calendario de disponibilidad.
  * `solicitudes`: Ciclo de vida de reservas multi-mascota, snapshot inmutable de datos clínicos y control de concurrencia atómico para evitar sobrecupos.
* **P1 — Complementarios Obligatorios:**
  * `valoraciones`: Calificación unidireccional (1 a 5 estrellas) con reseña, habilitada exclusivamente tras el estado `FINALIZADA` (`UNIQUE`).
  * `incidencias`: Protocolo de registro de emergencias veterinarias, conductas anómalas o extravíos durante el servicio.
* **P2 — Extensión y Post-MVP:**
  * `admin`: Panel administrativo de moderación, auditoría de incidencias y métricas operativas.

---

## 6. Cumplimiento normativo (Ley N° 25.326)

En concordancia con los contenidos de la asignatura *Legislación*, la plataforma implementa el principio de minimización y finalidad en el tratamiento de datos personales. Durante las búsquedas públicas y consultas de perfiles, no se divulgan números de teléfono ni domicilios exactos de dueños o cuidadores (restringiéndose a provincia y localidad general). Los datos de contacto directos se revelan única y exclusivamente a ambas partes cuando una solicitud ha sido formalmente aceptada por el cuidador.

</div>