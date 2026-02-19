from ...domain.entities.email_verification import EmailVerification
from ..models.email_verification_model import EmailVerificationModel


class EmailVerificationMapper:
    @staticmethod
    def to_main(model: EmailVerificationModel) -> EmailVerification:
        return EmailVerification(
            id=model.id,
            user_id=model.user_id,
            code_hash=model.code_hash,
            purpose=model.purpose,
            expires_at=model.expires_at,
            created_at=model.created_at,
            used_at=model.used_at,
            attempts=model.attempts,
        )

    @staticmethod
    def to_model(entity: EmailVerification) -> EmailVerificationModel:
        return EmailVerificationModel(
            id=entity.id,
            user_id=entity.user_id,
            code_hash=entity.code_hash,
            purpose=entity.purpose,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
            used_at=entity.used_at,
            attempts=entity.attempts,
        )
