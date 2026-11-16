"""Resumen público de plazas de alojamiento, sin datos de las reservas."""
from datetime import date


def tramos_cupo(disponibilidad, capacidad, reservas, hoy=None):
    inicio = max(disponibilidad.fecha_desde, hoy or date.today())
    fin = disponibilidad.fecha_hasta
    if inicio >= fin:
        return []
    eventos = {inicio: 0, fin: 0}
    for r in reservas:
        if r.modalidad != 'ALOJAMIENTO' or r.estado not in ('ACEPTADA', 'FINALIZADA'):
            continue
        desde, hasta = max(inicio, r.fecha_desde), min(fin, r.fecha_hasta)
        if desde < hasta:
            eventos[desde] = eventos.get(desde, 0) + r.total_mascotas
            eventos[hasta] = eventos.get(hasta, 0) - r.total_mascotas
    fechas = sorted(eventos)
    ocupadas = 0
    tramos = []
    for i, desde in enumerate(fechas[:-1]):
        ocupadas += eventos[desde]
        hasta = fechas[i + 1]
        libres = max(0, capacidad - ocupadas)
        if tramos and tramos[-1]['plazas_libres'] == libres:
            tramos[-1]['fecha_hasta'] = hasta.isoformat()
        else:
            tramos.append(dict(fecha_desde=desde.isoformat(), fecha_hasta=hasta.isoformat(), plazas_libres=libres))
    return tramos
