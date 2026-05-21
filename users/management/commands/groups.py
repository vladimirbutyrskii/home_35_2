from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = "Создание группы модераторов и назначение прав"

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderator_group, created = Group.objects.get_or_create(name="moderators")

        if created:
            self.stdout.write(self.style.SUCCESS("Группа модераторов создана"))
        else:
            self.stdout.write(self.style.WARNING("Группа модераторов уже существует"))

        # Получаем права на просмотр и изменение курсов и уроков
        course_ct = ContentType.objects.get_for_model(Course)
        lesson_ct = ContentType.objects.get_for_model(Lesson)

        # Права для курсов
        view_course = Permission.objects.get(
            codename="view_course", content_type=course_ct
        )
        change_course = Permission.objects.get(
            codename="change_course", content_type=course_ct
        )

        # Права для уроков
        view_lesson = Permission.objects.get(
            codename="view_lesson", content_type=lesson_ct
        )
        change_lesson = Permission.objects.get(
            codename="change_lesson", content_type=lesson_ct
        )

        # Назначаем права группе
        moderator_group.permissions.set(
            [view_course, change_course, view_lesson, change_lesson]
        )

        self.stdout.write(self.style.SUCCESS("Права для модераторов успешно назначены"))
