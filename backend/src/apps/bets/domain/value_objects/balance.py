from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class DailyBalance:
    """Resultado del balance de un dia especifico"""

    tarjet_date: date
    total_staked: Decimal
    total_won: Decimal
    total_lost: Decimal
    total_return: Decimal
    net_profit: Decimal
    bet_count: Decimal
    won_count: int
    lost_count: int
    void_count: int
    pending_count: int


@dataclass(frozen=True)
class TotalBalance:
    """Resultado del balance historico total"""

    total_staked: Decimal
    total_won: Decimal
    total_lost: Decimal
    total_return: Decimal
    net_profit: Decimal
    bet_count: int
    won_count: int
    lost_count: int
    void_count: int
    pending_count: int


@dataclass(frozen=True)
class BetHistorySummay:
    """Resumen de un rango de fechas con las apuestas incluidas"""

    start_date: date
    end_date: date
    total_staked: Decimal
    total_won: Decimal
    total_lost: Decimal
    total_return: Decimal
    net_profit: Decimal
    bet_count: int
    won_count: int
    lost_count: int
    void_count: int
    pending_count: int
