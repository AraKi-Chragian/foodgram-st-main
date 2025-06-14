import json
import logging
import os

from django.conf import settings
from django.core.files import File
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


def load_json(filename):
    file_path = os.path.join(settings.BASE_DIR, "data", filename)
    if not os.path.isfile(file_path):
        logger.error(f"Файл {filename} не найден по пути {file_path}")
        return []
    with open(file_path, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    return data


@receiver(post_migrate)
def load_test_users(sender, **kwargs):
    users_list = load_json("users.json")
    if not users_list:
        return

    emails_list = [user["email"] for user in users_list]
    existing = {user.email: user for user in User.objects.filter(email__in=emails_list)}

    for user_info in users_list:
        email = user_info["email"]
        if email in existing:
            logger.info(f"Пользователь {email} уже существует")
            continue

        new_user = User(
            email=email,
            username=user_info["username"],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
        )
        new_user.set_password(user_info["password"])

        avatar_file_path = os.path.join(settings.MEDIA_ROOT, user_info["avatar"])
        if os.path.isfile(avatar_file_path):
            with open(avatar_file_path, "rb") as avatar_file:
                new_user.avatar.save(
                    os.path.basename(avatar_file_path), File(avatar_file), save=False
                )

        new_user.save()
        logger.info(f"Создан пользователь: {email} с аватаркой")
