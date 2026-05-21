from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="SkyPro",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        user.set_password("admin123")
        user.save()
        self.stdout.write(self.style.SUCCESS("Суперпользователь создан"))
