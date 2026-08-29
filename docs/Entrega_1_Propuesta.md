<div align="center">
<h1>UNIVERSIDAD TECNOLÓGICA NACIONAL</h1>
<h2>Entrega 1 - Propuesta de Proyecto y Repositorio</h2>
<p><strong>Valletto, Marianela y Marinoni, Macarena</strong></p>
<p>Tecnicatura Universitaria en Programación - Universidad Tecnológica Nacional</p>
<p>Trabajo Final de Carrera</p>
<p>2026</p>
</div>

<br>

## ÍNDICE
- [ÍNDICE](#índice)
- [Parte 1: Identificación del problema y propuesta de solución](#parte-1-identificación-del-problema-y-propuesta-de-solución)
  - [1. Contexto y problema central](#1-contexto-y-problema-central)
  - [2. Actores involucrados](#2-actores-involucrados)
  - [3. Propuesta de solución y valor agregado](#3-propuesta-de-solución-y-valor-agregado)
  - [4. Validación e investigación previa](#4-validación-e-investigación-previa)
  - [5. Indicadores para medir el impacto](#5-indicadores-para-medir-el-impacto)
  - [6. Análisis competitivo y diferenciación](#6-análisis-competitivo-y-diferenciación)
- [Parte 2: Definición del stack tecnológico](#parte-2-definición-del-stack-tecnológico)
  - [1. Tecnologías seleccionadas](#1-tecnologías-seleccionadas)
  - [2. Justificación de la elección](#2-justificación-de-la-elección)
  - [3. Arquitectura propuesta y escalabilidad](#3-arquitectura-propuesta-y-escalabilidad)
  - [4. Riesgos técnicos y mitigaciones](#4-riesgos-técnicos-y-mitigaciones)
- [Parte 3: Plan de trabajo y alcance](#parte-3-plan-de-trabajo-y-alcance)
  - [1. Alcance del producto (MVP)](#1-alcance-del-producto-mvp)
  - [2. Exclusiones funcionales](#2-exclusiones-funcionales)
  - [3. Reglas de negocio principales](#3-reglas-de-negocio-principales)
  - [4. Criterios de éxito y evidencia mínima](#4-criterios-de-éxito-y-evidencia-mínima)
  - [5. Plan de trabajo preliminar](#5-plan-de-trabajo-preliminar)
- [Parte 4: Repositorio del Proyecto](#parte-4-repositorio-del-proyecto)

<div style="font-family: 'Calibri', sans-serif; font-size: 12pt; line-height: 1.5; text-align: justify;">


## Parte 1: Identificación del problema y propuesta de solución

**Resumen:** Se define la problemática central vinculada a la coordinación del cuidado temporal de mascotas, identificando a los actores involucrados, las limitaciones de las herramientas actuales y el valor agregado de la solución tecnológica propuesta.

### 1. Contexto y problema central
Los dueños de perros y gatos en Argentina enfrentan dificultades significativas para encontrar y seleccionar cuidadores temporales adecuados. Actualmente, esta necesidad suele resolverse mediante alternativas informales, como familiares, grupos de redes sociales, mensajería o veterinarias, las cuales funcionan de manera aislada y no están diseñadas para una gestión integral. Ademas, estas alternativas pueden resolver necesidades puntuales, pero no siempre permiten conocer previamente la experiencia, disponibilidad, ubicación, servicios ofrecidos o reputación de la persona que realizará el cuidado.


### 2. Actores involucrados
Para comprender el ecosistema del sistema, se identifican los siguientes actores principales:
*   **Dueños de mascotas:** Personas responsables de perros o gatos que necesitan contratar temporalmente un servicio de cuidado. Requieren encontrar cuidadores disponibles, informar las necesidades particulares de sus mascotas, comparar alternativas y realizar el seguimiento del servicio solicitado.
*   **Cuidadores:** Personas que ofrecen servicios de cuidado mediante visitas al domicilio del dueño o alojamiento temporal en el domicilio del cuidador. Necesitan presentar su experiencia, servicios y disponibilidad; recibir solicitudes completas; aceptarlas o rechazarlas; y construir una reputación a partir de valoraciones.
*   **Mascotas:** Aunque no utilizan directamente la plataforma, los perros y gatos son los principales beneficiarios. Su bienestar depende de que el cuidador conozca sus rutinas, alimentación, comportamiento, medicación y cuidados especiales.
*   **Administradores:** Personas responsables de supervisar el funcionamiento de la plataforma. Podrán consultar usuarios y operaciones, activar o desactivar cuentas, moderar contenido y valoraciones, gestionar denuncias o incidencias y visualizar indicadores básicos. Sus acciones deberán respetar permisos definidos y quedar registradas cuando impliquen una intervención sobre información del sistema.

### 3. Propuesta de solución y valor agregado
La solución consiste en desarrollar "Cuidando Peluditos", una plataforma web que conecte a dueños con cuidadores, superando la simple digitalización de un directorio. El valor agregado de la propuesta radica en:
*   Centralizar los perfiles y relacionar las necesidades específicas de la mascota con los servicios ofrecidos.
*   Permitir la consulta de disponibilidad antes de generar una solicitud formal.
*   Registrar el historial de servicios y gestionar los estados de cada solicitud para reducir errores de coordinación.
*   Facilitar la toma de decisiones mediante valoraciones vinculadas exclusivamente a servicios finalizados.

### 4. Validación e investigación previa
La viabilidad y relevancia de la problemática se apoyan en una investigación de Experiencia de Usuario (UX) realizada en etapas previas. Esta validación exploratoria incluyó:
*   **Entrevistas semiestructuradas:** Realizadas a usuarios del público objetivo, confirmando la dificultad para hallar cuidadores de confianza y el estrés asociado a la alteración de las rutinas de la mascota.
*   **Card sorting y pruebas de usabilidad:** Ejecutadas con participantes reales, logrando que el flujo diseñado sea completado exitosamente en tiempos óptimos, lo que respalda la comprensión del problema y la utilidad de la interfaz propuesta.

### 5. Indicadores para medir el impacto
Para evaluar objetivamente la efectividad del Producto Mínimo Viable (MVP) y la mitigación del problema central, se definen los siguientes indicadores de éxito:
*   Tiempo promedio necesario para encontrar un cuidador disponible.
*   Cantidad de solicitudes sin respuesta, rechazadas o canceladas.
*   Porcentaje de usuarios que logra completar exitosamente el flujo de búsqueda y solicitud.
*   Percepción de confianza y facilidad de uso, medida a través de encuestas posteriores a las pruebas.

### 6. Análisis competitivo y diferenciación
El relevamiento del mercado actual identifica plataformas como Mascoters, TrustedHousesitters y PetBacker, las cuales presentan limitaciones vinculadas al idioma, suscripciones pagas, procesos extensos o interfaces sobrecargadas. "Cuidando Peluditos" se diferenciará estratégicamente ofreciendo:
*   Una experiencia adaptada íntegramente a usuarios, provincias y localidades de Argentina.
*   Modalidades de cuidado claramente identificadas (domicilio del dueño o alojamiento del cuidador).
*   Un flujo de contratación simplificado y trazabilidad absoluta sobre los estados de las solicitudes.

## Parte 2: Definición del stack tecnológico

**Resumen:** Se detallan y justifican las herramientas, lenguajes y frameworks seleccionados para el desarrollo del producto mínimo viable (MVP), incluyendo el diseño arquitectónico y el análisis de riesgos técnicos asociados.

### 1. Tecnologías seleccionadas
El proyecto se construirá sobre un conjunto de tecnologías orientadas a garantizar la viabilidad dentro del calendario académico, organizadas en las siguientes capas:
*   **Frontend:** HTML5, CSS3, JavaScript y Bootstrap 5. Se encargarán de las interfaces responsivas, formularios y validaciones del lado del cliente.
*   **Backend:** Python 3 y Flask. Gestionarán las reglas de negocio, rutas, autenticación y procesamiento de solicitudes.
*   **Base de datos y persistencia:** MySQL como motor relacional, complementado con Flask-SQLAlchemy para el acceso a datos y Flask-Migrate para el control de cambios del esquema.
*   **Seguridad y pruebas:** Autenticación y control de accesos mediante Flask-Login y Werkzeug, integrando Pytest para la ejecución de pruebas automatizadas sobre flujos principales.
*   **Despliegue y versionado:** Git y GitHub para el trabajo colaborativo, con un despliegue inicial planificado en el entorno de PythonAnywhere.

### 2. Justificación de la elección
La selección del stack equilibra el conocimiento previo del equipo, los tiempos de desarrollo y la seguridad. Al tratarse de un desarrollo académico, se priorizan tecnologías maduras y con documentación abundante, lo que disminuye el costo de aprendizaje frente a alternativas como Django o React. A nivel de datos, el uso de MySQL resulta apropiado ya que el dominio presenta relaciones claras y estructuradas (usuarios, mascotas, solicitudes) que requieren integridad referencial y manejo de transacciones.

### 3. Arquitectura propuesta y escalabilidad
Se utilizará una arquitectura de aplicación web modular con renderizado mediante plantillas desde el servidor. La estructura separará lógicamente la presentación, las rutas, los servicios y los modelos, organizando el sistema en módulos específicos (autenticación, mascotas, cuidadores, disponibilidad, solicitudes, valoraciones e incidencias). 

Esta arquitectura es adecuada para el alcance inicial y permite una correcta escalabilidad para una cantidad moderada de usuarios. Se descarta inicialmente una arquitectura de microservicios, ya que aumentaría la complejidad operativa, de pruebas y de despliegue sin aportar un beneficio proporcional al MVP propuesto.

### 4. Riesgos técnicos y mitigaciones
Para asegurar la integridad del desarrollo, se identificaron riesgos técnicos y sus correspondientes acciones de mitigación:
*   **Errores de autorización (acceso indebido):** Se mitigará implementando una matriz de permisos estricta y pruebas específicas para cada rol.
*   **Exposición de credenciales:** Se evitará subiendo secretos al control de versiones, utilizando archivos de variables de entorno locales y rotando credenciales.
*   **Limitaciones del entorno de despliegue:** Se realizará una prueba temprana de despliegue en PythonAnywhere para validar la capacidad de almacenamiento y compatibilidad.

## Parte 3: Plan de trabajo y alcance

**Resumen:** Se establecen los límites funcionales de la primera versión del sistema, diferenciando los módulos indispensables de aquellos excluidos, y se definen las reglas de negocio, criterios de éxito y el cronograma de ejecución.

### 1. Alcance del producto (MVP)
La primera versión del sistema contempla el desarrollo de los módulos esenciales para validar el flujo principal de coordinación de cuidados. Las funcionalidades obligatorias incluyen:
*   **Autenticación y roles:** Registro, inicio y cierre de sesión con accesos diferenciados para dueños, cuidadores y administradores.
*   **Gestión de entidades:** Alta, consulta, modificación y baja lógica de mascotas, junto con la configuración de perfiles y servicios de cuidadores.
*   **Operatoria principal:** Registro de disponibilidad, motor de búsqueda con filtros básicos, creación de solicitudes y seguimiento mediante transiciones de estado (pendiente, aceptada, rechazada, cancelada, en curso y finalizada).
*   **Interacciones adicionales:** Sistema de valoraciones aplicable únicamente a servicios finalizados y un módulo de incidencias para la moderación administrativa.

### 2. Exclusiones funcionales
Para garantizar la viabilidad del proyecto dentro de los plazos académicos, se excluyen explícitamente de esta iteración: el procesamiento de pagos reales, sistemas de videollamadas, seguimiento por geolocalización en tiempo real, verificación automática de identidad y el desarrollo de aplicaciones móviles nativas.

### 3. Reglas de negocio principales
El comportamiento del sistema estará regido por normativas estrictas de validación y permisos:
*   Un usuario dueño únicamente podrá modificar los datos de sus propias mascotas y solicitudes.
*   Un usuario cuidador solo podrá aceptar solicitudes que coincidan con su disponibilidad registrada, advirtiendo o bloqueando superposiciones.
*   Las valoraciones solo podrán ser emitidas por el dueño asociado al servicio, una única vez y exclusivamente cuando el servicio se encuentre finalizado.
*   Toda acción administrativa de moderación o eliminación lógica deberá registrar el motivo, la fecha y el responsable para asegurar la trazabilidad.

### 4. Criterios de éxito y evidencia mínima
La aceptación del Producto Mínimo Viable (MVP) estará sujeta al cumplimiento de los siguientes indicadores funcionales:
*   Al menos el 80 % de los usuarios de prueba logra completar el flujo principal sin asistencia crítica.
*   El 100 % de las operaciones sensibles respeta las restricciones de la matriz de autorización por roles.
*   Las solicitudes de cuidado recorren únicamente las transiciones de estado permitidas por el sistema.
*   El código fuente se encuentra desplegado y puede ser demostrado exitosamente con datos de prueba.

### 5. Plan de trabajo preliminar
La ejecución del proyecto se estructurará de forma iterativa a lo largo de un estimado de 10 semanas, comenzando con la definición arquitectónica y modelo de datos (semanas 1 a 3), seguido por la implementación de usuarios y perfiles (semanas 4 a 6), desarrollo del motor de búsqueda y solicitudes (semanas 7 a 8), para concluir con las pruebas integrales, ajustes de seguridad y despliegue final (semanas 9 a 10).

## Parte 4: Repositorio del Proyecto

**Resumen:** Enlace al repositorio único centralizado donde se alojará el código fuente, la documentación técnica y el control de versiones colaborativo de todo el proyecto.

* **URL del Repositorio:** [Cuidando Peluditos](https://github.com/MaquiMarinoni/TUPaD_CuidandoPeluditos_ProyFinal.git)

<div>