
$ErrorActionPreference = "Stop"
$base = if ($env:PELUDITOS_TEST_URL) { $env:PELUDITOS_TEST_URL.TrimEnd("/") } else { "http://127.0.0.1:5000" }

function Crear-Sesion {
    $sesion = New-Object Microsoft.PowerShell.Commands.WebRequestSession
    $respuesta = Invoke-RestMethod `
        -Uri "$base/api/auth/csrf-token" `
        -WebSession $sesion

    return @{
        Cookies = $sesion
        Headers = @{
            "X-CSRFToken" = $respuesta.csrf_token
        }
    }
}

function Enviar-Json($metodo, $ruta, $datos, $sesion) {
    $json = $datos | ConvertTo-Json -Depth 5

    return Invoke-RestMethod `
        -Uri "$base$ruta" `
        -Method $metodo `
        -WebSession $sesion.Cookies `
        -Headers $sesion.Headers `
        -ContentType "application/json" `
        -Body $json
}

function Obtener-CodigoError($script) {
    try {
        & $script | Out-Null
        return 200
    }
    catch {
        if ($_.Exception.Response) {
            return [int]$_.Exception.Response.StatusCode
        }
        throw
    }
}

function Comprobar($nombre, $obtenido, $esperado) {
    if ($obtenido -eq $esperado) {
        Write-Host "OK - $nombre ($obtenido)" -ForegroundColor Green
    }
    else {
        Write-Host "ERROR - $nombre. Esperado: $esperado. Obtenido: $obtenido" `
            -ForegroundColor Red
        $script:fallas++
    }
}

$fallas = 0

# Usuarios ficticios distintos en cada ejecucion.
$identificador = [guid]::NewGuid().ToString("N").Substring(0, 10)
$password = "PruebaSegura2026!"

$sesionAnonima = Crear-Sesion

$codigo = Obtener-CodigoError {
    Invoke-RestMethod `
        -Uri "$base/api/mascotas" `
        -WebSession $sesionAnonima.Cookies
}

Comprobar "Sin iniciar sesion" $codigo 401

# Registrar dos duenios y un cuidador.
$usuarios = @(
    @{ nombre = "Ana"; rol = "DUENO" },
    @{ nombre = "Beto"; rol = "DUENO" },
    @{ nombre = "Carla"; rol = "CUIDADOR" }
)

$sesiones = @()

foreach ($usuario in $usuarios) {
    $sesion = Crear-Sesion
    $email = "$($usuario.nombre.ToLower()).$identificador@peluditos.example"

    $registro = @{
        nombre = $usuario.nombre
        apellido = "Seguridad"
        email = $email
        password = $password
        telefono = "3420000000"
        provincia = "Santa Fe"
        localidad = "Santa Fe"
        rol = $usuario.rol
    }

    Enviar-Json "Post" "/api/auth/register" $registro $sesion | Out-Null

    Enviar-Json "Post" "/api/auth/login" @{
        email = $email
        password = $password
    } $sesion | Out-Null

    $sesiones += $sesion
}

$duenoA = $sesiones[0]
$duenoB = $sesiones[1]
$cuidador = $sesiones[2]

# Crear una mascota del primer duenio.
$mascota = Enviar-Json "Post" "/api/mascotas" @{
    nombre = "Mascota Seguridad"
    especie = "PERRO"
    tamano = "CHICO"
} $duenoA

$idMascota = $mascota.mascota.id

Comprobar "Mascota creada" $([int]($idMascota -gt 0)) 1

# Otro duenio no puede consultar la mascota.
$codigo = Obtener-CodigoError {
    Invoke-RestMethod `
        -Uri "$base/api/mascotas/$idMascota" `
        -WebSession $duenoB.Cookies
}

Comprobar "Lectura de mascota ajena" $codigo 404

# Otro duenio no puede editar la mascota.
$codigo = Obtener-CodigoError {
    Enviar-Json "Put" "/api/mascotas/$idMascota" @{
        nombre = "Nombre Intruso"
    } $duenoB
}

Comprobar "Edicion de mascota ajena" $codigo 404

# Otro duenio no puede eliminar la mascota.
$codigo = Obtener-CodigoError {
    Invoke-RestMethod `
        -Uri "$base/api/mascotas/$idMascota" `
        -Method Delete `
        -WebSession $duenoB.Cookies `
        -Headers $duenoB.Headers
}

Comprobar "Eliminacion de mascota ajena" $codigo 404

# Un cuidador no puede crear mascotas.
$codigo = Obtener-CodigoError {
    Enviar-Json "Post" "/api/mascotas" @{
        nombre = "No Permitida"
        especie = "GATO"
        tamano = "CHICO"
    } $cuidador
}

Comprobar "Cuidador sin permiso de mascotas" $codigo 403

# Rechazar especies incorrectas.
$codigo = Obtener-CodigoError {
    Enviar-Json "Post" "/api/mascotas" @{
        nombre = "Mascota Incorrecta"
        especie = "CABALLO"
        tamano = "MEDIANO"
    } $duenoA
}

Comprobar "Validacion de especie" $codigo 400

# El propietario se obtiene de la sesion.
$codigo = Obtener-CodigoError {
    Enviar-Json "Post" "/api/mascotas" @{
        nombre = "Cambio de Duenio"
        especie = "PERRO"
        tamano = "CHICO"
        dueno_id = 999
    } $duenoA
}

Comprobar "Bloqueo de dueno_id" $codigo 400


# Probar CSRF con una sesion nueva que conserva
# solamente la cookie de autenticacion.

$sinToken = New-Object Microsoft.PowerShell.Commands.WebRequestSession

$cookieSesion = $duenoA.Cookies.Cookies.GetCookies(
    [uri]$base
) | Where-Object { $_.Name -eq "session" } |
Select-Object -First 1

if ($null -eq $cookieSesion) {
    throw "No se encontro la cookie de sesion."
}

$sinToken.Cookies.Add([uri]$base, $cookieSesion)

# Intentamos editar una mascota existente sin enviar
# el encabezado X-CSRFToken.

$codigo = Obtener-CodigoError {
    Invoke-RestMethod `
        -Uri "$base/api/mascotas/$idMascota" `
        -Method Put `
        -WebSession $sinToken `
        -ContentType "application/json" `
        -Body '{"nombre":"Cambio sin CSRF"}' `
        -ErrorAction Stop
}

Comprobar "Proteccion CSRF" $codigo 400


# Eliminar logicamente la mascota con su propietario.
Invoke-RestMethod `
    -Uri "$base/api/mascotas/$idMascota" `
    -Method Delete `
    -WebSession $duenoA.Cookies `
    -Headers $duenoA.Headers | Out-Null

$codigo = Obtener-CodigoError {
    Invoke-RestMethod `
        -Uri "$base/api/mascotas/$idMascota" `
        -WebSession $duenoA.Cookies
}

Comprobar "Mascota desactivada no accesible" $codigo 404

Write-Host ""
if ($fallas -eq 0) {
    Write-Host "RESULTADO: TODAS LAS PRUEBAS PASARON" -ForegroundColor Green
}
else {
    Write-Host "RESULTADO: $fallas PRUEBAS FALLARON" -ForegroundColor Red
    exit 1
}
