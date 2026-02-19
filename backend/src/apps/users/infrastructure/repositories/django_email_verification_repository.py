from datetime import UTC, datetime
from uuid import UUID

from django.db.models import F

from ...domain.entities.email_verification import EmailVerification
from ...domain.repositories.email_verification_repository import EmailVerficationRepository
from ..mappers.email_verification_mapper import EmailVerificationMapper
from ..models.email_verification_model import EmailVerificationModel


class DjangoEmailVerificationRepository(EmailVerficationRepository):
    def save(self, verfication: EmailVerification) -> None:
        model = EmailVerificationMapper.to_model(verfication)
        model.save()

    def get_latest_by_user(self, user_id: UUID) -> EmailVerification:
        try:
            model = EmailVerificationModel.objects.filter(user_id=user_id).latest("created_at")
            return EmailVerificationMapper.to_main(model)
        except EmailVerificationModel.DoesNotExist:
            return None

    def mark_as_used(self, verfication_id: UUID) -> None:
        EmailVerificationModel.objects.filter(id=verfication_id).update(used_at=datetime.now(UTC))

    def increment_attempts(self, verfication_id: UUID) -> None:
        EmailVerificationModel.objects.filter(id=verfication_id).update(attempts=F("attempts") + 1)
