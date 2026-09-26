# Cuidando Peluditos — Plataforma de Cuidado y Alojamiento de Mascotas

**Proyecto Final Integrador de Carrera**  
**Carrera:** Tecnicatura Universitaria en Programación a Distancia (TUPaD)  
**Institución:** Universidad Tecnológica Nacional (UTN)  
**Grupo:** 176  
**Integrantes:**
* Macarena Aylen Marinoni ([@MaquiMarinoni](https://github.com/MaquiMarinoni)) - marinonimacarena@gmail.com
* Marianela Paula Valletto ([@maruvalletto](https://github.com/maruvalletto)) - maruvalletto@gmail.com

**Docente Evaluador:** Oscar Londero  

---

## 📌 Descripción del Proyecto

**Cuidando Peluditos** es una solución web integral diseñada para resolver la dificultad de los dueños de perros y gatos para encontrar y coordinar servicios de cuidado confiables (alojamiento en casa del cuidador o visitas a domicilio) ante viajes, compromisos laborales o imprevistos.

La plataforma reduce la asimetría informativa centralizando perfiles transparentes, declaraciones explícitas de convivencia, disponibilidad de agenda en tiempo real, gestión de múltiples mascotas por solicitud, control de concurrencia para evitar sobreventas de cupos, preservación histórica de fichas médicas mediante snapshots, trazabilidad de incidencias y valoraciones verificadas únicamente post-servicio.

---

## 🚀 Estado del Proyecto: 2.ª Entrega — Diseño y Módulos

Esta instancia acredita la **Condición de Regular** en la asignatura, presentando el diseño formal de la base de datos relacional (DER en 3FN), las restricciones de integridad y concurrencia, el listado de módulos funcionales priorizados y la estructura inicial del repositorio (etapa de análisis y diseño arquitectónico).

📄 **Documentación de entregas:**
* [1.ª Entrega — Propuesta de Proyecto y Relevamiento UX](docs/Marinoni-Valletto_G176_Entrega01.md)
* [2.ª Entrega — Diseño, DER y Módulos a Desarrollar](docs/Marinoni-Valletto_G176_Entrega02.md)

---

## 🛠️ Stack Tecnológico Definitivo

| Capa | Tecnologías | Justificación Técnica |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript ES6, Bootstrap 5.3 | Interfaz responsiva tradicional basada en componentes y prototipos UX previamente validados con usuarios. |
| **Backend** | Python 3.10+, Flask 3.x | Arquitectura modular desacoplada mediante *Application Factory* y *Blueprints* organizados por dominio. |
| **Persistencia / ORM** | Flask-SQLAlchemy 3.x, Flask-Migrate (Alembic) | Mapeo objeto-relacional de entidades, control de transacciones ACID y evolución versionada del esquema. |
| **Base de Datos** | MySQL 8.x / MariaDB (InnoDB) | Motor relacional con soporte estricto de integridad referencial, restricciones de unicidad, índices B-Tree y bloqueo pesimista (`SELECT ... FOR UPDATE`). |
| **Seguridad** | Flask-Login, Werkzeug Security | Sesiones de usuario seguras, hashing irreversible de contraseñas y permisos basados en roles (`DUENO`, `CUIDADOR`, `ADMIN`). Cumplimiento de la Ley 25.326 (protección de datos de contacto y domicilios). |
| **Testing** | Pytest | Suite de pruebas unitarias e integración para validación de agenda, solapamientos y condiciones de carrera. |

---

## 📂 Estructura del Repositorio

El repositorio se organiza siguiendo las pautas de arquitectura limpia y los requisitos formales de la cátedra:

```text
TUPaD_CuidandoPeluditos_ProyFinal/
├── backend/                      # Arquitectura del servidor y módulos
│   ├── app/                      # Modelos SQLAlchemy, Blueprints y configuración
│   ├── tests/                    # Pruebas automatizadas con Pytest
│   ├── requirements.txt          # Dependencias fijadas del proyecto
│   ├── run.py                    # Punto de entrada de la aplicación Flask
│   └── README.md                 # Documentación técnica del backend
├── frontend/                     # Capa de presentación (interfaz de usuario)
│   ├── static/                   # Hojas de estilo CSS, JS cliente e imágenes
│   ├── templates/                # Plantillas Jinja2 / HTML organizadas por módulo
│   └── README.md                 # Documentación de la capa frontend
├── database/                     # Definición y persistencia de datos
│   ├── schema.sql                # Script DDL formal (tablas, claves, índices)
│   ├── seeds.sql                 # Script DML con datos iniciales (roles del sistema)
│   └── README.md                 # Documentación del DER e instrucciones de ejecución
├── docs/                         # Informes académicos y documentación formal
│   ├── Marinoni-Valletto_G176_Entrega01.md  # Informe formal de la Entrega 1
│   ├── Marinoni-Valletto_G176_Entrega02.md  # Informe formal de la Entrega 2
│   └── estilos.css                         # Estilos para renderizado a PDF
├── .github/                      # Instrucciones de IA y diagramación Mermaid
├── .vscode/                      # Configuraciones del espacio de trabajo
├── .gitignore                    # Reglas de exclusión de Git (venv, instance, cache)
└── README.md                     # Portada principal del repositorio