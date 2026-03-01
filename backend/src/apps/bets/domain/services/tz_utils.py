"""Utilidades para conversion de fechas locales a rangos UTC."""

from datetime import UTC, date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Offsets validos van de UTC-12 a UTC+14
_MIN_OFFSET = -720
_MAX_OFFSET = 840


def get_day_utc_range(
    target_date: date,
    *,
    tz_name: str | None = None,
    tz_offset_minutes: int = 0,
) -> tuple[datetime, datetime]:
    """Retorna (start_utc, end_utc) que representan el dia completo
    de ``target_date`` en la zona horaria indicada.

    Prioriza ``tz_name`` (IANA, ej. 'America/Guayaquil') sobre
    ``tz_offset_minutes``.  Si ninguno se provee, usa UTC.

    El rango es [start, end) — inicio inclusivo, fin exclusivo.
    """
    if tz_name:
        try:
            tz = ZoneInfo(tz_name)
        except (ZoneInfoNotFoundError, KeyError) as err:
            raise ValueError(f"Zona horaria invalida: {tz_name}") from err
    elif tz_offset_minutes != 0:
        if not (_MIN_OFFSET <= tz_offset_minutes <= _MAX_OFFSET):
            raise ValueError(f"tz_offset fuera de rango: {tz_offset_minutes}")
        # JS getTimezoneOffset() → positivo = detras de UTC
        tz = timezone(timedelta(minutes=-tz_offset_minutes))
    else:
        tz = UTC

    local_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=tz)
    local_end = local_start + timedelta(days=1)

    return local_start.astimezone(UTC), local_end.astimezone(UTC)


def parse_tz_params(query_params: dict) -> dict:
    """Extrae y valida los parametros de timezone de un request.

    Retorna dict con ``tz_name`` y ``tz_offset_minutes`` listos
    para pasar a ``get_day_utc_range``.
    """
    tz_name = query_params.get("tz")
    tz_offset_minutes = 0

    if tz_name:
        # Validar que existe
        try:
            ZoneInfo(tz_name)
        except (ZoneInfoNotFoundError, KeyError) as err:
            raise ValueError(f"Zona horaria invalida: {tz_name}") from err
    else:
        raw = query_params.get("tz_offset", "0")
        try:
            tz_offset_minutes = int(raw)
        except (ValueError, TypeError):
            tz_offset_minutes = 0

        if not (_MIN_OFFSET <= tz_offset_minutes <= _MAX_OFFSET):
            raise ValueError(f"tz_offset fuera de rango: {tz_offset_minutes}")

    return {"tz_name": tz_name, "tz_offset_minutes": tz_offset_minutes}
