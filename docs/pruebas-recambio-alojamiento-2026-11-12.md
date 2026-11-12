# Salida e ingreso el mismo día — 12/11/2026

## Entorno y ejecución

Ejecución: Marianela, mediante `python -m scripts.prueba_recambio_alojamiento`. Flask.test_client con sesiones autenticadas y tokens CSRF, conectado a MariaDB mediante DATABASE_URL. El script comprobó el motor MySQL/MariaDB y la base `cuidandopeluditos_pruebas` antes de crear datos. No es una prueba manual de formularios ni una ejecución con SQLite.

Se crearon usuarios, un cuidador ficticio de capacidad máxima 1, disponibilidad y tres mascotas propias. Las tres solicitudes se crearon PENDIENTES antes de aceptar las reservas.

## Resultado registrado

| Caso | Período | Resultado |
| --- | --- | --- |
| A, solicitud #16 | 12 al 14/12/2026 | Aceptación HTTP 200. |
| B, solicitud #17 | 14 al 16/12/2026 | Aceptación HTTP 200 con A ya aceptada; retiro e ingreso coinciden el 14/12. |
| C, solicitud #18 | 13 al 15/12/2026 | Aceptación impedida, HTTP 409, por superposición real y falta de cupo. |

Cada solicitud contenía una mascota y dos noches a $100 por mascota/noche. Se comprobó el total de $200 para cada caso. Las consultas posteriores confirmaron los estados ACEPTADA, ACEPTADA y PENDIENTE antes de la limpieza.

**Resultado: todas las comprobaciones pasaron.** La fecha de salida no consume una noche de alojamiento. Dos reservas consecutivas no se cuentan como ocupación simultánea, mientras un solapamiento real sí bloquea la aceptación cuando supera la capacidad.

## Estado posterior

Las solicitudes #16, #17 y #18 se cancelaron mediante la API, con HTTP 200 en los tres casos. Permanecen los usuarios, el perfil, la disponibilidad y las mascotas ficticias creadas por el script. Las reservas manuales anteriores no se modificaron.

Este caso valida el límite de retiro e ingreso y un solapamiento efectivo. No sustituye un ensayo de aceptaciones concurrentes ni el caso de capacidad 2 con reservas parcialmente solapadas que no coinciden entre sí; la concurrencia tiene su registro independiente.

## Reproducción

Con DATABASE_URL configurada hacia una base MariaDB terminada en `_pruebas`, ejecutar desde la raíz del repositorio:

```powershell
python -m scripts.prueba_recambio_alojamiento
```

El script genera identificadores propios y fechas relativas a la fecha de ejecución. Utiliza el cliente de pruebas de Flask, por lo que no requiere iniciar otro servidor HTTP.
