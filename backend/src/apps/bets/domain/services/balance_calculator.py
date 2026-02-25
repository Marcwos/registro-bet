from decimal import Decimal
from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.entities.bet_status import BetStatus


class BalanceCalculator:
    """Servicio de dominio: calcula balances desde datos reales

    profit_real por apuesta:
      - ganada: stake * (odds - 1)
      - perdida: -stake
      - nula/pendiente: 0
    """

    def __init__(self, status_map: dict[UUID, BetStatus]):
        """status_map: diccionario {status_id: BetStatus} para poder consultar el code de cada estado sin ir a BD"""
        self.status_map = status_map

    def calculate(self, bets: list[Bet]) -> dict:
        """Calcula metricas de un conjunto de apuestas

        Retorna dict con: total_staked, total_won, total_lost, net_profit, bet_count, won_count, lost_count, void_count, pending_count
        """
        total_staked = Decimal("0.00")
        total_won = Decimal("0.00")
        total_lost = Decimal("0.00")
        won_count = 0
        lost_count = 0
        void_count = 0
        pending_count = 0

        for bet in bets:
            status = self.status_map.get(bet.status_id)
            if status is None:
                continue

            code = status.code

            # Siempre sumamos lo apostado
            total_staked += bet.stake_amount.amount

            if code == "won":
                won_count += 1
                # ganada -> profit_real = stake * (odds - 1)
                profit_real = (bet.stake_amount.amount * (bet.odds.value - Decimal("1"))).quantize(Decimal("0.01"))
                total_won += profit_real
            elif code == "lost":
                lost_count += 1
                # perdida -> profit_real = -stake
                total_lost += bet.stake_amount.amount
            elif code == "void":
                void_count += 1
                # nula -> 0
            else:
                # pendiente
                pending_count += 1
        net_profit = total_won - total_lost

        return {
            "total_staked": total_staked,
            "total_won": total_won,
            "total_lost": total_lost,
            "net_profit": net_profit,
            "bet_count": len(bets),
            "won_count": won_count,
            "lost_count": lost_count,
            "void_count": void_count,
            "pending_count": pending_count,
        }
