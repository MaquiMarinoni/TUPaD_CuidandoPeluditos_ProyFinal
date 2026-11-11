
$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:5000"
$fallas = 0

function Peticion($metodo, $ruta, $sesion, $headers, $datos = $null) {
    $parametros = @{
        Uri = "$base$ruta"
        Method = $metodo
        WebSession = $sesion
        UseBasicParsing = $true
        ErrorAction = "Stop"
    }

    if ($null -ne $headers) {
        $parametros.Headers = $headers
    }

    if ($null -ne $datos) {
        $parametros.ContentType = "application/json"
        $parametros.Body = $datos | ConvertTo-Json -Depth 8
    }

    try {
        $respuesta = Invoke-WebRequest @parametros
        return @{
            codigo = [int]$respuesta.StatusCode
            datos = $respuesta.Content | ConvertFrom-Json
        }
    }
    catch {
        if ($null -eq $_.Exception.Response) {
            throw
        }

        return @{
            codigo = [int]$_.Exception.Response.StatusCode
            datos = $null
        }
    }
}

function Verificar($nombre, $obtenido, $esperado) {
    if ($obtenido -eq $esperado) {
        Write-Host "OK - $nombre ($obtenido)" -ForegroundColor Green
    }
    else {
        Write-Host "ERROR - ${nombre}: esperado ${esperado}, recibido ${obtenido}" `
            -ForegroundColor Red
        $script:fallas++
    }
}

function Crear-Usuario($nombre, $rol, $identificador) {
    $sesion = New-Object Microsoft.PowerShell.Commands.WebRequestSession

    $csrf = Peticion "GET" "/api/auth/csrf-token" $sesion $null
    $headers = @{
        "X-CSRFToken" = $csrf.datos.csrf_token
    }

    $email = "$($nombre.ToLower()).$identificador@peluditos.example"

    $registro = @{
        nombre = $nombre
        apellido = "Reservas"
        email = $email
        password = "PruebaLocal2026!"
        telefono = "3420000000"
        provincia = "Santa Fe"
        localidad = "Santa Fe"
        rol = $rol
    }

    $r = Peticion "POST" "/api/auth/register" $sesion $headers $registro
    Verificar "Registro $nombre" $r.codigo 201

    $r = Peticion "POST" "/api/auth/login" $sesion $headers @{
        email = $email
        password = "PruebaLocal2026!"
    }

    Verificar "Login $nombre" $r.codigo 200

    return @{
        sesion = $sesion
        headers = $headers
    }
}

$identificador = [guid]::NewGuid().ToString("N").Substring(0, 10)

$dueno1 = Crear-Usuario "Ana" "DUENO" $identificador
$dueno2 = Crear-Usuario "Beto" "DUENO" $identificador
$cuidador = Crear-Usuario "Carlos" "CUIDADOR" $identificador

# Crear perfil con capacidad maxima de 2 mascotas.
$r = Peticion "POST" "/api/cuidadores/mi-perfil" `
    $cuidador.sesion $cuidador.headers @{
        descripcion = "Perfil para probar reservas."
        capacidad_maxima = 2
        admite_perros = $true
        admite_gatos = $true
        tarifa_diaria = "100.00"
        tarifa_visita = "50.00"
    }

Verificar "Perfil cuidador" $r.codigo 201
$idCuidador = $r.datos.cuidador.id

# Fechas futuras dinamicas para poder repetir la prueba.
$inicio = (Get-Date).Date.AddDays(20)
$salida = $inicio.AddDays(3)

$desde = $inicio.ToString("yyyy-MM-dd")
$hasta = $salida.ToString("yyyy-MM-dd")

$r = Peticion "POST" "/api/disponibilidades" `
    $cuidador.sesion $cuidador.headers @{
        modalidad = "ALOJAMIENTO"
        fecha_desde = $desde
        fecha_hasta = $hasta
    }

Verificar "Disponibilidad del cuidador" $r.codigo 201

# Crear dos mascotas de Ana y una de Beto.
$idsAna = @()

foreach ($nombre in @("Luna", "Toby")) {
    $r = Peticion "POST" "/api/mascotas" `
        $dueno1.sesion $dueno1.headers @{
            nombre = $nombre
            especie = "PERRO"
            tamano = "MEDIANO"
            cuidados_especiales = "Sin indicaciones especiales."
        }

    Verificar "Mascota $nombre" $r.codigo 201
    $idsAna += [int]$r.datos.mascota.id
}

$r = Peticion "POST" "/api/mascotas" `
    $dueno2.sesion $dueno2.headers @{
        nombre = "Michi"
        especie = "GATO"
        tamano = "CHICO"
    }

Verificar "Mascota Michi" $r.codigo 201
$idMichi = [int]$r.datos.mascota.id

function Datos-Solicitud($ids) {
    return @{
        cuidador_id = [int]$idCuidador
        modalidad = "ALOJAMIENTO"
        fecha_desde = $desde
        fecha_hasta = $hasta
        mascotas_ids = @($ids)
        contacto_emergencia = "Contacto de prueba"
        veterinario_emergencia = "Veterinaria de prueba"
        autorizacion_urgencia = $true
        limite_gastos_urgencia = "5000.00"
    }
}

# Ana solicita alojamiento para dos mascotas.
$r = Peticion "POST" "/api/solicitudes" `
    $dueno1.sesion $dueno1.headers (Datos-Solicitud $idsAna)

Verificar "Solicitud de dos mascotas" $r.codigo 201

$idSolicitud1 = [int]$r.datos.solicitud.id

Verificar "Total mascotas calculado" `
    $r.datos.solicitud.total_mascotas 2

Verificar "Importe calculado por backend" `
    ([decimal]$r.datos.solicitud.monto_total) ([decimal]600)

Verificar "Estado inicial" `
    $r.datos.solicitud.estado "PENDIENTE"

# Beto solicita las mismas noches para una mascota.
$r = Peticion "POST" "/api/solicitudes" `
    $dueno2.sesion $dueno2.headers (Datos-Solicitud @($idMichi))

Verificar "Segunda solicitud pendiente" $r.codigo 201
$idSolicitud2 = [int]$r.datos.solicitud.id

# Solo el cuidador puede aceptar solicitudes.
$r = Peticion "POST" "/api/solicitudes/$idSolicitud1/aceptar" `
    $dueno1.sesion $dueno1.headers

Verificar "Dueño no puede aceptar" $r.codigo 409

# Carlos acepta la primera reserva: ocupa 2 plazas.
$r = Peticion "POST" "/api/solicitudes/$idSolicitud1/aceptar" `
    $cuidador.sesion $cuidador.headers

Verificar "Primera aceptacion" $r.codigo 200
Verificar "Estado ACEPTADA" $r.datos.solicitud.estado "ACEPTADA"

# Ya no queda capacidad para aceptar a Michi.
$r = Peticion "POST" "/api/solicitudes/$idSolicitud2/aceptar" `
    $cuidador.sesion $cuidador.headers

Verificar "Sobrecupo rechazado" $r.codigo 409

# Ana no puede leer la solicitud privada de Beto.
$r = Peticion "GET" "/api/solicitudes/$idSolicitud2" `
    $dueno1.sesion $dueno1.headers

Verificar "Solicitud ajena protegida" $r.codigo 404

# Una mascota no puede enviarse dos veces.
$duplicada = Datos-Solicitud @($idsAna[0], $idsAna[0])

$r = Peticion "POST" "/api/solicitudes" `
    $dueno1.sesion $dueno1.headers $duplicada

Verificar "Mascota duplicada rechazada" $r.codigo 400

# Beto no puede solicitar una mascota de Ana.
$r = Peticion "POST" "/api/solicitudes" `
    $dueno2.sesion $dueno2.headers (Datos-Solicitud @($idsAna[0]))

Verificar "Mascota ajena rechazada" $r.codigo 403

# El dueño puede cancelar una reserva futura.
$r = Peticion "POST" "/api/solicitudes/$idSolicitud1/cancelar" `
    $dueno1.sesion $dueno1.headers

Verificar "Cancelacion" $r.codigo 200

# Liberadas las dos plazas, Carlos puede aceptar a Michi.
$r = Peticion "POST" "/api/solicitudes/$idSolicitud2/aceptar" `
    $cuidador.sesion $cuidador.headers

Verificar "Aceptacion despues de liberar cupo" $r.codigo 200

# No se permite aceptar nuevamente.
$r = Peticion "POST" "/api/solicitudes/$idSolicitud2/aceptar" `
    $cuidador.sesion $cuidador.headers

Verificar "Transicion repetida rechazada" $r.codigo 409

# No se puede finalizar una estadia futura.
$r = Peticion "POST" "/api/solicitudes/$idSolicitud2/finalizar" `
    $cuidador.sesion $cuidador.headers

Verificar "Finalizacion anticipada rechazada" $r.codigo 409

# Consultar el historial de la segunda solicitud.
$r = Peticion "GET" "/api/solicitudes/$idSolicitud2" `
    $dueno2.sesion $dueno2.headers

Verificar "Consulta de solicitud" $r.codigo 200
Verificar "Historial de dos estados" `
    @($r.datos.solicitud.historial).Count 2

# CSRF: una peticion sin encabezado debe rechazarse.
$sinToken = New-Object Microsoft.PowerShell.Commands.WebRequestSession

$cookie = $dueno2.sesion.Cookies.GetCookies([uri]$base) |
    Where-Object { $_.Name -eq "session" } |
    Select-Object -First 1

$sinToken.Cookies.Add([uri]$base, $cookie)

$r = Peticion "POST" "/api/solicitudes/$idSolicitud2/cancelar" `
    $sinToken $null

Verificar "CSRF sin token" $r.codigo 400

Write-Host ""
if ($fallas -eq 0) {
    Write-Host "RESULTADO: TODAS LAS PRUEBAS PASARON" -ForegroundColor Green
}
else {
    Write-Host "RESULTADO: $fallas PRUEBAS FALLARON" -ForegroundColor Red
    exit 1
}

Write-Host "Solicitud 1: $idSolicitud1"
Write-Host "Solicitud 2: $idSolicitud2"
Write-Host "Cuidador: $idCuidador"
