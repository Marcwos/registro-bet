from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

from src.apps.bets.application.use_cases.delete_bet import DeleteBet
from src.apps.bets.domain.entities.bet import Bet
from src.apps.bets.domain.repositories.bet_repository import BetRepository
from src.apps.bets.domain.value_objects.money import Money
from src.apps.bets.domain.value_objects.odds import Odds
from src.apps.users.application.uses_cases.change_password import ChangePassword
from src.apps.users.application.uses_cases.login_user import LoginUser
from src.apps.users.application.uses_cases.register_user import RegisterUser
from src.apps.users.domain.entities.user import User
from src.apps.users.domain.repositories.auth_session_repository import AuthSessionRepository
from src.apps.users.domain.repositories.user_repository import UserRepository
from src.apps.users.domain.services.password_hasher import PasswordHasher
from src.apps.users.domain.services.token_provider import TokenProvider
from src.apps.users.domain.value_objects.email import Email
from src.apps.users.domain.value_objects.role import Role
from src.apps.users.domain.value_objects.user_id import UserId

from ...domain.services.audit_service import AuditService


class TestRegisterUserWithAudit:
    def setup_method(self):
        self.user_repo = Mock(spec=UserRepository)
        self.hasher = Mock(spec=PasswordHasher)
        self.audit_service = Mock(spec=AuditService)
        self.user_repo.get_by_email.return_value = None
        self.hasher.hash.return_value = "hashed_password"

    def test_register_logs_audit_event(self):
        use_case = RegisterUser(self.user_repo, self.hasher, audit_service=self.audit_service)
        use_case.execute(email="test@test.com", password="12345678")

        self.audit_service.log.assert_called_once()
        call_kwargs = self.audit_service.log.call_args
        assert call_kwargs.kwargs["action"] == "user_registered"
        assert call_kwargs.kwargs["entity_type"] == "user"
        assert call_kwargs.kwargs["metadata"] == {"email": "test@test.com"}

    def test_register_works_without_audit(self):
        use_case = RegisterUser(self.user_repo, self.hasher)
        user = use_case.execute(email="test@test.com", password="12345678")

        assert user.email.value == "test@test.com"


class TestLoginUserWithAudit:
    def setup_method(self):
        self.user_repo = Mock(spec=UserRepository)
        self.session_repo = Mock(spec=AuthSessionRepository)
        self.hasher = Mock(spec=PasswordHasher)
        self.token_provider = Mock(spec=TokenProvider)
        self.audit_service = Mock(spec=AuditService)

        self.user = User(
            id=UserId(uuid4()),
            email=Email("test@test.com"),
            password_hash="hashed",
            role=Role.USER,
            is_email_verified=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.user_repo.get_by_email.return_value = self.user
        self.hasher.verify.return_value = True
        self.token_provider.generate_refresh_token.return_value = "refresh_token"
        self.token_provider.generate_access_token.return_value = "access_token"

    def test_login_logs_audit_event(self):
        use_case = LoginUser(
            self.user_repo,
            self.session_repo,
            self.hasher,
            self.token_provider,
            audit_service=self.audit_service,
        )
        use_case.execute(email="test@test.com", password="12345678", ip_address="10.0.0.1")

        self.audit_service.log.assert_called_once()
        call_kwargs = self.audit_service.log.call_args
        assert call_kwargs.kwargs["action"] == "user_logged_in"
        assert call_kwargs.kwargs["ip_address"] == "10.0.0.1"

    def test_login_works_without_audit(self):
        use_case = LoginUser(self.user_repo, self.session_repo, self.hasher, self.token_provider)
        result = use_case.execute(email="test@test.com", password="12345678")

        assert result.access_token == "access_token"


class TestChangePasswordWithAudit:
    def setup_method(self):
        self.user_repo = Mock(spec=UserRepository)
        self.session_repo = Mock(spec=AuthSessionRepository)
        self.hasher = Mock(spec=PasswordHasher)
        self.audit_service = Mock(spec=AuditService)

        self.user = User(
            id=UserId(uuid4()),
            email=Email("test@test.com"),
            password_hash="hashed",
            role=Role.USER,
            is_email_verified=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.user_repo.get_by_id.return_value = self.user
        self.hasher.verify.return_value = True
        self.hasher.hash.return_value = "new_hashed"

    def test_change_password_logs_audit_event(self):
        use_case = ChangePassword(
            self.user_repo,
            self.session_repo,
            self.hasher,
            audit_service=self.audit_service,
        )
        use_case.execute(
            user_id=str(self.user.id.value),
            current_password="oldpass",
            new_password="newpass123",
        )

        self.audit_service.log.assert_called_once()
        call_kwargs = self.audit_service.log.call_args
        assert call_kwargs.kwargs["action"] == "password_changed"
        assert call_kwargs.kwargs["entity_type"] == "user"

    def test_change_password_works_without_audit(self):
        use_case = ChangePassword(self.user_repo, self.session_repo, self.hasher)
        use_case.execute(
            user_id=str(self.user.id.value),
            current_password="oldpass",
            new_password="newpass123",
        )
        self.session_repo.revoke_all_by_user.assert_called_once()


class TestDeleteBetWithAudit:
    def setup_method(self):
        self.bet_repo = Mock(spec=BetRepository)
        self.audit_service = Mock(spec=AuditService)

        self.bet_id = uuid4()
        self.user_id = uuid4()
        self.bet = Bet(
            id=self.bet_id,
            user_id=self.user_id,
            title="Apuesta 1",
            stake_amount=Money(Decimal("10.00")),
            odds=Odds(Decimal("2.50")),
            profit_expected=Decimal("15.00"),
            profit_final=None,
            status_id=uuid4(),
            sport_id=None,
            category_id=None,
            description="",
            is_freebet=False,
            is_boosted=False,
            placed_at=datetime.now(UTC),
            settled_at=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.bet_repo.get_by_id.return_value = self.bet

    def test_delete_bet_logs_audit_event(self):
        use_case = DeleteBet(self.bet_repo, audit_service=self.audit_service)
        use_case.execute(bet_id=self.bet_id, user_id=self.user_id)

        self.audit_service.log.assert_called_once()
        call_kwargs = self.audit_service.log.call_args
        assert call_kwargs.kwargs["action"] == "bet_deleted"
        assert call_kwargs.kwargs["entity_type"] == "bet"
        assert call_kwargs.kwargs["entity_id"] == self.bet_id
        assert call_kwargs.kwargs["metadata"]["bet_title"] == "Apuesta 1"

    def test_delete_bet_works_without_audit(self):
        use_case = DeleteBet(self.bet_repo)
        use_case.execute(bet_id=self.bet_id, user_id=self.user_id)

        self.bet_repo.delete.assert_called_once_with(self.bet_id)
