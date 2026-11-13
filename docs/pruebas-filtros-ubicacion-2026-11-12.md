# Filtros de búsqueda de cuidadores — 12/11/2026

## Entorno

Ejecución manual: Marianela. Edge, aplicación local en `http://127.0.0.1:5001`, MariaDB 11.4.13 y base `cuidandopeluditos_pruebas`. Rama `integration/tpi-final`, versión publicada `0b7e0a9`. Recorrido realizado desde Encontrar cuidadores con sesión de cuidador.

Se utilizó el catálogo ficticio existente. No se crearon ni modificaron perfiles durante este recorrido. Los conteos corresponden a los datos presentes en esta ejecución y pueden cambiar al agregar o retirar perfiles.

## Resultados

| Caso | Datos ingresados | Resultado observado | Evidencia |
| --- | --- | --- | --- |
| Localidad con coincidencias | Provincia vacía; localidad Rosario | 4 cuidadores encontrados. La primera captura muestra tres perfiles de Rosario y el contador de cuatro. | [Localidad](evidencias/filtros-ubicacion-2026-11-12/01-localidad-rosario.png) |
| Localidad inexistente | Provincia vacía; localidad LocalidadSinResultados | 0 cuidadores y mensaje No encontramos cuidadores. | [Sin resultados](evidencias/filtros-ubicacion-2026-11-12/02-localidad-sin-resultados.png) |
| Limpiar filtros | Acción Limpiar filtros después de la búsqueda sin coincidencias | Campos vacíos y catálogo de 8 cuidadores restablecido. | [Limpieza](evidencias/filtros-ubicacion-2026-11-12/03-limpiar-filtros.png) |
| Provincia con coincidencias | Provincia Santa Fe; localidad vacía | 8 cuidadores, resultado informado durante la ejecución. El conteo por sí solo no demuestra exclusión de otras provincias, porque no se prepararon perfiles de control de otra provincia. | Resultado textual |
| Provincia inexistente | Provincia ProvinciaSinResultados; localidad vacía | 0 cuidadores y mensaje de búsqueda sin coincidencias. | [Provincia](evidencias/filtros-ubicacion-2026-11-12/04-provincia-sin-resultados.png) |
| Combinación con coincidencias | Provincia Santa Fe; localidad Rosario | Cuatro tarjetas, todas de Rosario, Santa Fe. La captura de las tarjetas no incluye los campos; sus valores corresponden al paso ejecutado. | [Cuatro perfiles](evidencias/filtros-ubicacion-2026-11-12/05-resultados-rosario-santa-fe.png) |
| Combinación incompatible | Provincia ProvinciaSinResultados; localidad Rosario | 0 cuidadores aunque Rosario tenga coincidencias sin ese filtro. Se comprueba que la provincia no se ignora al combinar los campos. | [Combinación](evidencias/filtros-ubicacion-2026-11-12/06-combinacion-sin-resultados.png) |

## Especie y fechas desde el buscador de Inicio

Se mantuvo la sesión de cuidador. Las búsquedas se realizaron en modalidad Alojamiento, especie Gato y provincia y localidad vacías.

| Caso | Resultado observado | Evidencia |
| --- | --- | --- |
| Gato sin fechas | Resumen Alojamiento · Gato y 5 cuidadores encontrados; los tres visibles en la captura admiten gatos. Los perfiles ficticios conocidos que solo aceptan perros no aparecen entre esos visibles. No se documenta inspección individual de las cinco tarjetas. | [Especie](evidencias/filtros-ubicacion-2026-11-12/07-gato-sin-fechas.png) |
| Gato del 14 al 16/11/2026 | 1 cuidador encontrado: Cuidador Prueba. | [Fechas cubiertas](evidencias/filtros-ubicacion-2026-11-12/08-gato-fechas-cubiertas.png) |
| Consulta de disponibilidad | El detalle de Cuidador Prueba muestra alojamiento publicado del 14 al 16/11/2026, coincidente con el período buscado. | [Detalle](evidencias/filtros-ubicacion-2026-11-12/09-disponibilidad-publicada.png) |
| Gato del 14 al 17/11/2026 | 0 cuidadores; se excluye Cuidador Prueba porque no cubre el período completo. | [Fuera del período](evidencias/filtros-ubicacion-2026-11-12/10-fechas-fuera-de-disponibilidad.png) |
| Desde 16/11 y hasta 14/11/2026 | El formulario permanece en Inicio y muestra: La salida debe ser posterior al ingreso: al menos una noche. | [Fechas invertidas](evidencias/filtros-ubicacion-2026-11-12/11-fechas-invertidas.png) |

El buscador presenta disponibilidad publicada y advierte que el cupo está sujeto a confirmación. Estos resultados no demuestran plazas libres efectivas ni equivalen a una reserva aceptada; el backend comprueba la capacidad al procesar las solicitudes. No se crearon reservas en este bloque.

## Alcance del registro

Se comprobaron provincia, localidad, su combinación y limpieza, y luego especie Gato con fechas de alojamiento según los casos siguientes. No se verificaron en este recorrido los filtros de visitas ni la revisión de contactos según estado. Tampoco se comprobaron aquí búsquedas parciales, diferencias de mayúsculas, acentos o persistencia de filtros tras recargar.

Se utilizó IA como apoyo para organizar y redactar la documentación de pruebas.
