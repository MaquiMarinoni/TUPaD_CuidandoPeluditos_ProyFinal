# Cuidando Peluditos

**Informe final de implementación y validación**  
**Trabajo Final de Carrera — Tecnicatura Universitaria en Programación**  
**Universidad Tecnológica Nacional**

**Grupo:** 176  
**Integrantes:** Macarena Marinoni y Marianela Valletto  
**Tutor:** Oscar Londero  
**Fecha:** 13 de noviembre de 2026

**Aplicación publicada:** https://cuidando-peluditos.onrender.com  
**Repositorio:** https://github.com/MaquiMarinoni/TUPaD_CuidandoPeluditos_ProyFinal

---

## Resumen ejecutivo

Cuidando Peluditos es una aplicación web orientada a vincular a dueños de perros y gatos con personas que ofrecen cuidado temporal mediante visitas a domicilio o alojamiento. El proyecto centraliza perfiles, disponibilidad, solicitudes, seguimiento de estados e información relevante de las mascotas. Su implementación se realizó con Python y Flask, una interfaz web responsiva y persistencia relacional. La versión final fue desplegada en Render con TiDB Cloud, utilizando una conexión cifrada compatible con MySQL.

En la etapa de cierre se verificaron 21 pruebas automatizadas aprobadas y se informaron 12 recorridos funcionales satisfactorios sobre la aplicación publicada, incluidos permisos, cupos, solicitudes, finalización, valoraciones e incidencias. Se comprobó también la conservación de usuarios y mascotas después del reinicio del servicio. El alcance validado corresponde a los roles Dueño y Cuidador; el panel administrativo se mantiene fuera de la versión implementada.

## 1. Problema y fundamentación

La necesidad de cuidado temporal de mascotas suele resolverse mediante redes personales, mensajería y contactos informales. Estas alternativas dificultan conocer de antemano la disponibilidad, las condiciones del cuidado, la experiencia del cuidador y el historial de cada servicio. La propuesta busca organizar esa información y reducir los errores de coordinación.

La investigación UX documentada en la Entrega 01 incluyó cinco entrevistas semiestructuradas, un *card sorting* abierto con diez participantes y cinco pruebas exploratorias de usabilidad. En ese estudio se informó una tasa de completitud del 100 % en las tareas evaluadas y un tiempo medio de recorrido de 54 segundos. Estos resultados corresponden a la fase de investigación previa, no a una medición posterior del sistema desplegado.

## 2. Objetivos y alcance

**Objetivo general:** desarrollar una plataforma web que permita gestionar de forma trazable la contratación de servicios de cuidado de mascotas.

**Objetivos específicos:**

- Registrar usuarios y mascotas.
- Publicar perfiles y disponibilidades de cuidadores.
- Buscar cuidadores mediante filtros.
- Gestionar solicitudes, estados y cupos.
- Registrar incidencias vinculadas a los servicios.
- Permitir valoraciones de servicios finalizados.

**Modalidades de servicio:** visitas al domicilio del dueño y alojamiento en el hogar del cuidador.

**Exclusiones:** pagos reales, videollamadas, geolocalización en tiempo real, verificación automática de identidad y aplicaciones móviles nativas.

## 3. Proceso de desarrollo

La Entrega 01 estableció el problema, la propuesta de solución, el relevamiento UX y el stack previsto. La Entrega 02 formalizó las reglas de negocio, la máquina de estados, el modelo entidad-relación, los módulos priorizados y un escenario de prueba integral.

Posteriormente se implementó el backend Flask y se integró la interfaz de usuario. El desarrollo colaborativo se gestionó mediante ramas de GitHub y una rama de integración, separando las tareas de backend y frontend.

En el cierre se preparó una rama específica para despliegue, `deploy/render`, con dependencias y configuración de producción. No se atribuyen porcentajes de trabajo individuales, ya que no se cuenta con un registro verificable de horas o commits por integrante.

## 4. Arquitectura y tecnologías

| Capa | Implementación |
| --- | --- |
| Interfaz | HTML5, CSS3, JavaScript y Bootstrap 5.3; plantillas y archivos estáticos. |
| Backend | Python 3, Flask 3, patrón *Application Factory* y *Blueprints* por dominio. |
| Persistencia | Flask-SQLAlchemy, Flask-Migrate / Alembic y PyMySQL. |
| Desarrollo y pruebas | MariaDB local, SQLite aislado para pytest, Git, GitHub y VS Code. |
| Producción | Render Web Service, Gunicorn 22 y TiDB Cloud Starter compatible con MySQL mediante TLS. |

La aplicación organiza rutas y modelos por autenticación, mascotas, cuidadores, disponibilidades, solicitudes, visitas, incidencias y valoraciones. La capa de datos utiliza migraciones versionadas. El esquema vigente consta de 11 tablas, incluida `alembic_version`, con revisión Alembic `c0af3fd5552a`.

## 5. Modelo de datos y reglas de negocio

Las entidades principales son usuarios, roles, mascotas, perfiles de cuidadores, disponibilidades, solicitudes, relación entre solicitudes y mascotas, incidencias, valoraciones e historial de estados. El modelo registra relaciones entre dueños, cuidadores y mascotas, y conserva datos históricos asociados a las solicitudes.

Las principales reglas de negocio implementadas son:

- Las mascotas pertenecen a un dueño y sus operaciones deben respetar la identidad del usuario autenticado.
- Los cuidadores publican disponibilidad y capacidad; las solicitudes deben respetar fechas, modalidad y cupos.
- Las solicitudes pueden incluir varias mascotas de un mismo dueño; la evolución de estados queda trazada.
- La aceptación, el rechazo, la cancelación y la finalización aplican reglas de estado y permisos.
- La valoración corresponde al dueño de un servicio finalizado y se limita a una por solicitud.
- Las incidencias registran acontecimientos del servicio y su estado de resolución.

Las migraciones Alembic constituyen el procedimiento vigente para crear el esquema. El archivo `database/schema.sql` se conserva como antecedente histórico y no debe ejecutarse sobre una base con información, ya que puede resultar destructivo.

## 6. Funcionalidades implementadas

| Módulo | Resultado validado |
| --- | --- |
| Autenticación | Registro, inicio y cierre de sesión; sesiones y control de acceso. |
| Mascotas | Alta y consulta de mascotas asociadas al dueño; persistencia tras reinicio. |
| Cuidadores | Perfil, búsqueda y filtros de provincia, localidad, especie y fechas. |
| Disponibilidad | Carga de agenda y control de fechas y cupos. |
| Solicitudes | Creación, aceptación, rechazo, cancelación y liberación de cupos. |
| Finalización | Cierre de servicio e historial de estados. |
| Valoraciones | Calificación posterior a un servicio finalizado; persistencia. |
| Incidencias | Registro, consulta y resolución según permisos. |
| Administrador | Panel administrativo P2 no validado ni incluido como módulo operativo. |

## 7. Despliegue y persistencia

La aplicación está disponible públicamente en *https://cuidando-peluditos.onrender.com*. Render ejecuta Flask mediante Gunicorn. La base relacional se aloja en TiDB Cloud Starter, compatible con el protocolo MySQL, y se accede desde el backend mediante PyMySQL y TLS con verificación de certificado. Las credenciales se administran mediante variables de entorno y no deben incorporarse al repositorio.

El esquema se creó mediante las dos migraciones Alembic disponibles, alcanzando la versión `c0af3fd5552a`. Se verificaron las 11 tablas y los roles iniciales `DUENO`, `CUIDADOR` y `ADMIN`. El servicio web y la base de datos son componentes separados: reiniciar Render no elimina los datos almacenados en TiDB.

La instancia gratuita de Render puede suspenderse por inactividad, por lo que la primera solicitud después de un período sin uso puede demorar. Este comportamiento debe contemplarse en la demostración.

## 8. Pruebas y resultados

Las evidencias corresponden a entornos distintos y se distinguen para evitar atribuir resultados de un motor a otro.

| Entorno | Evidencia | Resultado |
| --- | --- | --- |
| SQLite aislado | Suite `python -m pytest -q` ejecutada en el entorno local. | **21/21 aprobadas**; avisos de APIs deprecadas no bloqueantes. |
| MariaDB local | Pruebas de incidencias, valoraciones, finalización, cancelación, cupos y filtros; documentación y capturas en `docs/`. | Recorridos registrados como satisfactorios, con límites documentados. |
| Render + TiDB | Doce casos funcionales reportados en la aplicación publicada, incluidos permisos, cupos, finalización, valoración, incidencias y diseño responsivo. | **12/12 casos informados como correctos.** |
| Render + TiDB | Reinicio del servicio y nueva consulta de datos. | Usuarios y mascotas conservados; sesión activa tras reinicio. |

### 8.1. Casos funcionales comprobados en producción

1. Intentar acceder a Mis mascotas sin iniciar sesión.
2. Comprobar que un Dueño no pueda modificar mascotas de otro usuario.
3. Comprobar que un Cuidador no pueda aceptar solicitudes destinadas a otro cuidador.
4. Crear una solicitud para una fecha disponible y comprobar que se registre.
5. Intentar reservar una fecha sin disponibilidad y comprobar que el sistema lo impida.
6. Cancelar una solicitud y comprobar que se libere el cupo correspondiente.
7. Crear una solicitud como Dueño y aceptarla como Cuidador.
8. Finalizar el servicio mediante la opción disponible.
9. Registrar una valoración y comprobar que persista después de actualizar la página.
10. Registrar y resolver una incidencia en un servicio que lo permita.
11. Comprobar que los filtros de búsqueda de cuidadores funcionen.
12. Probar las pantallas principales desde un celular o una ventana estrecha.

**Resultado informado:** los doce casos fueron satisfactorios.

## 9. Hallazgos, limitaciones y trabajo futuro

Durante las pruebas de producción se detectó una discrepancia entre el horario de Argentina y las comparaciones de fecha y hora del servidor. Se identificaron comparaciones con `datetime.now()` y `date.today()` y se propuso configurar la variable `TZ=America/Argentina/Buenos_Aires` en Render. La conversación posterior informa aceptación y finalización exitosas, pero no contiene una confirmación explícita de que esos casos se repitieron después de aplicar la variable; por lo tanto, esa verificación queda como punto de cierre.

El panel de administración, considerado extensión P2 en la planificación, no se presenta como funcionalidad terminada. No se realizaron pruebas de carga masiva ni una auditoría de seguridad integral. La aplicación corresponde a un prototipo académico y no incluye procesamiento de pagos reales.

Como mejoras futuras se consideran un módulo administrativo completo, una política explícita de manejo de zonas horarias en toda la aplicación, mayor cobertura de pruebas de permisos y concurrencia en producción, y revisión adicional de accesibilidad y protección de datos personales.

## 10. Conclusiones

El proyecto permitió integrar análisis de requisitos, investigación de usuarios, diseño relacional, desarrollo web, autenticación, reglas de negocio, pruebas y despliegue. El resultado es un sistema accesible públicamente que permite ejecutar el circuito principal de coordinación de cuidados entre Dueño y Cuidador, con persistencia de información en un servicio de base de datos independiente.

Las pruebas automatizadas y manuales aportan evidencia de funcionamiento para los escenarios ejecutados, sin constituir una garantía absoluta de ausencia de defectos. 

## 11. Enlaces y fuentes del proyecto

- **Aplicación:** https://cuidando-peluditos.onrender.com
- **Repositorio:** https://github.com/MaquiMarinoni/TUPaD_CuidandoPeluditos_ProyFinal
- **Documentación de origen:** `docs/Marinoni-Valletto_G176_Entrega01.md` y `docs/Marinoni-Valletto_G176_Entrega02.md`.
- **Validación local:** `docs/validacion-final-2026-11-12.md` y archivos de evidencias vinculados.
- **Guía de ejecución:** `docs/ejecucion-local-mariadb.md` y `database/README.md`.
- **Rama del despliegue:** `deploy/render`; confirmar el commit exacto publicado antes de la entrega.
- **Video de presentación:** enlace pendiente de incorporar cuando esté disponible.

## 12. Lista de control para publicación

- [ ] Confirmar que la configuración horaria de Render fue aplicada y repetir una aceptación con horario futuro.
- [ ] Añadir el PDF final y el enlace del video al repositorio; comprobar permisos desde una sesión sin autenticar.
- [ ] Actualizar el README principal con la URL pública, TiDB, 21 pruebas y limitaciones.
- [ ] Registrar el commit o tag de la versión entregada y comprobar correspondencia con Render.


