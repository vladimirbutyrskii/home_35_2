from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from users.models import User
import logging

logger = logging.getLogger(__name__)


@shared_task
def deactivate_inactive_users():
    """
    Блокировка пользователей, не заходивших более месяца.
    Запускается автоматически по расписанию.
    """
    month_ago = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(
        is_active=True, last_login__lt=month_ago
    ).exclude(is_superuser=True)

    count = inactive_users.count()

    if count > 0:
        inactive_users.update(is_active=False)
        logger.info(f"Заблокировано {count} неактивных пользователей")
    else:
        logger.info("Нет пользователей для блокировки")

    return f"Заблокировано {count} неактивных пользователей"
