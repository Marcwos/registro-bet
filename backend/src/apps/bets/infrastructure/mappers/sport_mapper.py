from ...domain.entities.sport import Sport
from ..models.sport_model import SportModel


class SportMapper:
    @staticmethod
    def to_domain(model: SportModel) -> Sport:
        return Sport(
            id=model.id,
            name=model.name,
            is_active=model.is_active,
        )

    @staticmethod
    def to_model(entity: Sport) -> SportModel:
        return SportModel(
            id=entity.id,
            name=entity.name,
            is_active=entity.is_active,
        )
