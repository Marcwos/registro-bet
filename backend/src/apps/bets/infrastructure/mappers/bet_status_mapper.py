from ...domain.entities.bet_status import BetStatus
from ..models.bet_status_model import BetStatusModel


class BetStatusMapper:
    @staticmethod
    def to_main(model: BetStatusModel) -> BetStatus:
        return BetStatus(
            id=model.id,
            name=model.name,
            code=model.code,
            is_final=model.is_final,
        )

    @staticmethod
    def to_model(entity: BetStatus) -> BetStatusModel:
        return BetStatusModel(
            id=entity.id,
            name=entity.name,
            code=entity.code,
            is_final=entity.is_final,
        )
