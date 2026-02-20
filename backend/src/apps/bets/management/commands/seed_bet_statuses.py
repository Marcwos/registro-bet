from django.core.management.base import BaseCommand

from ...application.use_cases.seed_bet_statuses import SeedBetStatuses
from ...infrastructure.repositories.django_bet_status_repository import DjangoBetStatusRepository


class Command(BaseCommand):
    help = "Carga los estados de apuesta por defecto (pendiente, ganada, perdida, nula)"

    def handle(self, *arg, **options):
        repository = DjangoBetStatusRepository()
        use_case = SeedBetStatuses(repository)
        created = use_case.execute()

        if created:
            for s in created:
                self.stdout.write(self.style.SUCCESS(f"Creado: {s.name} ({s.code})"))
        else:
            self.stdout.write(self.style.WARNING("Todos los estados existen"))

        self.stdout.write(self.style.SUCCESS("Seed de estados compledo"))
