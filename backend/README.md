# Backend | Cuidando Peluditos

En este directorio se define la estructura modular del servidor para la plataforma **Cuidando Peluditos**, organizada bajo el patrón **Application Factory** y **Blueprints** de Flask, conforme a la arquitectura en capas requerida para la **2.ª Entrega (Etapa de Análisis y Diseño)**.

## Módulos Funcionales a Desarrollar
* `auth/`: Módulo de autenticación, control de sesiones seguras (`Flask-Login`) y roles de usuario (`DUENO`, `CUIDADOR`, `ADMIN`).
* `mascotas/`: Módulo para la gestión y registro de mascotas vinculadas al dueño.
* `cuidadores/`: Módulo para la administración de perfiles de cuidadores, condiciones de convivencia y agenda de disponibilidad.
* `solicitudes/`: Núcleo de la plataforma. Máquina de estados de reservas, cálculo atómico de cupos disponibles y control de concurrencia pesimista (`SELECT ... FOR UPDATE`).
* `valoraciones/`: Módulo de reputación para la emisión de reseñas únicas post-servicio finalizado.
* `incidencias/`: Módulo de registro y trazabilidad de contingencias médicas o de conducta durante el cuidado.

*Nota: La codificación de controladores (`routes.py`), servicios de negocio (`services.py`) y persistencia ORM se incorporará a partir de la siguiente etapa tras la aprobación formal de la 2.ª Entrega.*