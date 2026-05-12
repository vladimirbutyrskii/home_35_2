from django.core.management import BaseCommand
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class Command(BaseCommand):
    help = "Создание всех периодических задач для проекта"

    def handle(self, *args, **options):
        # Создаем интервал для блокировки пользователей (каждые 24 часа)
        deactivate_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=24,
            period=IntervalSchedule.HOURS,
        )

        # Создаем интервал для отладки (каждые 60 секунд) - опционально
        debug_schedule, _ = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.SECONDS,
        )

        # Блокировка неактивных пользователей
        PeriodicTask.objects.update_or_create(
            name="Deactivate inactive users",
            defaults={
                "task": "users.tasks.deactivate_inactive_users",
                "interval": deactivate_schedule,
                "crontab": None,
                "enabled": True,
            },
        )

        # Отладочная задача
        PeriodicTask.objects.update_or_create(
            name="Debug periodic task",
            defaults={
                "task": "lms.tasks.debug_periodic_task",
                "interval": debug_schedule,
                "crontab": None,
                "enabled": True,
            },
        )

        self.stdout.write(
            self.style.SUCCESS("Все периодические задачи созданы/обновлены")
        )
