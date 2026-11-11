# Frontend base - Cuidando Peluditos

Prototipo de integración construido en `feature/frontend-base` para que Maru continúe con el diseño.

## Ejecutar

1. Iniciar MariaDB y configurar DATABASE_URL como en el backend.
2. Desde la raíz del proyecto: `./.venv/Scripts/python.exe -m flask --app backend.run:app run --host 127.0.0.1 --port 5000 --no-debugger --no-reload`
3. Abrir http://127.0.0.1:5000/demo

El prototipo consume la API sobre el mismo origen, con cookies de sesión y `X-CSRFToken`.
Las pestañas permiten probar registro/login, mascotas, catálogo de cuidadores, perfil/agenda y solicitudes de alojamiento y visita.
No es diseño definitivo; evitar cargar datos personales reales.

Los cambios viven en una rama propia y **no deben fusionarse sobre feature/frontend sin coordinar con Maru**.