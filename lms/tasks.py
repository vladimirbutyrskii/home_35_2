from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from lms.models import Course, Subscription

from django.utils import timezone
from datetime import timedelta


@shared_task
def send_course_update_notification(course_id):
    """Отправка уведомлений подписчикам об обновлении курса"""
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course)

        if not subscriptions.exists():
            return f'Нет подписчиков для курса "{course.name}"'

        # Сбор уникальных email подписчиков
        recipient_list = list(subscriptions.values_list("user__email", flat=True))

        # Отправка письма
        send_mail(
            subject=f"Обновление курса: {course.name}",
            message=f'Курс "{course.name}" был обновлен. Зайдите на платформу для просмотра новых материалов.'
                    f'\n\nСсылка: http://localhost:8000/courses/{course.id}/',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return f'Уведомления отправлены {subscriptions.count()} подписчикам курса "{course.name}"'

    except Course.DoesNotExist:
        return f"Курс с id={course_id} не найден"


@shared_task
def send_course_update_notification_with_throttle(course_id):
    """
    Отправка уведомлений с проверкой - не чаще 1 раза в 4 часа
    """
    course = Course.objects.get(id=course_id)

    # Проверка, когда в последний раз отправляли уведомление
    if course.last_notification_sent:
        time_since_last = timezone.now() - course.last_notification_sent
        if time_since_last < timedelta(hours=4):
            return f'Уведомление для курса "{course.name}" не отправлено (прошло менее 4 часов с предыдущего)'

    # Отправка уведомлений
    subscriptions = Subscription.objects.filter(course=course)

    if subscriptions.exists():
        recipient_list = list(subscriptions.values_list("user__email", flat=True))
        send_mail(
            subject=f"Обновление курса: {course.name}",
            message=f'Курс "{course.name}" был обновлен. Зайдите на платформу для просмотра новых материалов.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        # Обновляем время последнего уведомления
        course.last_notification_sent = timezone.now()
        course.save(update_fields=["last_notification_sent"])

        return f'Уведомления отправлены {subscriptions.count()} подписчикам курса "{course.name}"'

    return f'Нет подписчиков для курса "{course.name}"'


@shared_task
def check_inactive_users():
    """Проверка неактивных пользователей (пример периодической задачи)"""
    from users.models import User
    from datetime import timedelta
    from django.utils import timezone

    threshold_date = timezone.now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=threshold_date, is_active=True)

    # Логика для неактивных пользователей
    return f"Найдено {inactive_users.count()} неактивных пользователей"


@shared_task
def debug_task():
    """Отладочная задача"""
    print("Периодическая задача выполнена")
    return "OK"


@shared_task
def debug_periodic_task():
    """Отладочная периодическая задача"""
    print("Периодическая задача выполнена через celery-beat")
    return "OK"
