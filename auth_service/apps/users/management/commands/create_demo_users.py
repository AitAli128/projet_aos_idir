from django.core.management.base import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "Crée des comptes de démonstration (idempotent)."

    def handle(self, *args, **options):
        demos = [
            ("pro@demo.local", "demodemo123", User.Role.PRO),
            ("admin@demo.local", "adminadmin123", User.Role.ADMIN),
        ]
        for email, password, role in demos:
            if User.objects.filter(email=email).exists():
                continue
            User.objects.create_user(email=email, password=password, role=role)
            self.stdout.write(self.style.SUCCESS(f"Créé {email} ({role})"))
        self.stdout.write(self.style.SUCCESS("Comptes démo prêts (ignorés s’ils existent déjà)."))
