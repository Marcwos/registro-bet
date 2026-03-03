from decimal import Decimal
from uuid import UUID

from ...domain.entities.bet import Bet
from ...domain.entities.bet_status import BetStatus


class BalanceCalculator:
    """Servicio de dominio: calcula balances desde datos reales

    Para apuestas ganadas, usa el valor real registrado:
      profit_final > profit_expected > stake * odds (fallback teórico)
    profit_real por apuesta:
      - ganada: retorno_real - stake
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
        total_return = Decimal("0.00")
        won_count = 0
        lost_count = 0
        void_count = 0
        pending_count = 0

        for bet in bets:
            status = self.status_map.get(bet.status_id)
            if status is None:
                continue

            code = status.code
            is_freebet = getattr(bet, "is_freebet", False)

            # Freebet no cuenta como dinero apostado real
            if not is_freebet:
                total_staked += bet.stake_amount.amount

            if code == "won":
                won_count += 1
                # Retorno real: profit_final > profit_expected > cálculo teórico
                if bet.profit_final is not None:
                    return_amount = bet.profit_final
                elif bet.profit_expected is not None:
                    return_amount = bet.profit_expected
                else:
                    return_amount = (bet.stake_amount.amount * bet.odds.value).quantize(Decimal("0.01"))
                total_return += return_amount

                if is_freebet:
                    # Freebet ganada: la casa devuelve profit_final pero NO el stake
                    # (el bono no era dinero real), ganancia = return - stake
                    total_won += (return_amount - bet.stake_amount.amount).quantize(Decimal("0.01"))
                else:
                    total_won += (return_amount - bet.stake_amount.amount).quantize(Decimal("0.01"))
            elif code == "lost":
                lost_count += 1
                if is_freebet:
                    # Freebet perdida: no se resta stake (no era dinero real)
                    pass
                else:
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
            "total_return": total_return,
            "net_profit": net_profit,
            "bet_count": len(bets),
            "won_count": won_count,
            "lost_count": lost_count,
            "void_count": void_count,
            "pending_count": pending_count,
        }
