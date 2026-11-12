# Ejecución local con MariaDB en Windows

Entorno probado: Python 3.13, MariaDB 11.4.13 con tablas InnoDB y dependencias de `backend/requirements.txt`. Ejecutar los comandos PowerShell desde la raíz del repositorio, con el servicio MariaDB iniciado.

## 1. Dependencias

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

## 2. Base y cuenta de desarrollo

Si la base y la cuenta aún no existen, abrir el cliente como administrador:

```powershell
& "C:\Program Files\MariaDB 11.4\bin\mariadb.exe" -u root -p
```

Dentro del cliente, ejecutar este SQL reemplazando `CLAVE_ELEGIDA_LOCALMENTE` por una contraseña propia:

```sql
CREATE DATABASE cuidandopeluditos_pruebas
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'peluditos_app'@'127.0.0.1'
  IDENTIFIED BY 'CLAVE_ELEGIDA_LOCALMENTE';
GRANT ALL PRIVILEGES ON cuidandopeluditos_pruebas.*
  TO 'peluditos_app'@'127.0.0.1';
EXIT;
```

Los permisos se limitan a la base local de desarrollo e incluyen las operaciones de las migraciones.

## 3. Conexión y migraciones

Configurar la conexión en la terminal donde se iniciará Flask. La contraseña se solicita sin mostrarla y no se guarda en archivos:

```powershell
$clavePeluditos = Read-Host "Contraseña de peluditos_app" -AsSecureString
$claveCodificada = [Uri]::EscapeDataString([System.Net.NetworkCredential]::new('', $clavePeluditos).Password)
$env:DATABASE_URL = "mysql+pymysql://peluditos_app:${claveCodificada}@127.0.0.1:3306/cuidandopeluditos_pruebas?charset=utf8mb4"
$env:FLASK_ENV = "dev"
Remove-Variable clavePeluditos, claveCodificada
```

La variable `DATABASE_URL` dura hasta cerrar esa terminal. Aplicar las migraciones y comprobar el esquema:

```powershell
.\.venv\Scripts\python.exe -m flask --app backend.run:app db upgrade --directory backend/migrations
.\.venv\Scripts\python.exe -m flask --app backend.run:app db current --directory backend/migrations
.\.venv\Scripts\python.exe -m flask --app backend.run:app db check --directory backend/migrations
```

Cargar los roles iniciales:

```powershell
& "C:\Program Files\MariaDB 11.4\bin\mariadb.exe" -h 127.0.0.1 -u peluditos_app -p cuidandopeluditos_pruebas -e "INSERT IGNORE INTO roles (nombre) VALUES ('DUENO'), ('CUIDADOR'), ('ADMIN'); SELECT id, nombre FROM roles;"
```

No usar `database/schema.sql` sobre una base con datos: elimina las tablas. El arranque de esta versión utiliza las migraciones del proyecto.

## 4. Iniciar Flask

```powershell
.\.venv\Scripts\python.exe -m flask --app backend.run:app run --host 127.0.0.1 --port 5001 --no-debugger --no-reload
```

Abrir [Cuidando Peluditos](http://127.0.0.1:5001/). Mantener la terminal abierta; Ctrl+C detiene el servidor. Al volver a iniciar, configurar nuevamente la conexión. Los datos permanecen en MariaDB.

## 5. Pruebas

Con Flask en ejecución, usar otra terminal y ejecutar los scripts sobre la base local de prueba:

```powershell
$env:PELUDITOS_TEST_URL = "http://127.0.0.1:5001"
.\.venv\Scripts\python.exe -m scripts.prueba_integridad_reservas
.\.venv\Scripts\python.exe -m scripts.prueba_concurrencia_visitas
.\.venv\Scripts\python.exe -m scripts.prueba_visitas
& .\scripts\prueba_seguridad_mascotas.ps1
& .\scripts\prueba_solicitudes.ps1
.\.venv\Scripts\python.exe -m scripts.prueba_ciclo_y_snapshots
```

Los scripts generan datos ficticios; algunos dejan reservas de prueba aceptadas. La prueba de finalización válida utiliza una base SQLite en memoria independiente:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_finalizacion.py -q
```

Resultados y alcance: [pruebas de MariaDB](pruebas-mariadb.md). El caso aislado de SQLite no sustituye la validación de finalización positiva en MariaDB.
