# Frontend — Cuidando Peluditos

Interfaz HTML/CSS/JavaScript sobre Flask, con plantillas Jinja2 y Bootstrap 5.3.3 incluido localmente. La entrada es `/`; `/demo` conserva acceso a la misma interfaz.

## Organización

- `templates/base.html`: cabecera, pie, mensajes y cuadro de confirmación.
- `templates/inicio.html`: portada, buscador, pasos, servicios y preguntas frecuentes.
- `templates/cuenta.html`: ingreso y registro de dueño/cuidador.
- `templates/mascotas.html`: listado, alta y edición.
- `templates/cuidadores.html`: búsqueda, perfiles y disponibilidad pública.
- `templates/agenda.html`: perfil y disponibilidad del cuidador.
- `templates/solicitudes.html`: creación, estados, acciones e historial.
- `templates/index.html`: reúne las secciones mediante Jinja2.
- `statics/css/base.css`: identidad visual y adaptación a tamaños de pantalla.
- `statics/js/app.js`: navegación por secciones y comunicación con `/api/`.
- `statics/vendor/`: Bootstrap y su licencia.
- `statics/img/README.md`: procedencia y notas de los recursos gráficos.

Flask entrega la plantilla inicial. JavaScript obtiene los datos de la API y envía las operaciones con la cookie de sesión y el encabezado `X-CSRFToken`. El servidor valida permisos, precios y cupos. Ocultar botones por rol es una ayuda de navegación, no un control de seguridad suficiente.

## Ejecutar y probar

Seguir la [guía de ejecución local con MariaDB](../docs/ejecucion-local-mariadb.md).

Resultados documentados:
- [Pruebas manuales iniciales en SQLite](../docs/pruebas-manuales-frontend.md).
- [Integración y concurrencia en MariaDB](../docs/pruebas-mariadb.md).
