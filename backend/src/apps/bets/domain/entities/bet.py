from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ..value_objects.money import Money
from ..value_objects.odds import Odds


@dataclass
class Bet:
    id: UUID
    user_id: UUID
    title: str
    stake_amount: Money
    odds: Odds
    profit_expected: Decimal
    profit_final: Decimal | None
    status_id: UUID
    sport_id: UUID | None
    category_id: UUID | None
    description: str
    is_freebet: bool
    is_boosted: bool
    placed_at: datetime
    settled_at: datetime | None
    created_at: datetime
    updated_at: datetime
