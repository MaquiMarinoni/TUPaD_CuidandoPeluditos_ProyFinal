# Backend | Cuidando Peluditos

Este directorio contiene la estructura inicial de los módulos del servidor de **Cuidando Peluditos**. La arquitectura propuesta utiliza una factoría de aplicación (*Application Factory*) y *Blueprints* de Flask para separar las rutas, las reglas de negocio y el acceso a los datos.

## Módulos Funcionales a desarrollar
* `auth/`: Módulo de registro, inicio y cierre de sesión mediante `Flask-Login`, y control de acceso según el rol del usuario (`DUENO`, `CUIDADOR`, `ADMIN`).
* `mascotas/`: Módulo para la gestión y registro de mascotas vinculadas al dueño.
* `cuidadores/`: Módulo para la administración de perfiles de cuidadores, condiciones de convivencia y agenda de disponibilidad.
* `solicitudes/`: Núcleo de la plataforma. Máquina de estados de reservas, cálculo atómico de cupos disponibles y control de concurrencia pesimista (`SELECT ... FOR UPDATE`).
* `valoraciones/`: Módulo de reputación para la emisión de reseñas únicas post-servicio finalizado.
* `incidencias/`: Módulo de registro y trazabilidad de contingencias médicas o de conducta durante el cuidado.